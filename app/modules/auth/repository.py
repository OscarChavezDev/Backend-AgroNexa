from bson import ObjectId

from app.database.mongo import get_db
from app.utils.helpers import now_utc


def find_by_email(correo):
    return get_db().users.find_one({"correo": correo})


def find_by_id(user_id):
    return get_db().users.find_one({"_id": ObjectId(user_id)})


def create_user(user_doc):
    result = get_db().users.insert_one(user_doc)
    return str(result.inserted_id)


def increment_login(user_id):
    db = get_db()
    user = db.users.find_one({"_id": ObjectId(user_id)}, {"estado": 1, "inactivadoAuto": 1})
    if not user:
        return False

    ts = now_utc()
    ops = {
        "$inc": {"loginCount": 1},
        "$set": {"lastLogin": ts, "updatedAt": ts},
    }

    fue_inactivo = user.get("estado") == "inactivo"
    if fue_inactivo:
        ops["$set"]["estado"] = "activo"
        ops["$set"]["inactivadoAuto"] = False
        ops["$push"] = {
            "historialEstado": {
                "tipo": "reactivado_automatico",
                "fecha": ts,
                "motivo": "El usuario volvio a iniciar sesion tras un periodo de inactividad",
            }
        }

    db.users.update_one({"_id": ObjectId(user_id)}, ops)

    if fue_inactivo:
        full = db.users.find_one({"_id": ObjectId(user_id)}, {"nombre": 1, "apellido": 1, "correo": 1})
        if full:
            try:
                from app.modules.mensajes.service import crear_notif_reingreso

                crear_notif_reingreso(
                    user_id=user_id,
                    nombre=full.get("nombre", ""),
                    apellido=full.get("apellido", ""),
                    correo=full.get("correo", ""),
                )
            except Exception:
                pass

    return fue_inactivo
