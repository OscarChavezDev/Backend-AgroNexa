from app.database.mongo import get_db
from app.utils.helpers import now_utc
from bson import ObjectId


def find_by_email(correo):
    return get_db().users.find_one({"correo": correo})


def create_user(user_doc):
    result = get_db().users.insert_one(user_doc)
    return str(result.inserted_id)


def increment_login(user_id):
    get_db().users.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$inc": {"loginCount": 1},
            "$set": {"lastLogin": now_utc(), "updatedAt": now_utc()},
        },
    )
