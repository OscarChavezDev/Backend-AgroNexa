from app.modules.parcelas.models import (
    build_parcela, normalizar_nodos, normalizar_poligono, centro_de,
)
from app.modules.parcelas import repository as repo
from app.utils.helpers import serialize_doc
from app.utils.validators import required_fields

UPDATABLE_FIELDS = {
    "nombre", "cultivo", "ubicacion", "referencia",
    "areaAproximada", "unidadArea", "observaciones",
    "variedad", "edadCultivo", "cantidadPlantas", "sistemaCultivo",
    "poligono", "nodos",
}


def create_parcela(user_id, data):
    missing = required_fields(data, ["nombre", "cultivo", "referencia"])
    if missing:
        return None, f"Campos requeridos: {', '.join(missing)}"

    poligono = normalizar_poligono(data.get("poligono"))
    nodos = normalizar_nodos(data.get("nodos"))
    ubicacion = data.get("ubicacion") or {}

    # Si se dibujó el lindero o se marcaron nodos, el punto principal se deduce
    # de ellos: obligar a marcar además un punto suelto sería redundante.
    if "lat" not in ubicacion or "lng" not in ubicacion:
        derivada = centro_de(poligono, nodos, None)
        if not derivada:
            return None, "Marca la ubicación de la parcela en el mapa"
        ubicacion = derivada

    data = {**data, "ubicacion": ubicacion}
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

    # El mapa se guarda ya normalizado para que las muestras siempre encuentren
    # sus nodos con el mismo id.
    if "poligono" in fields:
        fields["poligono"] = normalizar_poligono(fields["poligono"])
    if "nodos" in fields:
        fields["nodos"] = normalizar_nodos(fields["nodos"])

    updated = repo.update(parcela_id, user_id, fields)
    if not updated:
        return None, "Parcela no encontrada"
    return {"id": parcela_id}, None


def delete_parcela(parcela_id, user_id):
    deleted = repo.deactivate(parcela_id, user_id)
    if not deleted:
        return None, "Parcela no encontrada"
    return {"id": parcela_id}, None
