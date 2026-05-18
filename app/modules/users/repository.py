from app.database.mongo import get_db
from app.utils.helpers import now_utc
from bson import ObjectId


def find_by_id(user_id):
    return get_db().users.find_one({"_id": ObjectId(user_id)})


def find_all(filters=None):
    return list(get_db().users.find(filters or {}))


def update(user_id, fields):
    fields["updatedAt"] = now_utc()
    result = get_db().users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": fields},
    )
    return result.matched_count > 0


def update_status(user_id, estado):
    return update(user_id, {"estado": estado})


def update_plan(user_id, plan):
    return update(user_id, {"plan": plan})
