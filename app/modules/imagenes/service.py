import os
import base64
import logging

import cloudinary.uploader
from bson import ObjectId
from app.modules.muestras.repository import find_by_id_and_user
from app.modules.imagenes import repository as repo
from app.utils.helpers import now_utc, serialize_doc
from app.utils.groq_utils import GROQ_MODEL_DEFAULT, opciones_razonamiento, extraer_json

logger = logging.getLogger(__name__)

TIPOS_IMAGEN = ("hoja", "fruto", "tallo", "planta_completa", "suelo")

GROQ_VISION_MODEL_DEFAULT = GROQ_MODEL_DEFAULT


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


PROMPT_VALIDACION = """Eres un sistema de validación para un software de diagnóstico fitosanitario de cacao (Theobroma cacao).

Tu única tarea: determinar si la imagen muestra una parte de una planta de CACAO apta para diagnóstico. RECUERDA: el propósito del sistema es diagnosticar cacao ENFERMO, así que las imágenes con enfermedad, hongos, pudrición o deformación son EXACTAMENTE lo que se espera recibir, NO motivo de rechazo.

RESPONDE SOLO con JSON válido, sin texto extra ni markdown:
{
  "relevante": true,
  "motivo": "descripción concisa: qué parte de la planta se ve y si corresponde a cacao"
}

VÁLIDA (relevante: true) — si la imagen muestra una de estas partes de una planta de CACAO, SANA O ENFERMA:
- Fruto/mazorca de cacao (vaina alargada, ovalada, con surcos; colores verde, amarillo, naranja, rojo o morado), AUNQUE esté deformada, podrida, manchada o cubierta de hongo.
- Hoja de cacao (grande, ovalada-alargada, nervadura marcada; brotes rojizos cuando son jóvenes), aunque tenga manchas, necrosis o esté seca.
- Tallo o rama de cacao (corteza, posibles cojines florales), aunque presente lesiones o proliferación de brotes.
- Raíz de cacao.
- Flor de cacao (pequeñas, blancas/rosadas, sobre el tronco o ramas — cauliflora).
- Planta completa / árbol de cacao.

IMPORTANTE — NO confundas la ENFERMEDAD con "no es cacao":
- Una mazorca con Moniliasis se cubre de un POLVO o capa BLANCA-CREMA (esporulación del hongo) sobre manchas marrones. Sigue siendo una mazorca de cacao válida; NO es "un hongo creciendo en un tronco".
- La pudrición parda/negra (Phytophthora) ennegrece la mazorca: sigue siendo cacao válido.
- La escoba de bruja deforma frutos y brotes: sigue siendo cacao válido.
- Si reconoces la FORMA de una mazorca, hoja, rama o árbol de cacao (aunque esté muy afectada por hongo, pudrición o deformación), responde relevante: true e indica en el motivo que parece cacao enfermo.

NO VÁLIDA (relevante: false) — rechaza solo si:
- La parte vegetal es CLARAMENTE de otro cultivo (café, plátano, maíz, palta, mango, cítricos, etc.). Indica en el motivo qué planta parece ser.
- Personas, animales, insectos sueltos, maquinaria, herramientas, objetos, edificios.
- Capturas de pantalla, documentos, texto, dibujos.
- Paisajes amplios sin una parte de cacao en primer plano.
- Suelo, agua o cielo sin planta de cacao identificable.
- Un hongo/seta aislado SIN forma reconocible de fruto, hoja o rama de cacao alrededor.
- Imágenes tan borrosas u oscuras que no se distingue ninguna forma.

REGLA CLAVE: ante la duda entre "cacao enfermo" y "no es cacao", prioriza ACEPTAR (relevante: true) si hay cualquier forma reconocible de mazorca, hoja, rama o árbol de cacao. Es preferible aceptar una mazorca muy enferma que rechazarla por la enfermedad. El motivo debe ser breve y claro (ej: "Mazorca de cacao con moniliasis avanzada" o "Hoja de plátano, no es cacao")."""


def validar_imagen_agricola(imagen_bytes, mime_type):
    """
    Usa Groq para verificar si la imagen es relevante para diagnóstico agrícola.

    Si la IA no está disponible se deja pasar la imagen para no bloquear al
    usuario, pero se marca `validado: False`. Sin esa marca la interfaz mostraría
    "imagen aceptada" igual que si hubiera pasado el control, y el fallo quedaría
    invisible: exactamente lo que ocurrió cuando Groq dio de baja el modelo.
    """
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        return {
            "relevante": True,
            "validado": False,
            "motivo": "No se pudo verificar la imagen: falta la clave de IA (GROQ_API_KEY).",
        }, None

    try:
        from groq import Groq

        img_b64 = base64.b64encode(imagen_bytes).decode("utf-8")
        model_name = os.getenv("GROQ_VISION_MODEL", GROQ_VISION_MODEL_DEFAULT)

        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": [
                {"type": "text", "text": PROMPT_VALIDACION},
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{img_b64}"}}
            ]}],
            temperature=0.1,
            # Los modelos de razonamiento necesitan margen: el límite corta la
            # respuesta antes del JSON y la validación queda inservible.
            max_tokens=1200,
            **opciones_razonamiento(model_name),
        )

        texto = (response.choices[0].message.content or "").strip()
        resultado = extraer_json(texto)
        if resultado is None:
            logger.warning("Validación IA: respuesta no JSON — %s", texto[:100])
            return {
                "relevante": True,
                "validado": False,
                "motivo": "No se pudo verificar la imagen: la IA respondió en un formato inesperado.",
            }, None

        resultado["validado"] = True
        return resultado, None

    except Exception as e:
        # Se registra como error (no warning) porque deja el control desactivado.
        logger.error("Validación de imagen no disponible — modelo '%s': %s",
                     os.getenv("GROQ_VISION_MODEL", GROQ_VISION_MODEL_DEFAULT), e)
        return {
            "relevante": True,
            "validado": False,
            "motivo": "No se pudo verificar la imagen. Revisa que la imagen corresponda a cacao.",
        }, None


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
