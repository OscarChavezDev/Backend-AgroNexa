from datetime import timedelta

from app.database.mongo import get_db
from app.modules.auth.models import normalize_role
from app.utils.helpers import serialize_doc, now_utc
from bson import ObjectId

VALID_ESTADOS    = ("activo", "inactivo", "suspendido")
INACTIVIDAD_DIAS = 14   # días sin actividad para marcar inactivo


def aplicar_inactividad_automatica():
    """
    1. Marca como inactivos a usuarios activos sin login en INACTIVIDAD_DIAS días.
       La fecha del evento es el lastLogin real (cuándo dejaron de usar el sistema).
    2. Repara entradas antiguas con fecha incorrecta: si el evento inactivado_automatico
       tiene fecha = updatedAt (detectada hoy en vez del lastLogin real), la corrige.
    """
    db     = get_db()
    ts     = now_utc()
    limite = ts - timedelta(days=INACTIVIDAD_DIAS)

    # ── 1. Nuevos candidatos ─────────────────────────────────────────────────
    candidatos = list(db.users.find({
        "estado": "activo",
        "rol":    {"$ne": "admin"},
        "$or": [
            {"lastLogin": {"$lt": limite}},
            {"lastLogin": {"$exists": False}, "createdAt": {"$lt": limite}},
        ],
    }, {"_id": 1, "lastLogin": 1, "createdAt": 1}))

    for u in candidatos:
        fecha_inactivacion = u.get("lastLogin") or u.get("createdAt") or ts
        db.users.update_one(
            {"_id": u["_id"]},
            {
                "$set": {
                    "estado":         "inactivo",
                    "inactivadoAuto": True,
                    "updatedAt":      ts,
                },
                "$push": {
                    "historialEstado": {
                        "tipo":   "inactivado_automatico",
                        "fecha":  fecha_inactivacion,
                        "motivo": f"Sin actividad durante {INACTIVIDAD_DIAS} días consecutivos",
                    }
                },
            },
        )

    # ── 2. Reparar entradas antiguas con fecha = updatedAt (código anterior) ─
    # Detectar: evento inactivado_automatico cuya fecha es igual a updatedAt
    # (se guardó "ahora" en vez del lastLogin real). Corregirla con lastLogin.
    ya_inactivos = list(db.users.find(
        {"estado": "inactivo", "inactivadoAuto": True, "rol": {"$ne": "admin"},
         "historialEstado": {"$elemMatch": {"tipo": "inactivado_automatico"}}},
        {"_id": 1, "lastLogin": 1, "createdAt": 1, "updatedAt": 1, "historialEstado": 1}
    ))

    for u in ya_inactivos:
        historial  = u.get("historialEstado") or []
        last_login = u.get("lastLogin") or u.get("createdAt")
        if not last_login:
            continue
        updated_at = u.get("updatedAt")

        nuevos = []
        reparado = False
        for h in historial:
            if (h.get("tipo") == "inactivado_automatico"
                    and updated_at
                    and h.get("fecha") == updated_at):
                # Fecha incorrecta — reemplazar con lastLogin
                h = dict(h)
                h["fecha"] = last_login
                reparado = True
            nuevos.append(h)

        if reparado:
            db.users.update_one(
                {"_id": u["_id"]},
                {"$set": {"historialEstado": nuevos}}
            )

    return len(candidatos)


def list_all_users(filters=None):
    # Aplica la regla de inactividad antes de devolver la lista
    aplicar_inactividad_automatica()

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
    db  = get_db()
    ts  = now_utc()
    tipo_map = {
        "activo":     "activado_manual",
        "inactivo":   "inactivado_manual",
        "suspendido": "suspendido_manual",
    }
    result = db.users.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "estado":         estado,
                "inactivadoAuto": False,   # al cambiar manualmente, limpiar flag auto
                "updatedAt":      ts,
            },
            "$push": {
                "historialEstado": {
                    "tipo":   tipo_map.get(estado, "cambio_manual"),
                    "fecha":  ts,
                    "motivo": f"Estado cambiado manualmente por el administrador a '{estado}'",
                }
            },
        },
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


def get_user_historial(user_id):
    """Devuelve el historial de cambios de estado de un usuario, más reciente primero."""
    db   = get_db()
    user = db.users.find_one({"_id": ObjectId(user_id)}, {"historialEstado": 1, "estado": 1})
    if not user:
        return None, "Usuario no encontrado"
    historial = user.get("historialEstado") or []
    # Ordenar más reciente primero
    historial = sorted(historial, key=lambda x: x.get("fecha", ""), reverse=True)
    return [_serialize_historial(h) for h in historial], None


def _serialize_historial(entry):
    from app.utils.helpers import _serialize_value
    return {k: _serialize_value(v) for k, v in entry.items()}


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


def get_actividad_temporal():
    """
    Retorna:
    - porDia:      actividad (muestras) por día de la semana
    - porMes:      actividad (muestras) por mes (últimos 6 meses)
    - registros:   usuarios registrados por día (últimos 90 días)
    """
    from datetime import datetime, timezone, date
    db = get_db()

    # ── Por día de semana (muestras) ───────────────────────────────────────────
    pipeline_dia = [
        {"$match": {"estado": {"$ne": "eliminado"}}},
        {"$group": {"_id": {"$dayOfWeek": "$createdAt"}, "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    raw_dias = {d["_id"]: d["count"] for d in db.muestras.aggregate(pipeline_dia)}
    nombres  = {1: "Dom", 2: "Lun", 3: "Mar", 4: "Mié", 5: "Jue", 6: "Vie", 7: "Sáb"}
    por_dia  = [{"dia": nombres[i], "count": raw_dias.get(i, 0)} for i in range(1, 8)]

    # ── Por mes — últimos 6 meses (muestras) ───────────────────────────────────
    ahora  = datetime.now(timezone.utc)
    inicio = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    for _ in range(5):
        inicio = (inicio.replace(day=1) - timedelta(days=1)).replace(day=1)

    pipeline_mes = [
        {"$match": {"estado": {"$ne": "eliminado"}, "createdAt": {"$gte": inicio}}},
        {"$group": {
            "_id": {"year": {"$year": "$createdAt"}, "month": {"$month": "$createdAt"}},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id.year": 1, "_id.month": 1}}
    ]
    meses_es = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
                "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    por_mes  = []
    for m in db.muestras.aggregate(pipeline_mes):
        y, mo = m["_id"]["year"], m["_id"]["month"]
        por_mes.append({"mes": f"{meses_es[mo-1]} {str(y)[2:]}", "count": m["count"]})

    # ── Registros de usuarios por día (últimos 90 días) ────────────────────────
    hace_90 = datetime(ahora.year, ahora.month, ahora.day,
                       tzinfo=timezone.utc) - timedelta(days=89)

    pipeline_reg = [
        {"$match": {"rol": {"$ne": "admin"}, "createdAt": {"$gte": hace_90}}},
        {"$group": {
            "_id": {
                "y": {"$year": "$createdAt"},
                "m": {"$month": "$createdAt"},
                "d": {"$dayOfMonth": "$createdAt"}
            },
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id.y": 1, "_id.m": 1, "_id.d": 1}}
    ]
    raw_reg = {
        date(r["_id"]["y"], r["_id"]["m"], r["_id"]["d"]): r["count"]
        for r in db.users.aggregate(pipeline_reg)
    }

    # Construir serie completa día a día (sin huecos)
    registros = []
    for i in range(90):
        dia = (hace_90 + timedelta(days=i)).date()
        registros.append({
            "fecha": dia.isoformat(),
            "count": raw_reg.get(dia, 0)
        })

    return {"porDia": por_dia, "porMes": por_mes, "registros": registros}, None


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

def get_reingresos():
    """
    Retorna todos los eventos de reingreso (reactivado_automatico) de todos los usuarios.
    Para cada reingreso incluye cuándo fue inactivado y cuántos días estuvo ausente.
    Ordenado más reciente primero.
    """
    from app.utils.helpers import _serialize_value
    db = get_db()
    usuarios = list(db.users.find(
        {"rol": {"$ne": "admin"}, "historialEstado": {"$exists": True, "$ne": []}},
        {"password": 0}
    ))

    eventos = []
    for u in usuarios:
        historial = sorted(
            u.get("historialEstado") or [],
            key=lambda x: x.get("fecha") or "",
        )
        # Emparejar cada reactivación con su inactivación previa más cercana
        # Acepta tanto inactivación automática como manual
        ultima_inactivacion = None
        for h in historial:
            tipo = h.get("tipo", "")
            if tipo in ("inactivado_automatico", "inactivado_manual"):
                ultima_inactivacion = h
            elif tipo == "reactivado_automatico":
                fecha_reactiv = h.get("fecha")
                fecha_inactiv = ultima_inactivacion.get("fecha") if ultima_inactivacion else None

                dias_inactivo = None
                if fecha_reactiv and fecha_inactiv:
                    try:
                        # Usar total_seconds para precisión real (no truncar a días completos)
                        total_horas = (fecha_reactiv - fecha_inactiv).total_seconds() / 3600
                        dias_inactivo = round(total_horas / 24, 1)  # 1 decimal
                        if dias_inactivo < 0:
                            dias_inactivo = 0
                    except Exception:
                        pass

                eventos.append({
                    "userId":           str(u["_id"]),
                    "nombre":           u.get("nombre", ""),
                    "apellido":         u.get("apellido", ""),
                    "correo":           u.get("correo", ""),
                    "rol":              normalize_role(u.get("rol", "")),
                    "fecha":            _serialize_value(fecha_reactiv),
                    "fechaInactivacion": _serialize_value(fecha_inactiv),
                    "diasInactivo":     dias_inactivo,
                    "motivo":           h.get("motivo", ""),
                })
                ultima_inactivacion = None  # reset para el próximo ciclo

    eventos.sort(key=lambda x: x["fecha"] or "", reverse=True)
    return eventos, None
