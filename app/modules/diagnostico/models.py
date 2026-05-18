from app.utils.helpers import now_utc
from bson import ObjectId


def build_diagnostico(muestra, diagnostico_data):
    return {
        "muestraId": muestra["_id"],
        "parcelaId": muestra["parcelaId"],
        "userId": muestra["userId"],
        "resultado": diagnostico_data["resultado"],
        "motivo": diagnostico_data["motivo"],
        "recomendaciones": diagnostico_data["recomendaciones"],
        "createdAt": now_utc(),
    }
