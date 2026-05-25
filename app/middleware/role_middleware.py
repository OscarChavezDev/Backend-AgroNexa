from functools import wraps
from flask_jwt_extended import get_jwt_identity
from app.utils.response import error_response
from app.database.mongo import get_db
from app.modules.auth.models import normalize_role
from bson import ObjectId


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            db = get_db()
            user = db.users.find_one({"_id": ObjectId(user_id)})
            allowed_roles = tuple(normalize_role(role) for role in roles)
            if not user or normalize_role(user.get("rol")) not in allowed_roles:
                return error_response("Acceso no autorizado", status=403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator
