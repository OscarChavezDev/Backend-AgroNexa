from app.modules.users import repository as repo
from app.modules.users.models import UPDATABLE_FIELDS
from app.utils.helpers import serialize_doc
from app.extensions.bcrypt import bcrypt

VALID_ESTADOS = ("activo", "inactivo", "suspendido")


def get_profile(user_id):
    user = repo.find_by_id(user_id)
    if not user:
        return None, "Usuario no encontrado"
    user.pop("password", None)
    return serialize_doc(user), None


def update_profile(user_id, data):
    fields = {k: v for k, v in data.items() if k in UPDATABLE_FIELDS}
    if not fields:
        return None, "No hay campos válidos para actualizar"
    repo.update(user_id, fields)
    return {"id": user_id}, None


def list_users(rol=None):
    filters = {}
    if rol:
        filters["rol"] = rol
    users = repo.find_all(filters)
    for u in users:
        u.pop("password", None)
    return [serialize_doc(u) for u in users], None


def get_user(user_id):
    user = repo.find_by_id(user_id)
    if not user:
        return None, "Usuario no encontrado"
    user.pop("password", None)
    return serialize_doc(user), None


def change_status(user_id, estado):
    if estado not in VALID_ESTADOS:
        return None, f"Estado inválido. Debe ser uno de: {', '.join(VALID_ESTADOS)}"
    updated = repo.update_status(user_id, estado)
    if not updated:
        return None, "Usuario no encontrado"
    return {"id": user_id}, None


def change_password(user_id, current_password, new_password):
    user = repo.find_by_id(user_id)
    if not user:
        return None, "Usuario no encontrado"

    # Verificar contraseña actual
    if not bcrypt.check_password_hash(user["password"], current_password):
        return None, "La contraseña actual es incorrecta"

    # Generar hash de la nueva contraseña
    new_password_hash = bcrypt.generate_password_hash(new_password).decode("utf-8")

    # Actualizar la contraseña en la base de datos
    updated = repo.update(user_id, {"password": new_password_hash})
    if not updated:
        return None, "No se pudo actualizar la contraseña"

    return {"id": user_id}, None

