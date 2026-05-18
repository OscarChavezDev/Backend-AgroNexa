from app.utils.helpers import now_utc
from bson import ObjectId


def build_muestra(user_id, data):
    return {
        "parcelaId": ObjectId(data["parcelaId"]),
        "userId": ObjectId(user_id),
        "fechaObservacion": data.get("fechaObservacion", now_utc()),
        "parteAfectada": data.get("parteAfectada", ""),
        "etapaCultivo": data.get("etapaCultivo", ""),
        "nivelAfectacion": data.get("nivelAfectacion", "leve"),
        "observaciones": data.get("observaciones", ""),
        "sintomas": data.get("sintomas", []),
        "datosSuelo": {
            "ph": data.get("datosSuelo", {}).get("ph"),
            "nitrogeno": data.get("datosSuelo", {}).get("nitrogeno", ""),
            "fosforo": data.get("datosSuelo", {}).get("fosforo", ""),
            "potasio": data.get("datosSuelo", {}).get("potasio", ""),
            "humedad": data.get("datosSuelo", {}).get("humedad", ""),
        },
        "datosAmbiente": {
            "temperatura": data.get("datosAmbiente", {}).get("temperatura"),
            "humedadAmbiental": data.get("datosAmbiente", {}).get("humedadAmbiental"),
            "lluviasRecientes": data.get("datosAmbiente", {}).get("lluviasRecientes", False),
            "sombraExcesiva": data.get("datosAmbiente", {}).get("sombraExcesiva", False),
        },
        "imagenes": [],
        "estado": "registrado",
        "createdAt": now_utc(),
        "updatedAt": now_utc(),
    }
