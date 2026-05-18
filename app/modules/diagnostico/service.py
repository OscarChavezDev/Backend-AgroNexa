from app.modules.diagnostico.rules import generar_diagnostico
from app.modules.diagnostico.models import build_diagnostico
from app.modules.diagnostico import repository as repo
from app.modules.muestras.repository import find_by_id_and_user, find_by_id, update as update_muestra
from app.utils.helpers import serialize_doc


def generar(muestra_id, user_id):
    muestra = find_by_id_and_user(muestra_id, user_id)
    if not muestra:
        return None, "Muestra no encontrada"

    if repo.find_by_muestra(muestra_id):
        return None, "Esta muestra ya tiene un diagnóstico generado"

    diagnostico_data = generar_diagnostico(muestra)
    doc = build_diagnostico(muestra, diagnostico_data)
    diagnostico_id = repo.create(doc)

    update_muestra(muestra_id, user_id, {"estado": "diagnosticado"})

    result = serialize_doc(doc)
    result["id"] = diagnostico_id
    return result, None


def get_diagnostico(diagnostico_id):
    doc = repo.find_by_id(diagnostico_id)
    if not doc:
        return None, "Diagnóstico no encontrado"
    return serialize_doc(doc), None


def get_diagnostico_by_muestra(muestra_id, user_id):
    muestra = find_by_id_and_user(muestra_id, user_id)
    if not muestra:
        return None, "Muestra no encontrada"

    doc = repo.find_by_muestra(muestra_id)
    if not doc:
        return None, "Esta muestra aún no tiene diagnóstico"
    return serialize_doc(doc), None
