from app.database.mongo import get_db
from app.utils.helpers import now_utc
from bson import ObjectId


def crear(doc):
    doc["createdAt"] = now_utc()
    doc.setdefault("leido", False)
    result = get_db().mensajes.insert_one(doc)
    return str(result.inserted_id)


def listar_todos():
    return list(get_db().mensajes.find({}).sort("createdAt", -1))


def conteo_no_leidos():
    return get_db().mensajes.count_documents({"leido": False})


def marcar_leido(mensaje_id):
    get_db().mensajes.update_one(
        {"_id": ObjectId(mensaje_id)},
        {"$set": {"leido": True}}
    )


def marcar_todos_leidos():
    get_db().mensajes.update_many({}, {"$set": {"leido": True}})
