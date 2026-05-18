SINTOMAS_CRITICOS = {"polvo blanco", "fruto momificado", "manchas oscuras", "pudricion", "brotes deformados", "ramas anormales"}


def _match(sintomas, *keywords):
    s = {x.lower() for x in sintomas}
    return any(k in s for k in keywords)


def _evaluar_enfermedad(parte, sintomas, datos_suelo):
    humedad = (datos_suelo.get("humedad") or "").lower()

    if parte in ("fruto",) and _match(sintomas, "polvo blanco", "fruto momificado"):
        return "moniliasis", 0.85

    if parte in ("rama", "brote") and _match(sintomas, "brotes deformados", "ramas anormales"):
        return "escoba de bruja", 0.80

    if (
        parte in ("fruto",)
        and _match(sintomas, "manchas oscuras")
        and _match(sintomas, "pudricion")
        and humedad == "alta"
    ):
        return "pudricion parda", 0.78

    return "no determinado", 0.40


def _evaluar_riesgo(nivel_afectacion, datos_suelo, sintomas):
    humedad = (datos_suelo.get("humedad") or "").lower()
    criticos = {s.lower() for s in sintomas} & SINTOMAS_CRITICOS

    if nivel_afectacion == "severo" or humedad == "alta" or len(criticos) >= 2:
        return "alto"
    if nivel_afectacion == "moderado" or len(criticos) == 1:
        return "moderado"
    return "bajo"


RECOMENDACIONES = {
    "moniliasis": [
        "Retirar y destruir frutos afectados",
        "No dejar frutos enfermos en el suelo",
        "Realizar podas de mantenimiento",
        "Aplicar fungicida cúprico si el daño avanza",
        "Solicitar revisión técnica si el daño supera el 20% de la parcela",
    ],
    "escoba de bruja": [
        "Podar y quemar ramas afectadas",
        "Desinfectar herramientas de poda",
        "Evitar heridas innecesarias en el tallo",
        "Consultar con un técnico agrícola",
    ],
    "pudricion parda": [
        "Retirar frutos y tejidos afectados",
        "Mejorar el drenaje del suelo",
        "Reducir la sombra excesiva",
        "Aplicar fungicida sistémico bajo supervisión",
    ],
    "no determinado": [
        "Registrar más síntomas para mejorar el diagnóstico",
        "Tomar fotografías del área afectada",
        "Consultar con un técnico agrícola para revisión presencial",
    ],
}


def generar_diagnostico(muestra):
    parte = (muestra.get("parteAfectada") or "").lower()
    sintomas = muestra.get("sintomas") or []
    datos_suelo = muestra.get("datosSuelo") or {}
    nivel_afectacion = (muestra.get("nivelAfectacion") or "leve").lower()

    enfermedad, confianza = _evaluar_enfermedad(parte, sintomas, datos_suelo)
    riesgo = _evaluar_riesgo(nivel_afectacion, datos_suelo, sintomas)
    recomendaciones = RECOMENDACIONES.get(enfermedad, RECOMENDACIONES["no determinado"])

    motivo = (
        f"Análisis basado en parte afectada '{parte}', "
        f"síntomas registrados y datos del suelo."
    )

    return {
        "resultado": {
            "riesgo": riesgo,
            "enfermedad": enfermedad,
            "confianza": confianza,
        },
        "motivo": motivo,
        "recomendaciones": recomendaciones,
    }
