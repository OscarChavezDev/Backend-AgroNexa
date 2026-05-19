from app.database.mongo import get_db
from bson import ObjectId


def create(imagen_doc):
    result = get_db().imagenes_muestra.insert_one(imagen_doc)
    return str(result.inserted_id)


def find_by_muestra(muestra_id):
    return list(get_db().imagenes_muestra.find(
        {"muestraId": ObjectId(muestra_id)},
        sort=[("createdAt", 1)],
    ))


def find_by_id(imagen_id):
    return get_db().imagenes_muestra.find_one({"_id": ObjectId(imagen_id)})


def delete(imagen_id):
    get_db().imagenes_muestra.delete_one({"_id": ObjectId(imagen_id)})
