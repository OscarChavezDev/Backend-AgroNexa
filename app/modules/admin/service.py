from app.database.mongo import get_db
from app.modules.auth.models import normalize_role
from app.utils.helpers import serialize_doc, now_utc
from bson import ObjectId

VALID_ESTADOS = ("activo", "inactivo", "suspendido")


def list_all_users(filters=None):
    db = get_db()
    query = filters or {}

    pipeline = [
        {"$match": query},
        {"$lookup": {
            "from": "parcelas",
            "let": {"uid": "$_id"},
            "pipeline": [{"$match": {"$expr": {"$eq": ["$userId", "$$uid"]}, "estado": {"$ne": "eliminado"}}}],
            "as": "_p"
        }},
        {"$lookup": {
            "from": "muestras",
            "let": {"uid": "$_id"},
            "pipeline": [{"$match": {"$expr": {"$eq": ["$userId", "$$uid"]}, "estado": {"$ne": "eliminado"}}}],
            "as": "_m"
        }},
        {"$lookup": {
            "from": "diagnosticos",
            "let": {"uid": "$_id"},
            "pipeline": [{"$match": {"$expr": {"$eq": ["$userId", "$$uid"]}}}],
            "as": "_d"
        }},
        {"$addFields": {
            "totalParcelas":     {"$size": "$_p"},
            "totalMuestras":     {"$size": "$_m"},
            "totalDiagnosticos": {"$size": "$_d"},
        }},
        {"$project": {"_p": 0, "_m": 0, "_d": 0, "password": 0}},
        {"$sort": {"createdAt": -1}},
    ]

    users = list(db.users.aggregate(pipeline))
    for u in users:
        u["rol"] = normalize_role(u.get("rol"))
    return [serialize_doc(u) for u in users], None


def get_user_detail(user_id):
    db = get_db()
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return None, "Usuario no encontrado"
    user.pop("password", None)
    user["rol"] = normalize_role(user.get("rol"))
    return serialize_doc(user), None


def change_user_status(user_id, estado):
    if estado not in VALID_ESTADOS:
        return None, f"Estado inválido. Debe ser uno de: {', '.join(VALID_ESTADOS)}"
    db = get_db()
    result = db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"estado": estado, "updatedAt": now_utc()}},
    )
    if result.matched_count == 0:
        return None, "Usuario no encontrado"
    return {"id": user_id}, None


def delete_user(user_id):
    db = get_db()
    result = db.users.delete_one({"_id": ObjectId(user_id), "rol": {"$ne": "admin"}})
    if result.deleted_count == 0:
        return None, "Usuario no encontrado o no se puede eliminar un administrador"
    return {"id": user_id}, None


def get_user_parcelas(user_id):
    db = get_db()
    pipeline = [
        {"$match": {"userId": ObjectId(user_id), "estado": {"$ne": "eliminado"}}},
        {"$lookup": {
            "from": "muestras",
            "let": {"pid": "$_id"},
            "pipeline": [{"$match": {"$expr": {"$eq": ["$parcelaId", "$$pid"]}, "estado": {"$ne": "eliminado"}}}],
            "as": "_m",
        }},
        {"$lookup": {
            "from": "diagnosticos",
            "let": {"pid": "$_id"},
            "pipeline": [{"$match": {"$expr": {"$eq": ["$parcelaId", "$$pid"]}}}],
            "as": "_d",
        }},
        {"$addFields": {
            "totalMuestras":     {"$size": "$_m"},
            "totalDiagnosticos": {"$size": "$_d"},
        }},
        {"$project": {"_m": 0, "_d": 0}},
        {"$sort": {"nombre": 1}},
    ]
    parcelas = list(db.parcelas.aggregate(pipeline))
    return [serialize_doc(p) for p in parcelas], None


def get_stats():
    db = get_db()
    total_usuarios = db.users.count_documents({"rol": {"$ne": "admin"}})
    activos = db.users.count_documents({"rol": {"$ne": "admin"}, "estado": "activo"})
    inactivos = db.users.count_documents({"rol": {"$ne": "admin"}, "estado": "inactivo"})
    total_parcelas = db.parcelas.count_documents({"estado": "activo"})
    total_muestras = db.muestras.count_documents({"estado": {"$ne": "eliminado"}})
    total_diagnosticos = db.diagnosticos.count_documents({})
    return {
        "usuarios": {"total": total_usuarios, "activos": activos, "inactivos": inactivos},
        "parcelas": total_parcelas,
        "muestras": total_muestras,
        "diagnosticos": total_diagnosticos,
    }, None
