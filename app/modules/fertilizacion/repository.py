from app.database.mongo import get_db
from bson import ObjectId


def create(plan_doc):
    result = get_db().fertilizacion.insert_one(plan_doc)
    return str(result.inserted_id)


def find_by_id(plan_id):
    return get_db().fertilizacion.find_one({"_id": ObjectId(plan_id)})


def find_ultimo_por_parcela(parcela_id, user_id):
    return get_db().fertilizacion.find_one(
        {"parcelaId": ObjectId(parcela_id), "userId": ObjectId(user_id)},
        sort=[("createdAt", -1)],
    )


def find_all_by_parcela(parcela_id, user_id):
    return list(get_db().fertilizacion.find(
        {"parcelaId": ObjectId(parcela_id), "userId": ObjectId(user_id)},
        sort=[("createdAt", -1)],
    ))


def find_all_by_user(user_id):
    return list(get_db().fertilizacion.find(
        {"userId": ObjectId(user_id)},
        sort=[("createdAt", -1)],
    ))
