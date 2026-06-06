import logging
from app.modules.diagnostico.ai_service import analizar_con_gemini
from app.modules.diagnostico.models import build_diagnostico_ia
from app.modules.diagnostico import repository as repo
from app.modules.muestras.repository import find_by_id_and_user, update as update_muestra
from app.modules.imagenes.repository import find_by_muestra as find_imagenes
from app.modules.parcelas.repository import find_by_id as find_parcela_by_id
from app.utils.helpers import serialize_doc

logger = logging.getLogger(__name__)


def _nombre_parcela(parcela_id):
    try:
        parcela = find_parcela_by_id(str(parcela_id))
        return (parcela or {}).get("nombre", "")
    except Exception:
        return ""


def _ejecutar_analisis(muestra, muestra_id, user_id):
    imagenes = find_imagenes(muestra_id)
    img_list = [{"url": img.get("url")} for img in imagenes]
    parcela_nombre = _nombre_parcela(muestra.get("parcelaId"))

    resultado_json, error, modelo = analizar_con_gemini(muestra, img_list, parcela_nombre)

    # Fallback: si Gemini falla por cuota o por cualquier error, usa diagnóstico por reglas
    _error_lower = (error or "").lower()
    _es_cuota = any(k in _error_lower for k in ("límite", "limite", "quota", "cuota", "rate", "429", "exceeded"))
    if error:
        logger.info("Gemini no disponible, usando diagnóstico por reglas como fallback.")
        from app.modules.diagnostico.rules import generar_diagnostico as reglas_diagnostico
        datos_reglas = reglas_diagnostico(muestra)
        resultado_json = _convertir_reglas_a_gemini(datos_reglas)
        error = None
        modelo = "reglas-locales"

    doc = build_diagnostico_ia(muestra, resultado_json, error, modelo)
    diagnostico_id = repo.create(doc)

    if not error:
        update_muestra(muestra_id, user_id, {"estado": "diagnosticado"})

    result = serialize_doc(doc)
    result["id"] = diagnostico_id
    return result, None


def _convertir_reglas_a_gemini(datos_reglas):
    """Convierte el resultado del sistema de reglas al formato JSON de Gemini."""
    resultado = datos_reglas.get("resultado") or {}
    enfermedad = resultado.get("enfermedad", "no determinado")
    confianza_num = resultado.get("confianza", 0.4)
    riesgo = resultado.get("riesgo", "bajo")
    recomendaciones = datos_reglas.get("recomendaciones") or []

    confianza_str = "alta" if confianza_num >= 0.75 else ("media" if confianza_num >= 0.55 else "baja")
    severidad_nivel = "severo" if riesgo == "alto" else ("moderado" if riesgo == "moderado" else "leve")

    return {
        "diagnostico_principal": {
            "enfermedad": enfermedad.replace("_", " ").title(),
            "nombre_cientifico": "",
            "confianza": confianza_str,
            "descripcion": datos_reglas.get("motivo", "Diagnóstico basado en síntomas y datos del sensor."),
        },
        "diagnosticos_diferenciales": [],
        "severidad": {
            "nivel": severidad_nivel,
            "porcentaje_afectacion": "estimación no disponible",
            "etapa": "inicial",
        },
        "sintomas_detectados": [],
        "factores_riesgo": [],
        "recomendaciones": {
            "acciones_inmediatas": recomendaciones[:3] if recomendaciones else [],
            "tratamiento": recomendaciones[3:] if len(recomendaciones) > 3 else [],
            "prevencion": [],
            "monitoreo": "Revisa la parcela cada 7 días y registra nuevas muestras si los síntomas persisten.",
        },
        "requiere_asistencia_tecnica": riesgo == "alto",
        "notas_adicionales": "Diagnóstico generado localmente por sistema de reglas. Para mayor precisión, configure Gemini API.",
    }


def generar(muestra_id, user_id):
    muestra = find_by_id_and_user(muestra_id, user_id)
    if not muestra:
        return None, "Muestra no encontrada"

    existente = repo.find_by_muestra(muestra_id)
    if existente and (existente.get("estado") or "") == "completado":
        return None, "Esta muestra ya tiene un diagnóstico. Usa 'regenerar' para obtener uno nuevo."

    # Si hay un diagnóstico en error, eliminarlo y volver a intentar
    if existente:
        repo.delete_by_muestra(muestra_id)

    return _ejecutar_analisis(muestra, muestra_id, user_id)


def regenerar(muestra_id, user_id):
    muestra = find_by_id_and_user(muestra_id, user_id)
    if not muestra:
        return None, "Muestra no encontrada"

    repo.delete_by_muestra(muestra_id)
    return _ejecutar_analisis(muestra, muestra_id, user_id)


def get_diagnostico(diagnostico_id):
    doc = repo.find_by_id(diagnostico_id)
    if not doc:
        return None, "Diagnóstico no encontrado"
    return serialize_doc(doc), None


def get_diagnostico_by_muestra(muestra_id, user_id):
    muestra = find_by_id_and_user(muestra_id, user_id)
    if not muestra:
        return None, "Muestra no encontrada"

    doc = repo.find_by_muestra(muestra_id)
    if not doc:
        return {"diagnostico": None}, None
    return serialize_doc(doc), None
