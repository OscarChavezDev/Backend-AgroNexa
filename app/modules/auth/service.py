from flask_jwt_extended import create_access_token
from app.extensions.bcrypt import bcrypt
from app.modules.auth.repository import find_by_email, create_user
from app.modules.auth.models import build_user, ROLES
from app.utils.validators import is_valid_email, required_fields
from app.utils.helpers import serialize_doc
from bson import ObjectId


def register_user(data):
    missing = required_fields(data, ["nombre", "apellido", "correo", "password"])
    if missing:
        return None, f"Campos requeridos: {', '.join(missing)}"

    if not is_valid_email(data["correo"]):
        return None, "Correo inválido"

    rol = data.get("rol", "productor")
    if rol not in ROLES:
        return None, f"Rol inválido. Debe ser uno de: {', '.join(ROLES)}"

    if find_by_email(data["correo"]):
        return None, "El correo ya está registrado"

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
        return None, "Credenciales inválidas"

    if not bcrypt.check_password_hash(user["password"], data["password"]):
        return None, "Credenciales inválidas"

    if user.get("estado") != "activo":
        return None, "Cuenta inactiva"

    token = create_access_token(identity=str(user["_id"]))
    return {"token": token, "rol": user["rol"], "plan": user["plan"]}, None


def get_me(user_id):
    from app.database.mongo import get_db
    user = get_db().users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return None, "Usuario no encontrado"
    user.pop("password", None)
    return serialize_doc(user), None
