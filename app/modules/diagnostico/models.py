from app.utils.helpers import now_utc


def build_diagnostico_ia(muestra, resultado_json, mensaje_error, modelo_ia="gemini-2.0-flash"):
    ahora = now_utc()
    estado = "completado" if resultado_json and not mensaje_error else "error"

    enfermedad_principal = ""
    confianza = ""
    severidad = ""
    recomendaciones_lista = []
    motivo = ""

    if resultado_json:
        dp = resultado_json.get("diagnostico_principal") or {}
        enfermedad_principal = dp.get("enfermedad") or ""
        confianza = dp.get("confianza") or ""
        severidad = (resultado_json.get("severidad") or {}).get("nivel") or ""
        motivo = dp.get("descripcion") or ""
        recs = resultado_json.get("recomendaciones") or {}
        if isinstance(recs, dict):
            recomendaciones_lista = (
                list(recs.get("acciones_inmediatas") or []) +
                list(recs.get("tratamiento") or [])
            )

    return {
        "muestraId": muestra["_id"],
        "parcelaId": muestra.get("parcelaId"),
        "userId": muestra.get("userId"),
        "resultado_json": resultado_json,
        "enfermedad_principal": enfermedad_principal,
        "confianza": confianza,
        "severidad": severidad,
        "estado": estado,
        "mensaje_error": mensaje_error if mensaje_error else None,
        "modelo_ia": modelo_ia or "gemini-2.0-flash",
        "fecha_analisis": ahora,
        "createdAt": ahora,
        "updatedAt": ahora,
        # Campos de compatibilidad con la UI antigua
        "resultado": {
            "enfermedad": enfermedad_principal,
            "confianza": confianza,
            "riesgo": severidad,
        },
        "motivo": motivo,
        "recomendaciones": recomendaciones_lista,
    }
