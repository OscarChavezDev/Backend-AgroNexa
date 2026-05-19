from app.database.mongo import get_db
from app.utils.helpers import now_utc
from bson import ObjectId


def create(muestra_doc):
    result = get_db().muestras.insert_one(muestra_doc)
    return str(result.inserted_id)


def find_all_by_user(user_id):
    return list(get_db().muestras.find(
        {"userId": ObjectId(user_id), "estado": {"$ne": "eliminado"}},
        sort=[("createdAt", -1)],
    ))


def find_all_by_parcela(parcela_id, user_id):
    return list(get_db().muestras.find(
        {
            "parcelaId": ObjectId(parcela_id),
            "userId": ObjectId(user_id),
            "estado": {"$ne": "eliminado"},
        },
        sort=[("createdAt", -1)],
    ))


def find_by_id(muestra_id):
    return get_db().muestras.find_one({"_id": ObjectId(muestra_id)})


def find_by_id_and_user(muestra_id, user_id):
    return get_db().muestras.find_one({
        "_id": ObjectId(muestra_id),
        "userId": ObjectId(user_id),
    })


def update(muestra_id, user_id, fields):
    fields["updatedAt"] = now_utc()
    result = get_db().muestras.update_one(
        {"_id": ObjectId(muestra_id), "userId": ObjectId(user_id)},
        {"$set": fields},
    )
    return result.matched_count > 0


def soft_delete(muestra_id, user_id):
    result = get_db().muestras.update_one(
        {"_id": ObjectId(muestra_id), "userId": ObjectId(user_id)},
        {"$set": {"estado": "eliminado", "updatedAt": now_utc()}},
    )
    return result.matched_count > 0


