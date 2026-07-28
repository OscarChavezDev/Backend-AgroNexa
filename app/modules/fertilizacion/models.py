from app.utils.helpers import now_utc


def build_plan_fertilizacion(parcela, muestra, plan, clima, fuente, modelo_ia=""):
    """
    Documento que se guarda en la colección `fertilizacion`.

    `plan` tiene la misma forma venga de la IA o del motor de reglas, para que la
    UI lo renderice igual sin preguntar de dónde salió.
    """
    ahora = now_utc()
    ventana = plan.get("ventanaAplicacion") or {}

    return {
        "parcelaId": parcela["_id"],
        "muestraId": (muestra or {}).get("_id"),
        "userId": parcela.get("userId"),
        "plan": plan,
        "clima": clima,
        "resumen": plan.get("resumen", ""),
        "aptoParaAplicar": ventana.get("apto"),
        "estadoVentana": ventana.get("estado", ""),
        "fuente": fuente,                 # "ia" | "reglas"
        "modelo_ia": modelo_ia or None,
        "estado": "completado",
        "fecha_generacion": ahora,
        "createdAt": ahora,
        "updatedAt": ahora,
    }
