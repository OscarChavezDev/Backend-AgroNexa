from app.modules.muestras.models import build_muestra
from app.modules.muestras import repository as repo
from app.modules.parcelas.repository import find_by_id_and_user as parcela_exists
from app.utils.helpers import serialize_doc
from app.utils.validators import required_fields

UPDATABLE_FIELDS = {
    "parteAfectada", "nivelAfectacion", "sintomas", "observaciones", "datosSensor",
}


def create_muestra(user_id, data):
    missing = required_fields(data, ["parcelaId", "parteAfectada", "nivelAfectacion"])
    if missing:
        return None, f"Campos requeridos: {', '.join(missing)}"

    if not parcela_exists(data["parcelaId"], user_id):
        return None, "Parcela no encontrada o no pertenece al usuario"

    doc = build_muestra(user_id, data)
    muestra_id = repo.create(doc)
    return {"id": muestra_id}, None


def list_muestras(user_id):
    muestras = repo.find_all_by_user(user_id)
    return [serialize_doc(m) for m in muestras], None


def list_muestras_by_parcela(parcela_id, user_id):
    if not parcela_exists(parcela_id, user_id):
        return None, "Parcela no encontrada o no pertenece al usuario"
    muestras = repo.find_all_by_parcela(parcela_id, user_id)
    return [serialize_doc(m) for m in muestras], None


def get_muestra(muestra_id, user_id):
    muestra = repo.find_by_id_and_user(muestra_id, user_id)
    if not muestra:
        return None, "Muestra no encontrada"
    return serialize_doc(muestra), None


def update_muestra(muestra_id, user_id, data):
    fields = {k: v for k, v in data.items() if k in UPDATABLE_FIELDS}
    if not fields:
        return None, "No hay campos válidos para actualizar"

    updated = repo.update(muestra_id, user_id, fields)
    if not updated:
        return None, "Muestra no encontrada"
    return {"id": muestra_id}, None


def delete_muestra(muestra_id, user_id):
    deleted = repo.soft_delete(muestra_id, user_id)
    if not deleted:
        return None, "Muestra no encontrada"
    return {"id": muestra_id}, None
