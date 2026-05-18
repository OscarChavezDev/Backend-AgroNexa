from app.utils.helpers import now_utc
from bson import ObjectId


def build_parcela(user_id, data):
    return {
        "userId": ObjectId(user_id),
        "nombre": data["nombre"],
        "ubicacion": {
            "lat": data["ubicacion"]["lat"],
            "lng": data["ubicacion"]["lng"],
        },
        "area": data.get("area"),
        "unidadArea": data.get("unidadArea", "ha"),
        "cultivo": data.get("cultivo", ""),
        "variedad": data.get("variedad", ""),
        "edadCultivo": data.get("edadCultivo", ""),
        "cantidadPlantas": data.get("cantidadPlantas"),
        "sistemaCultivo": data.get("sistemaCultivo", ""),
        "referencia": data.get("referencia", ""),
        "estado": "activo",
        "createdAt": now_utc(),
        "updatedAt": now_utc(),
    }
