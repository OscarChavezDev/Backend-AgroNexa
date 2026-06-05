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


PROMPT_VALIDACION = """Eres un sistema de validación ESTRICTO para un software de diagnóstico fitosanitario EXCLUSIVO de cacao (Theobroma cacao).

Tu única tarea: determinar si la imagen muestra una parte de una planta de CACAO apta para diagnóstico.

RESPONDE SOLO con JSON válido, sin texto extra ni markdown:
{
  "relevante": true,
  "motivo": "descripción concisa: qué parte de la planta se ve y si corresponde a cacao"
}

VÁLIDA (relevante: true) — SOLO si la imagen muestra CLARAMENTE una de estas partes Y pertenece a una planta de CACAO:
- Fruto/mazorca de cacao (vaina alargada, ovalada, con surcos; colores verde, amarillo, naranja, rojo o morado)
- Hoja de cacao (grande, ovalada-alargada, nervadura marcada; brotes rojizos cuando son jóvenes)
- Tallo o rama de cacao (corteza, posibles cojines florales)
- Raíz de cacao
- Flor de cacao (pequeñas, blancas/rosadas, sobre el tronco o ramas — cauliflora)
- Planta completa / árbol de cacao

NO VÁLIDA (relevante: false) — rechaza SIEMPRE si:
- La parte vegetal NO es de cacao (otro cultivo: café, plátano, maíz, palta, mango, cítricos, etc.). Indica en el motivo qué planta parece ser.
- No se distingue con seguridad que sea cacao
- Personas, animales, insectos sueltos, maquinaria, herramientas, objetos, edificios
- Capturas de pantalla, documentos, texto, dibujos
- Paisajes amplios sin una parte de cacao en primer plano
- Suelo, agua o cielo sin planta de cacao identificable
- Imágenes borrosas, oscuras o irreconocibles

REGLA CLAVE: si NO puedes confirmar que es cacao, responde relevante: false. Es preferible rechazar una imagen dudosa que aceptar un cultivo equivocado. El motivo debe ser breve y claro (ej: "Hoja de plátano, no es cacao" o "Mazorca de cacao en buen plano")."""


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
