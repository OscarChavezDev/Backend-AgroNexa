from app.utils.helpers import now_utc

ROLES = ("productor", "asociacion", "institucion", "admin")
ROLE_ALIASES = {
    "institucional": "institucion",
}
PLANES = ("basico", "plus", "asociacion", "institucional")


def normalize_role(rol):
    return ROLE_ALIASES.get(rol, rol)


def build_role_filter(rol):
    canonical_role = normalize_role(rol)
    aliases = [alias for alias, value in ROLE_ALIASES.items() if value == canonical_role]
    values = [canonical_role, *aliases]
    return values[0] if len(values) == 1 else {"$in": values}


def build_user(nombre, apellido, correo, password_hash, telefono="", rol="productor"):
    rol = normalize_role(rol)
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
