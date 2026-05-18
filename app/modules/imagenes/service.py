import cloudinary.uploader
from bson import ObjectId
from app.modules.muestras.repository import (
    find_by_id_and_user, push_imagen, pull_imagen,
)
from app.utils.validators import required_fields


def subir_imagen(user_id, file, data):
    missing = required_fields(data, ["muestraId"])
    if missing:
        return None, "muestraId es requerido"

    if not file:
        return None, "No se recibió ningún archivo"

    muestra = find_by_id_and_user(data["muestraId"], user_id)
    if not muestra:
        return None, "Muestra no encontrada"

    upload_result = cloudinary.uploader.upload(
        file,
        folder=f"agronexa/muestras/{data['muestraId']}",
    )

    imagen_doc = {
        "_id": ObjectId(),
        "url": upload_result["secure_url"],
        "publicId": upload_result["public_id"],
        "tipo": data.get("tipo", "general"),
        "descripcion": data.get("descripcion", ""),
    }

    push_imagen(data["muestraId"], imagen_doc)

    return {
        "id": str(imagen_doc["_id"]),
        "url": imagen_doc["url"],
    }, None


def listar_imagenes(muestra_id, user_id):
    muestra = find_by_id_and_user(muestra_id, user_id)
    if not muestra:
        return None, "Muestra no encontrada"

    imagenes = muestra.get("imagenes") or []
    result = []
    for img in imagenes:
        result.append({
            "id": str(img.get("_id", "")),
            "url": img.get("url"),
            "tipo": img.get("tipo"),
            "descripcion": img.get("descripcion"),
        })
    return result, None


def eliminar_imagen(user_id, imagen_id, muestra_id):
    if not muestra_id:
        return None, "muestraId es requerido"

    muestra = find_by_id_and_user(muestra_id, user_id)
    if not muestra:
        return None, "Muestra no encontrada"

    imagen = next(
        (img for img in (muestra.get("imagenes") or [])
         if str(img.get("_id")) == imagen_id),
        None,
    )
    if not imagen:
        return None, "Imagen no encontrada"

    try:
        cloudinary.uploader.destroy(imagen["publicId"])
    except Exception:
        pass

    pull_imagen(muestra_id, str(imagen["_id"]))
    return {"id": imagen_id}, None
