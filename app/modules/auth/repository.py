from app.database.mongo import get_db


def find_by_email(correo):
    return get_db().users.find_one({"correo": correo})


def create_user(user_doc):
    result = get_db().users.insert_one(user_doc)
    return str(result.inserted_id)
