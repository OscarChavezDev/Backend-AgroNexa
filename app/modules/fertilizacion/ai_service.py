import os
import logging

from groq import Groq

from app.utils.groq_utils import GROQ_MODEL_DEFAULT, opciones_razonamiento, extraer_json

logger = logging.getLogger(__name__)

GROQ_TEXT_MODEL_DEFAULT = GROQ_MODEL_DEFAULT

PROMPT_FERTILIZACION = """Eres un ingeniero agrónomo especialista en nutrición y fertilización de cacao (Theobroma cacao) en Perú.

IDIOMA (OBLIGATORIO): responde ÍNTEGRAMENTE en español. Todos los textos del JSON —resumen, justificaciones, momentos, notas, advertencias y cronograma— deben estar en español de Perú, con la terminología agrícola que usa un productor cacaotero. Las claves del JSON van en inglés/español tal como se especifican abajo, pero NINGÚN valor de texto puede estar en inglés.

Debes elaborar un PLAN DE FERTILIZACIÓN concreto para una parcela real, usando los análisis de suelo y el pronóstico del clima que se te entregan.

DATOS DE LA PARCELA
- Nombre: {parcela_nombre}
- Cultivo: {cultivo}
- Variedad: {variedad}
- Edad del cultivo: {edad}
- Área: {area} {unidad_area}
- Cantidad de plantas: {plantas}
- Sistema de cultivo: {sistema}

ANÁLISIS DE SUELO (sensor)
- pH: {ph}
- Nitrógeno: {nitrogeno} ppm
- Fósforo: {fosforo} ppm
- Potasio: {potasio} ppm
- Humedad del suelo: {humedad} %
- Temperatura del suelo: {temperatura} °C
- Conductividad eléctrica: {conductividad} dS/m

INTERPRETACIÓN AGRONÓMICA YA CALCULADA (úsala como base, es confiable)
{interpretacion}

PRONÓSTICO DEL CLIMA (próximos días)
- Condición actual: {clima_actual}
- Lluvia acumulada próximas 72 h: {lluvia_72h} mm
- Lluvia acumulada próximos 7 días: {lluvia_7d} mm
- Detalle diario: {pronostico_detalle}

CRITERIOS OBLIGATORIOS
1. pH primero: si el pH está por debajo de 5.0, el fósforo se fija por aluminio/hierro. Encalar ANTES de aplicar fósforo, o el fertilizante se desperdicia.
2. El cacao es sensible al cloruro: prefiere sulfato de potasio sobre cloruro de potasio.
3. En suelo alcalino usa sulfato de amonio (acidifica); en suelo ácido prefiere urea.
4. En suelo ácido la roca fosfórica se solubiliza bien y es más barata que el superfosfato.
5. CLIMA (crítico): si se esperan más de 25 mm de lluvia en 72 h, NO se debe aplicar: el fertilizante se pierde por escorrentía y lixiviación. Si se esperan menos de 10 mm en 7 días, el granulado no se disuelve y la urea se volatiliza. La ventana ideal es lluvia suave de 5 a 25 mm.
6. Calcula dosis REALES: kg de producto comercial por hectárea, total para el área de la parcela, y gramos por planta cuando conozcas la cantidad de plantas. Usa las riquezas: urea 46% N, sulfato de amonio 21% N, superfosfato triple 46% P₂O₅, roca fosfórica 30% P₂O₅, sulfato de potasio 50% K₂O.
7. Cada justificación debe explicar el PORQUÉ agronómico en lenguaje entendible para un productor, mencionando el valor medido. Nada de frases genéricas.

RESPONDE SOLO con JSON válido, sin markdown ni texto adicional:

{{
  "resumen": "2 o 3 frases: qué le falta al suelo, qué se debe hacer primero y si el clima acompaña",
  "correccionPh": {{
    "producto": "Cal dolomita",
    "nutriente": "Ca + Mg",
    "dosisHa": "2 t/ha",
    "totalParcela": "5 t para 2.5 ha",
    "prioridad": "alta",
    "justificacion": "por qué, mencionando el pH medido",
    "momento": "cuándo aplicarlo respecto al NPK"
  }},
  "fertilizantes": [
    {{
      "producto": "Urea",
      "nutriente": "N",
      "dosisHa": "261 kg/ha",
      "nutrienteHa": "120 kg N/ha",
      "totalParcela": "652 kg para 2.5 ha",
      "dosisPlanta": "261 g por planta",
      "prioridad": "alta",
      "justificacion": "por qué esta dosis, citando el valor medido de nitrógeno",
      "momento": "cómo fraccionar la aplicación durante el año",
      "nota": "advertencia o razón de haber elegido este producto (opcional)"
    }}
  ],
  "materiaOrganica": {{
    "producto": "Compost o gallinaza descompuesta",
    "dosisHa": "3 – 5 t/ha",
    "totalParcela": "opcional",
    "justificacion": "por qué conviene en este suelo concreto",
    "momento": "cuándo aplicarla"
  }},
  "ventanaAplicacion": {{
    "apto": true,
    "estado": "ideal",
    "motivo": "explicación basada en los milímetros de lluvia pronosticados",
    "recomendacion": "qué hacer exactamente",
    "mejorDia": {{"fecha": "2026-08-02", "precipitacionMm": 8, "porque": "razón"}}
  }},
  "advertencias": ["riesgos concretos: salinidad, encharcamiento, datos faltantes"],
  "cronograma": [
    {{"momento": "Semana 1", "accion": "qué aplicar y cuánto"}},
    {{"momento": "Mes 3", "accion": "segunda fracción"}}
  ]
}}

Si el pH ya está entre 5.5 y 6.5, devuelve "correccionPh": null.
Valores exactos — prioridad: "alta", "media" o "baja". ventanaAplicacion.estado: "ideal", "aceptable", "lluvia_excesiva" o "muy_seco".

RECORDATORIO FINAL: todo el contenido de texto debe estar en ESPAÑOL. No uses palabras en inglés en ningún valor del JSON."""


def _mensaje_amigable(exc):
    txt = str(exc).lower()
    if "429" in txt or "rate" in txt or "quota" in txt or "limit" in txt:
        return "Límite de uso de la IA alcanzado."
    if "401" in txt or "403" in txt or "auth" in txt or "invalid" in txt:
        return "API key de IA inválida."
    if "timeout" in txt:
        return "La IA tardó demasiado."
    return "No se pudo conectar con la IA."


def _resumir_interpretacion(suelo):
    etiquetas = {
        "ph": "pH",
        "nitrogeno": "Nitrógeno",
        "fosforo": "Fósforo",
        "potasio": "Potasio",
        "conductividadElectrica": "Conductividad eléctrica",
        "humedadSuelo": "Humedad del suelo",
    }
    lineas = []
    for clave, etiqueta in etiquetas.items():
        dato = suelo.get(clave) or {}
        lineas.append(f"- {etiqueta}: {dato.get('valor', 'N/D')} → nivel {dato.get('estado', 'sin dato')}")
    return "\n".join(lineas)


def _resumir_pronostico(clima):
    if not clima:
        return "No disponible"
    dias = (clima.get("pronostico") or [])[:5]
    return "; ".join(
        f"{d.get('fecha')}: {d.get('precipitacionMm', 0)} mm, {d.get('descripcion', '')}"
        for d in dias
    ) or "No disponible"


def generar_plan_ia(parcela, muestra, suelo, clima):
    """
    Pide a Groq un plan de fertilización en el mismo formato que el motor de reglas.
    Retorna (plan_json, mensaje_error, modelo_usado).
    """
    api_key = os.getenv("GROQ_API_KEY", "")
    model_name = os.getenv("GROQ_MODEL_TEXTO", GROQ_TEXT_MODEL_DEFAULT)

    if not api_key:
        return None, "GROQ_API_KEY no configurada", ""

    try:
        sensor = (muestra or {}).get("datosSensor") or {}
        parcela = parcela or {}

        prompt = PROMPT_FERTILIZACION.format(
            parcela_nombre=parcela.get("nombre") or "no especificada",
            cultivo=parcela.get("cultivo") or "cacao",
            variedad=parcela.get("variedad") or "no especificada",
            edad=parcela.get("edadCultivo") or "no especificada",
            area=parcela.get("areaAproximada") or "no especificada",
            unidad_area=parcela.get("unidadArea") or "ha",
            plantas=parcela.get("cantidadPlantas") or "no especificada",
            sistema=parcela.get("sistemaCultivo") or "no especificado",
            ph=sensor.get("ph", "N/D"),
            nitrogeno=sensor.get("nitrogeno", "N/D"),
            fosforo=sensor.get("fosforo", "N/D"),
            potasio=sensor.get("potasio", "N/D"),
            humedad=sensor.get("humedadSuelo", "N/D"),
            temperatura=sensor.get("temperaturaSuelo", "N/D"),
            conductividad=sensor.get("conductividadElectrica", "N/D"),
            interpretacion=_resumir_interpretacion(suelo),
            clima_actual=(clima or {}).get("actual", {}).get("descripcion", "No disponible"),
            lluvia_72h=(clima or {}).get("lluvia72hMm", "N/D"),
            lluvia_7d=(clima or {}).get("lluvia7diasMm", "N/D"),
            pronostico_detalle=_resumir_pronostico(clima),
        )

        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=4000,
            top_p=0.9,
            **opciones_razonamiento(model_name),
        )

        texto = (response.choices[0].message.content or "").strip()
        plan = extraer_json(texto)

        if plan is None:
            logger.warning("Plan de fertilización de IA no es JSON válido: %s", texto[:200])
            return None, "La IA no devolvió un formato válido.", model_name

        logger.info("Plan de fertilización generado con %s", model_name)
        return plan, None, model_name

    except Exception as e:
        logger.error("Error generando plan de fertilización con Groq: %s", e)
        return None, _mensaje_amigable(e), ""
