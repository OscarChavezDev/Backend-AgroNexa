from app.utils.helpers import now_utc
from bson import ObjectId


def build_parcela(user_id, data):
    return {
        "userId": ObjectId(user_id),
        "nombre": data["nombre"],
        "cultivo": data["cultivo"],
        "ubicacion": {
            "lat": data["ubicacion"]["lat"],
            "lng": data["ubicacion"]["lng"],
        },
        "referencia": data["referencia"],
        "areaAproximada": data.get("areaAproximada"),
        "unidadArea": data.get("unidadArea", "ha"),
        "observaciones": data.get("observaciones", ""),
        "variedad": data.get("variedad", ""),
        "edadCultivo": data.get("edadCultivo", ""),
        "cantidadPlantas": data.get("cantidadPlantas"),
        "sistemaCultivo": data.get("sistemaCultivo", ""),
        "estado": "activo",
        "createdAt": now_utc(),
        "updatedAt": now_utc(),
    }
