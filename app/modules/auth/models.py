from app.utils.helpers import now_utc

ROLES = ("productor", "asociacion", "institucion", "admin")
PLANES = ("basico", "plus", "asociacion", "institucional")


def build_user(nombre, apellido, correo, password_hash, telefono="", rol="productor"):
    return {
        "nombre": nombre,
        "apellido": apellido,
        "correo": correo,
        "password": password_hash,
        "telefono": telefono,
        "rol": rol,
        "plan": "basico",
        "estado": "activo",
        "createdAt": now_utc(),
        "updatedAt": now_utc(),
    }
