from app.database.mongo import get_db
from app.utils.helpers import now_utc
from bson import ObjectId


def create(parcela_doc):
    result = get_db().parcelas.insert_one(parcela_doc)
    return str(result.inserted_id)


def find_all_by_user(user_id):
    return list(get_db().parcelas.find({"userId": ObjectId(user_id), "estado": "activo"}))


def find_by_id(parcela_id):
    return get_db().parcelas.find_one({"_id": ObjectId(parcela_id)})


def find_by_id_and_user(parcela_id, user_id):
    return get_db().parcelas.find_one({
        "_id": ObjectId(parcela_id),
        "userId": ObjectId(user_id),
    })


def update(parcela_id, user_id, fields):
    fields["updatedAt"] = now_utc()
    result = get_db().parcelas.update_one(
        {"_id": ObjectId(parcela_id), "userId": ObjectId(user_id)},
        {"$set": fields},
    )
    return result.matched_count > 0


def deactivate(parcela_id, user_id):
    result = get_db().parcelas.update_one(
        {"_id": ObjectId(parcela_id), "userId": ObjectId(user_id)},
        {"$set": {"estado": "inactivo", "updatedAt": now_utc()}},
    )
    return result.matched_count > 0
