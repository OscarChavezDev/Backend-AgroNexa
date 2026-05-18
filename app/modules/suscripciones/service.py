from app.modules.suscripciones import repository as repo
from app.modules.suscripciones.models import build_suscripcion
from app.modules.users.repository import update_plan
from app.utils.helpers import serialize_doc


def list_planes():
    planes = repo.get_all_planes()
    return [serialize_doc(p) for p in planes], None


def suscribir(user_id, data):
    codigo = data.get("plan")
    if not codigo:
        return None, "El campo 'plan' es requerido"

    plan_doc = repo.get_plan_by_codigo(codigo)
    if not plan_doc:
        return None, "Plan no encontrado"

    repo.deactivate_all_by_user(user_id)

    doc = build_suscripcion(user_id, plan_doc)
    suscripcion_id = repo.create_suscripcion(doc)

    update_plan(user_id, codigo)

    return {"id": suscripcion_id, "plan": codigo}, None


def get_suscripcion_actual(user_id):
    doc = repo.find_active_by_user(user_id)
    if not doc:
        return None, "No tienes una suscripción activa"
    return serialize_doc(doc), None


def cambiar_plan(user_id, data):
    return suscribir(user_id, data)
