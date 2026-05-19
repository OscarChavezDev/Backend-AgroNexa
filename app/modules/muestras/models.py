from app.utils.helpers import now_utc
from bson import ObjectId

PARTES_AFECTADAS = ("hoja", "fruto", "tallo", "raiz", "flor", "planta_completa")
NIVELES_AFECTACION = ("leve", "moderado", "severo")
SINTOMAS_VALIDOS = (
    "manchas oscuras", "manchas amarillas", "pudricion", "polvo blanco",
    "fruto seco", "fruto deformado", "hojas secas", "ramas secas",
    "brotes deformados", "marchitez", "caida de frutos", "hongos visibles",
)


def build_muestra(user_id, data):
    sensor = data.get("datosSensor") or {}
    return {
        "parcelaId": ObjectId(data["parcelaId"]),
        "userId": ObjectId(user_id),
        "parteAfectada": data["parteAfectada"],
        "nivelAfectacion": data["nivelAfectacion"],
        "sintomas": data["sintomas"],
        "observaciones": data.get("observaciones", ""),
        "datosSensor": {
            "ph": sensor.get("ph"),
            "nitrogeno": sensor.get("nitrogeno"),
            "fosforo": sensor.get("fosforo"),
            "potasio": sensor.get("potasio"),
            "humedadSuelo": sensor.get("humedadSuelo"),
            "temperaturaSuelo": sensor.get("temperaturaSuelo"),
            "conductividadElectrica": sensor.get("conductividadElectrica"),
        },
        "estado": "registrado",
        "createdAt": now_utc(),
        "updatedAt": now_utc(),
    }
