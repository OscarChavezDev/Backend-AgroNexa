import logging

from app.modules.fertilizacion import repository as repo
from app.modules.fertilizacion.ai_service import generar_plan_ia
from app.modules.fertilizacion.models import build_plan_fertilizacion
from app.modules.fertilizacion.rules import (
    generar_plan as generar_plan_reglas,
    interpretar_suelo,
    evaluar_ventana_aplicacion,
)
from app.modules.clima.service import obtener_pronostico
from app.modules.parcelas.repository import find_by_id_and_user as find_parcela
from app.modules.muestras.repository import find_all_by_parcela
from app.utils.helpers import serialize_doc

logger = logging.getLogger(__name__)

PARCELA_NO_ENCONTRADA = "Parcela no encontrada"


def _ultima_muestra_con_suelo(parcela_id, user_id):
    """
    Devuelve la muestra más reciente que tenga al menos un dato de suelo.
    Las muestras vienen ordenadas por fecha descendente desde el repositorio.
    """
    muestras = find_all_by_parcela(parcela_id, user_id)
    claves = ("ph", "nitrogeno", "fosforo", "potasio", "humedadSuelo", "conductividadElectrica")

    for muestra in muestras:
        sensor = muestra.get("datosSensor") or {}
        if any(sensor.get(k) is not None for k in claves):
            return muestra

    return muestras[0] if muestras else None


def _normalizar_plan_ia(plan_ia, suelo, ventana, parcela_info):
    """
    Ajusta el plan de la IA al formato del motor de reglas.

    La ventana de aplicación y la lectura del suelo se calculan siempre con
    reglas deterministas: son aritmética sobre los milímetros de lluvia y los
    valores del sensor, así que no tiene sentido dejarlas al criterio del modelo.
    """
    plan = dict(plan_ia)
    plan["suelo"] = suelo
    plan["ventanaAplicacion"] = ventana
    plan["parcelaInfo"] = parcela_info
    plan.setdefault("fertilizantes", [])
    plan.setdefault("advertencias", [])
    plan.setdefault("resumen", "")
    return plan


def generar(parcela_id, user_id, forzar_reglas=False):
    parcela = find_parcela(parcela_id, user_id)
    if not parcela:
        return None, PARCELA_NO_ENCONTRADA

    muestra = _ultima_muestra_con_suelo(parcela_id, user_id)
    if not muestra:
        return None, (
            "Esta parcela todavía no tiene muestras registradas. "
            "Registra una muestra con datos de suelo para generar el plan de fertilización."
        )

    ubicacion = parcela.get("ubicacion") or {}
    clima, error_clima = obtener_pronostico(ubicacion.get("lat"), ubicacion.get("lng"))
    if error_clima:
        logger.info("Plan de fertilización sin datos de clima: %s", error_clima)

    # El plan por reglas se calcula siempre: sirve de resultado final o de respaldo.
    plan_reglas = generar_plan_reglas(parcela, muestra, clima)
    suelo = plan_reglas["suelo"]
    ventana = plan_reglas["ventanaAplicacion"]

    plan = plan_reglas
    fuente = "reglas"
    modelo = ""

    if not forzar_reglas:
        plan_ia, error_ia, modelo_ia = generar_plan_ia(parcela, muestra, suelo, clima)
        if plan_ia:
            plan = _normalizar_plan_ia(plan_ia, suelo, ventana, plan_reglas["parcelaInfo"])
            fuente = "ia"
            modelo = modelo_ia
        else:
            logger.info("IA no disponible (%s); se usa el plan por reglas.", error_ia)

    doc = build_plan_fertilizacion(parcela, muestra, plan, clima, fuente, modelo)
    plan_id = repo.create(doc)

    doc["muestraUsada"] = {
        "id": str(muestra["_id"]),
        "fecha": muestra.get("createdAt"),
    }
    doc["parcela"] = {
        "id": parcela_id,
        "nombre": parcela.get("nombre", ""),
        "cultivo": parcela.get("cultivo", ""),
    }
    if error_clima:
        doc["avisoClima"] = error_clima

    resultado = serialize_doc(doc)
    resultado["id"] = plan_id
    return resultado, None


def obtener_ultimo(parcela_id, user_id):
    parcela = find_parcela(parcela_id, user_id)
    if not parcela:
        return None, PARCELA_NO_ENCONTRADA

    doc = repo.find_ultimo_por_parcela(parcela_id, user_id)
    if not doc:
        return {"plan": None}, None

    resultado = serialize_doc(doc)
    resultado["parcela"] = {
        "id": parcela_id,
        "nombre": parcela.get("nombre", ""),
        "cultivo": parcela.get("cultivo", ""),
    }
    return resultado, None


def listar_historial(parcela_id, user_id):
    parcela = find_parcela(parcela_id, user_id)
    if not parcela:
        return None, PARCELA_NO_ENCONTRADA

    docs = repo.find_all_by_parcela(parcela_id, user_id)
    return [serialize_doc(d) for d in docs], None


def obtener_plan(plan_id):
    doc = repo.find_by_id(plan_id)
    if not doc:
        return None, "Plan de fertilización no encontrado"
    return serialize_doc(doc), None


def previsualizar(parcela_id, user_id):
    """
    Lectura rápida del suelo y la ventana climática, sin llamar a la IA ni guardar
    nada. Sirve para pintar la pantalla al entrar, antes de generar el plan.
    """
    parcela = find_parcela(parcela_id, user_id)
    if not parcela:
        return None, PARCELA_NO_ENCONTRADA

    muestra = _ultima_muestra_con_suelo(parcela_id, user_id)
    ubicacion = parcela.get("ubicacion") or {}
    clima, _ = obtener_pronostico(ubicacion.get("lat"), ubicacion.get("lng"))

    sensor = (muestra or {}).get("datosSensor") or {}
    return {
        "parcela": {
            "id": parcela_id,
            "nombre": parcela.get("nombre", ""),
            "cultivo": parcela.get("cultivo", ""),
        },
        "tieneMuestra": muestra is not None,
        "muestraUsada": (
            {"id": str(muestra["_id"]), "fecha": muestra.get("createdAt")} if muestra else None
        ),
        "suelo": interpretar_suelo(sensor),
        "clima": clima,
        "ventanaAplicacion": evaluar_ventana_aplicacion(clima),
    }, None
