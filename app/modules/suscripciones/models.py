from app.utils.helpers import now_utc
from datetime import timedelta
from bson import ObjectId

PLANES_DATA = [
    {
        "codigo": "basico",
        "nombre": "Plan Básico",
        "precio": 0,
        "moneda": "PEN",
        "periodo": "mensual",
        "trialDias": 0,
        "limites": {"parcelas": 2, "muestras": 3},
        "caracteristicas": [
            "Hasta 2 parcelas registradas",
            "3 diagnósticos con IA al mes",
            "Lectura básica de sensores (pH, NPK)",
            "Soporte: Auto-servicio (Preguntas Frecuentes)",
        ],
        "estado": "activo",
    },
    {
        "codigo": "plus",
        "nombre": "Productor Plus",
        "precio": 15,
        "moneda": "PEN",
        "periodo": "mensual",
        "trialDias": 30,
        "limites": {"parcelas": 15, "muestras": 30},
        "caracteristicas": [
            "Hasta 15 parcelas registradas",
            "30 diagnósticos con IA al mes",
            "Historial gráfico de sensores completo",
            "Alertas de clima y riesgo de plagas",
            "Soporte por correo y chat",
        ],
        "estado": "activo",
    },
    {
        "codigo": "asociacion",
        "nombre": "Asociación",
        "precio": 200,
        "moneda": "PEN",
        "periodo": "mensual",
        "trialDias": 30,
        "limites": {"parcelas": -1, "muestras": 500},
        "caracteristicas": [
            "Parcelas ilimitadas",
            "Hasta 50 productores asociados",
            "500 diagnósticos con IA al mes (Bolsa compartida)",
            "Reportes consolidados de suelo",
            "Alertas grupales por sector/zona",
            "Exportación en PDF/Excel para certificaciones",
            "Soporte vía WhatsApp + 1 capacitación virtual",
        ],
        "estado": "activo",
    },
    {
        "codigo": "institucional",
        "nombre": "Institucional",
        "precio": 350,
        "moneda": "PEN",
        "periodo": "mensual",
        "trialDias": 30,
        "limites": {"parcelas": -1, "muestras": 1500},
        "caracteristicas": [
            "Parcelas ilimitadas",
            "Múltiples cuentas para técnicos",
            "1,500 diagnósticos con IA al mes (Bolsa compartida)",
            "Mapa de calor de nutrientes por zona",
            "Monitoreo de brotes epidémicos territoriales",
            "Reportes consolidados y estadísticas públicas",
            "Soporte prioritario 24/7 + 2 capacitaciones virtuales/año",
        ],
        "estado": "activo",
    },
]


def build_suscripcion(user_id, plan_doc):
    ahora = now_utc()
    tiene_trial = plan_doc["trialDias"] > 0
    fecha_fin = ahora + timedelta(days=30)
    trial_fin = ahora + timedelta(days=plan_doc["trialDias"]) if tiene_trial else None

    return {
        "userId": ObjectId(user_id),
        "plan": plan_doc["codigo"],
        "precio": plan_doc["precio"],
        "estado": "activo",
        "fechaInicio": ahora,
        "fechaFin": fecha_fin,
        "trial": tiene_trial,
        "trialInicio": ahora if tiene_trial else None,
        "trialFin": trial_fin,
        "createdAt": ahora,
    }
