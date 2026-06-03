from bson import ObjectId
from flask_jwt_extended import create_access_token

from app.extensions.bcrypt import bcrypt
from app.modules.auth.models import ROLES, build_user, normalize_role
from app.modules.auth.repository import create_user, find_by_email, increment_login
from app.utils.helpers import serialize_doc
from app.utils.validators import is_valid_email, required_fields


def register_user(data):
    missing = required_fields(data, ["nombre", "apellido", "correo", "password"])
    if missing:
        return None, f"Campos requeridos: {', '.join(missing)}"

    if not is_valid_email(data["correo"]):
        return None, "Correo invalido"

    rol = normalize_role(data.get("rol", "productor"))
    if rol not in ROLES:
        return None, f"Rol invalido. Debe ser uno de: {', '.join(ROLES)}"

    if find_by_email(data["correo"]):
        return None, "El correo ya esta registrado"

    password_hash = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    user_doc = build_user(
        nombre=data["nombre"],
        apellido=data["apellido"],
        correo=data["correo"],
        password_hash=password_hash,
        telefono=data.get("telefono", ""),
        rol=rol,
    )
    user_id = create_user(user_doc)
    return {"id": user_id}, None


def login_user(data):
    missing = required_fields(data, ["correo", "password"])
    if missing:
        return None, f"Campos requeridos: {', '.join(missing)}"

    user = find_by_email(data["correo"])
    if not user:
        return None, "Credenciales invalidas"

    if not bcrypt.check_password_hash(user["password"], data["password"]):
        return None, "Credenciales invalidas"

    if user.get("estado") == "suspendido":
        return None, "Cuenta suspendida. Contacta al administrador."

    user_id = str(user["_id"])
    token = create_access_token(identity=user_id)
    was_reactivated = increment_login(user_id)
    return {
        "token": token,
        "rol": normalize_role(user["rol"]),
        "plan": user["plan"],
        "wasReactivated": bool(was_reactivated),
    }, None


def get_me(user_id):
    from app.database.mongo import get_db

    user = get_db().users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return None, "Usuario no encontrado"
    user.pop("password", None)
    user["rol"] = normalize_role(user.get("rol"))
    return serialize_doc(user), None


def google_login_user(data):
    token = data.get("idToken")
    if not token:
        return None, "Token de Google es requerido"

    try:
        from google.auth.transport import requests as google_requests
        from google.oauth2 import id_token

        from app.config.config import Config

        id_info = id_token.verify_oauth2_token(token, google_requests.Request(), Config.GOOGLE_CLIENT_ID)

        if id_info["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            return None, "Emisor de token invalido"

        email = id_info.get("email")
        if not email:
            return None, "No se pudo obtener el correo de Google"

        user = find_by_email(email)
        if not user:
            nombre = id_info.get("given_name") or "Usuario"
            apellido = id_info.get("family_name") or "Google"

            user_doc = build_user(
                nombre=nombre,
                apellido=apellido,
                correo=email,
                password_hash="",
                telefono="",
                rol="productor",
            )
            user_doc["googleLogin"] = True

            user_id = create_user(user_doc)
            user = find_by_email(email)
            is_new_user = True
        else:
            user_id = str(user["_id"])
            is_new_user = False

        if user.get("estado") == "suspendido":
            return None, "Cuenta suspendida. Contacta al administrador."

        app_token = create_access_token(identity=user_id)
        was_reactivated = increment_login(user_id)
        return {
            "token": app_token,
            "rol": normalize_role(user["rol"]),
            "plan": user.get("plan", "basico"),
            "isNewUser": is_new_user,
            "wasReactivated": bool(was_reactivated),
        }, None

    except ValueError as e:
        return None, f"Token de Google invalido: {str(e)}"
    except Exception as e:
        return None, f"Error en login de Google: {str(e)}"
