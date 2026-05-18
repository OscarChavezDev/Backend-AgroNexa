from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.utils.response import error_response


def jwt_required_custom(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            return error_response("Token inválido o expirado", status=401)
        return fn(*args, **kwargs)
    return wrapper
