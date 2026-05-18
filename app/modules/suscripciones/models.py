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
            "3 muestras o diagnósticos al mes",
            "Orientación preliminar",
            "Recomendaciones preventivas básicas",
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
        "limites": {"parcelas": -1, "muestras": -1},
        "caracteristicas": [
            "Parcelas ilimitadas",
            "Muestras ilimitadas",
            "Registro de imágenes por muestra",
            "Datos de suelo: pH, NPK y humedad",
            "Alertas tempranas personalizadas",
            "Historial completo por parcela",
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
        "limites": {"parcelas": -1, "muestras": -1},
        "caracteristicas": [
            "Panel multi-productor",
            "Gestión de productores asociados",
            "Reportes por parcela y por zona",
            "Métricas consolidadas",
            "Exportación de reportes",
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
        "limites": {"parcelas": -1, "muestras": -1},
        "caracteristicas": [
            "Monitoreo territorial",
            "Gestión avanzada por roles",
            "Panel institucional",
            "Reportes consolidados por zona",
            "Capacitaciones técnicas",
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
