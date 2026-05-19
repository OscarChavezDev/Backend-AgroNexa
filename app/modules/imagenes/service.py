import cloudinary.uploader
from bson import ObjectId
from app.modules.muestras.repository import find_by_id_and_user
from app.modules.imagenes import repository as repo
from app.utils.helpers import now_utc, serialize_doc

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
