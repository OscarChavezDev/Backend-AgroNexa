import os
import base64
import logging

import cloudinary.uploader
from bson import ObjectId
from app.modules.muestras.repository import find_by_id_and_user
from app.modules.imagenes import repository as repo
from app.utils.helpers import now_utc, serialize_doc

logger = logging.getLogger(__name__)

TIPOS_IMAGEN = ("hoja", "fruto", "tallo", "planta_completa", "suelo")


def subir_imagen(user_id, file, data):
    if not data.get("muestraId"):
        return None, "muestraId es requerido"

    if not file:
        return None, "No se recibió ningún archivo"

    muestra = find_by_id_and_user(data["muestraId"], user_id)
    if not muestra:
        return None, "Muestra no encontrada"

    tipo = data.get("tipoImagen", "planta_completa")
    if tipo not in TIPOS_IMAGEN:
        tipo = "planta_completa"

    upload_result = cloudinary.uploader.upload(
        file,
        folder=f"agronexa/muestras/{data['muestraId']}",
    )

    imagen_doc = {
        "muestraId": ObjectId(data["muestraId"]),
        "userId": ObjectId(user_id),
        "url": upload_result["secure_url"],
        "publicId": upload_result["public_id"],
        "tipoImagen": tipo,
        "descripcion": data.get("descripcion", ""),
        "createdAt": now_utc(),
    }

    imagen_id = repo.create(imagen_doc)
    return {"id": imagen_id, "url": imagen_doc["url"]}, None


def listar_imagenes(muestra_id, user_id):
    muestra = find_by_id_and_user(muestra_id, user_id)
    if not muestra:
        return None, "Muestra no encontrada"

    imagenes = repo.find_by_muestra(muestra_id)
    return [
        {
            "id": str(img["_id"]),
            "url": img.get("url"),
            "tipoImagen": img.get("tipoImagen"),
            "descripcion": img.get("descripcion"),
        }
        for img in imagenes
    ], None


PROMPT_VALIDACION = """Eres un sistema de validación estricto para un software de diagnóstico fitosanitario de cultivos de cacao.

Analiza esta imagen y determina con criterio ESTRICTO si es apta para diagnóstico de enfermedades en plantas o cultivos.

RESPONDE SOLO con JSON válido, sin texto extra ni markdown:
{
  "relevante": true,
  "motivo": "descripción concisa de lo que muestra la imagen y por qué es o no es válida"
}

VÁLIDA (relevante: true) — SOLO si muestra claramente:
- Hojas, frutos, tallos, raíces o flores de plantas con o sin síntomas visibles
- Tejido vegetal en primer plano o plano medio
- Síntomas fitosanitarios: manchas, pudrición, deformaciones, plagas sobre la planta

NO VÁLIDA (relevante: false) — si muestra cualquiera de estos casos:
- Personas, retratos, selfies
- Maquinaria agrícola, tractores, herramientas (aunque estén en campo)
- Paisajes amplios de campo sin primer plano vegetal
- Capturas de pantalla, documentos, tablas, texto
- Animales, insectos sueltos sin planta visible
- Objetos, edificios, suelo sin planta
- Imágenes borrosas o irreconocibles
- Cualquier imagen que NO permita evaluar el estado fitosanitario de una planta

Ante la duda: responde relevante: false. Es mejor rechazar que aceptar algo incorrecto."""


def validar_imagen_agricola(imagen_bytes, mime_type):
    """
    Usa Groq para verificar si la imagen es relevante para diagnóstico agrícola.
    Si la IA no está disponible, retorna relevante=True para no bloquear al usuario.
    """
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        return {"relevante": True, "motivo": "Validación no disponible (sin clave de IA)"}, None

    try:
        from groq import Groq
        from app.modules.diagnostico.ai_service import _extraer_json

        img_b64 = base64.b64encode(imagen_bytes).decode("utf-8")
        model_name = os.getenv("GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")

        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": [
                {"type": "text", "text": PROMPT_VALIDACION},
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{img_b64}"}}
            ]}],
            temperature=0.1,
            max_tokens=150,
        )

        texto = response.choices[0].message.content.strip()
        resultado = _extraer_json(texto)
        if resultado is None:
            logger.warning("Validación IA: respuesta no JSON — %s", texto[:100])
            return {"relevante": True, "motivo": "No se pudo analizar"}, None

        return resultado, None

    except Exception as e:
        logger.warning("Validación IA falló (no bloqueante): %s", e)
        return {"relevante": True, "motivo": "Validación no disponible"}, None


def eliminar_imagen(user_id, imagen_id, muestra_id):
    if not muestra_id:
        return None, "muestraId es requerido"

    muestra = find_by_id_and_user(muestra_id, user_id)
    if not muestra:
        return None, "Muestra no encontrada"

    imagen = repo.find_by_id(imagen_id)
    if not imagen or str(imagen.get("muestraId")) != muestra_id:
        return None, "Imagen no encontrada"

    try:
        cloudinary.uploader.destroy(imagen["publicId"])
    except Exception:
        pass

    repo.delete(imagen_id)
    return {"id": imagen_id}, None
