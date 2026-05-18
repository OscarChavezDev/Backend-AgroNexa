from pymongo import ASCENDING, GEOSPHERE
from .mongo import get_db


def seed_initial_data():
    from app.modules.suscripciones.repository import seed_planes
    from app.modules.suscripciones.models import PLANES_DATA
    seed_planes(PLANES_DATA)


def create_indexes():
    db = get_db()
    if db is None:
        return

    db.users.create_index("correo", unique=True)
    db.users.create_index("rol")
    db.users.create_index("plan")

    db.parcelas.create_index("userId")
    db.parcelas.create_index([("ubicacion", GEOSPHERE)])
    db.parcelas.create_index("estado")

    db.muestras.create_index("userId")
    db.muestras.create_index("parcelaId")
    db.muestras.create_index("createdAt")
    db.muestras.create_index("estado")

    db.diagnosticos.create_index("muestraId")
    db.diagnosticos.create_index("parcelaId")
    db.diagnosticos.create_index("userId")
    db.diagnosticos.create_index("resultado.riesgo")
    db.diagnosticos.create_index("resultado.enfermedad")

    db.suscripciones.create_index("userId")
    db.suscripciones.create_index("plan")
    db.suscripciones.create_index("estado")
    db.suscripciones.create_index("fechaFin")
