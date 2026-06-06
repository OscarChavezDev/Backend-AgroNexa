from app.database.mongo import get_db
from app.utils.helpers import now_utc
from bson import ObjectId


def get_all_planes():
    return list(get_db().planes.find({"estado": "activo"}))


def get_plan_by_codigo(codigo):
    return get_db().planes.find_one({"codigo": codigo, "estado": "activo"})


def seed_planes(planes_data):
    db = get_db()
    for plan in planes_data:
        db.planes.update_one(
            {"codigo": plan["codigo"]},
            {"$set": plan},
            upsert=True,
        )


def create_suscripcion(doc):
    result = get_db().suscripciones.insert_one(doc)
    return str(result.inserted_id)


def find_active_by_user(user_id):
    return get_db().suscripciones.find_one({
        "userId": ObjectId(user_id),
        "estado": "activo",
    })


def deactivate_all_by_user(user_id):
    get_db().suscripciones.update_many(
        {"userId": ObjectId(user_id), "estado": "activo"},
        {"$set": {"estado": "inactivo"}},
    )
