from app.modules.users import repository as repo
from app.modules.users.models import UPDATABLE_FIELDS
from app.utils.helpers import serialize_doc

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
