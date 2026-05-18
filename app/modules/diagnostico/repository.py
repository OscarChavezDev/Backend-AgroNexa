from app.database.mongo import get_db
from bson import ObjectId


def create(diagnostico_doc):
    result = get_db().diagnosticos.insert_one(diagnostico_doc)
    return str(result.inserted_id)


def find_by_id(diagnostico_id):
    return get_db().diagnosticos.find_one({"_id": ObjectId(diagnostico_id)})


def find_by_muestra(muestra_id):
    return get_db().diagnosticos.find_one({"muestraId": ObjectId(muestra_id)})


def find_all_by_user(user_id):
    return list(get_db().diagnosticos.find(
        {"userId": ObjectId(user_id)},
        sort=[("createdAt", -1)],
    ))
