"""Acceso a datos del módulo admin.

El service compone las queries/pipelines (lógica de negocio) y este repositorio
ejecuta las operaciones contra Mongo. Es el único punto del módulo que toca get_db().
"""
from bson import ObjectId

from app.database.mongo import get_db


# ── Lecturas de usuarios ──────────────────────────────────────────────────────
def find_users(query, projection=None):
    return list(get_db().users.find(query, projection))


def find_user_by_id(user_id, projection=None):
    return get_db().users.find_one({"_id": ObjectId(user_id)}, projection)


def aggregate_users(pipeline):
    return list(get_db().users.aggregate(pipeline))


# ── Agregaciones de otras colecciones (analíticas del panel) ──────────────────
def aggregate_parcelas(pipeline):
    return list(get_db().parcelas.aggregate(pipeline))


def aggregate_muestras(pipeline):
    return list(get_db().muestras.aggregate(pipeline))


# ── Conteos (estadísticas) ────────────────────────────────────────────────────
def count_users(query):
    return get_db().users.count_documents(query)


def count_parcelas(query):
    return get_db().parcelas.count_documents(query)


def count_muestras(query):
    return get_db().muestras.count_documents(query)


def count_diagnosticos(query):
    return get_db().diagnosticos.count_documents(query)


# ── Escrituras de usuarios ────────────────────────────────────────────────────
def update_user(user_id, update):
    """Aplica un documento de actualización Mongo completo ($set, $push, ...).

    user_id puede ser ObjectId (interno) o str (desde la API).
    """
    oid = user_id if isinstance(user_id, ObjectId) else ObjectId(user_id)
    return get_db().users.update_one({"_id": oid}, update)


def delete_non_admin_user(user_id):
    return get_db().users.delete_one({"_id": ObjectId(user_id), "rol": {"$ne": "admin"}})
