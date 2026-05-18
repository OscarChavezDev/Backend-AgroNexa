from app.modules.parcelas.models import build_parcela
from app.modules.parcelas import repository as repo
from app.utils.helpers import serialize_doc
from app.utils.validators import required_fields

UPDATABLE_FIELDS = {
    "nombre", "ubicacion", "area", "unidadArea", "cultivo",
    "variedad", "edadCultivo", "cantidadPlantas", "sistemaCultivo", "referencia",
}


def create_parcela(user_id, data):
    missing = required_fields(data, ["nombre", "ubicacion"])
    if missing:
        return None, f"Campos requeridos: {', '.join(missing)}"

    ubicacion = data.get("ubicacion", {})
    if "lat" not in ubicacion or "lng" not in ubicacion:
        return None, "ubicacion debe incluir lat y lng"

    doc = build_parcela(user_id, data)
    parcela_id = repo.create(doc)
    return {"id": parcela_id}, None


def list_parcelas(user_id):
    parcelas = repo.find_all_by_user(user_id)
    return [serialize_doc(p) for p in parcelas], None


def get_parcela(parcela_id, user_id):
    parcela = repo.find_by_id_and_user(parcela_id, user_id)
    if not parcela:
        return None, "Parcela no encontrada"
    return serialize_doc(parcela), None


def update_parcela(parcela_id, user_id, data):
    fields = {k: v for k, v in data.items() if k in UPDATABLE_FIELDS}
    if not fields:
        return None, "No hay campos válidos para actualizar"

    updated = repo.update(parcela_id, user_id, fields)
    if not updated:
        return None, "Parcela no encontrada"
    return {"id": parcela_id}, None


def delete_parcela(parcela_id, user_id):
    deleted = repo.deactivate(parcela_id, user_id)
    if not deleted:
        return None, "Parcela no encontrada"
    return {"id": parcela_id}, None
