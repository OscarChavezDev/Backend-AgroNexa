import os
import logging
import base64

import requests as http_requests
from groq import Groq

from app.utils.groq_utils import GROQ_MODEL_DEFAULT, opciones_razonamiento, extraer_json

logger = logging.getLogger(__name__)

GROQ_VISION_MODEL_DEFAULT = GROQ_MODEL_DEFAULT

# ── Pasada 1: observación visual pura (el modelo solo MIRA, no diagnostica) ──────
PROMPT_OBSERVACION = """Eres un fitopatólogo experto en cacao (Theobroma cacao). Observa la imagen con el MÁXIMO detalle y describe ÚNICAMENTE lo que ves. NO diagnostiques todavía, NO nombres enfermedades: solo describe signos visuales.

IDIOMA (OBLIGATORIO): escribe toda la observación en español.

Reporta de forma estructurada y concreta:
1. PARTE DE LA PLANTA: ¿fruto/mazorca, hoja, tallo, brote, flor, raíz? ¿cuántos elementos y en qué estado?
2. FORMA (CRÍTICO): ¿la forma es NORMAL (mazorca lisa, ovalada/alargada, simétrica; hoja entera y plana) o hay ANOMALÍAS? Busca y nombra explícitamente si los ves: deformaciones, gibas o jorobas, hinchazones, estrangulamientos, acostillado/surcos anormales, forma de "fresa", "zanahoria" o "chirimoya", asimetría, frutos pequeños o atrofiados, brotes engrosados, proliferación de ramas ("escobas"), hojas rizadas o deformadas. Di claramente cuando algo NO tiene la forma normal del cacao.
3. COLOR: colores presentes y sus variaciones; zonas decoloradas, oscurecidas, amarillentas o necróticas.
4. SUPERFICIE Y TEXTURA: lisa, rugosa, presencia de polvo blanco/crema, moho, costras, lesiones acuosas o aceitosas, brillo anormal.
5. MANCHAS Y LESIONES: color, borde, tamaño, distribución y si parecen avanzar.
6. OTROS SIGNOS: perforaciones, pudrición, marchitez, secamiento, presencia de insectos, telarañas o cuerpos de hongo.
7. CALIDAD DE IMAGEN: ¿nítida o borrosa? ¿se distingue bien la lesión?

REGLA: cualquier desviación de la forma y color normales del cacao es relevante, AUNQUE no sepas la causa. Nunca digas "está sano" en esta fase: solo describe lo observado. Sé conciso pero completo (máximo 220 palabras)."""


# ── Pasada 2: diagnóstico estructurado a partir de la observación + la imagen ─────
PROMPT_SISTEMA = """Eres un experto fitopatólogo especializado en cultivos de cacao (Theobroma cacao).

IDIOMA (OBLIGATORIO): responde ÍNTEGRAMENTE en español. Todos los valores de texto del JSON —enfermedad, descripción, razones, síntomas, factores de riesgo, recomendaciones, monitoreo y notas— deben estar en español. Solo el nombre científico va en latín. NINGÚN valor de texto puede estar en inglés.

REGLA FUNDAMENTAL DEL DIAGNÓSTICO:
- El diagnóstico debe basarse PRINCIPALMENTE en la OBSERVACIÓN VISUAL que aparece abajo: es el registro de lo que tú mismo viste al examinar la foto en detalle.
- Los "síntomas reportados" por el usuario son SOLO una referencia de contexto. NO determines la enfermedad basándote en ellos. Pueden estar incompletos, ser imprecisos o estar vacíos ("Sin síntoma visible").
- Si la observación visual contradice los síntomas reportados, prioriza SIEMPRE la observación visual.
- En "sintomas_detectados" lista únicamente los signos que aparecen en la observación visual, no los que reportó el usuario.

OBSERVACIÓN VISUAL (tu propio examen de la foto; es la evidencia principal):
{observacion_visual}

REGLA ANTI-FALSO-NEGATIVO (MUY IMPORTANTE):
- Una mazorca de cacao SANA es lisa, ovalada o alargada, simétrica y de color uniforme. Una hoja sana es entera, plana y verde uniforme.
- Si observas CUALQUIER deformación (gibas, jorobas, hinchazones, estrangulamientos, acostillado o surcos anormales, forma de "fresa"/"zanahoria"/"chirimoya", asimetría marcada, frutos atrofiados, brotes engrosados o proliferación de ramas), el cultivo NO está sano: hay un problema. NO lo clasifiques como "ninguna enfermedad visible".
- Las DEFORMACIONES de la mazorca y los brotes engrosados con proliferación de ramas son signos típicos de ESCOBA DE BRUJA (Moniliophthora perniciosa). Considérala SIEMPRE como candidata principal o diferencial cuando veas deformación, aunque no haya manchas ni polvo.
- Solo declara "ninguna enfermedad visible" cuando la superficie sea uniforme, la forma sea normal Y no haya manchas, deformaciones ni decoloraciones. Si dudas, NO declares sano: asigna la enfermedad más probable con la confianza que corresponda.

DATOS DE CONTEXTO (referencia, no decisivos):
- Parte afectada: {parte_afectada}
- Observaciones del usuario: {observaciones}
- Síntomas reportados por el usuario (solo referencia): {sintomas}
- Nivel de afectación indicado: {nivel_afectacion}
- Datos del suelo: pH={ph}, Humedad={humedad}%, Temperatura={temperatura}°C, N={nitrogeno} ppm, P={fosforo} ppm, K={potasio} ppm, CE={conductividad} dS/m
- Fecha: {fecha}
- Parcela: {nombre_parcela}

Enfermedades y problemas del cacao a considerar (con sus signos visuales típicos y lo que los DIFERENCIA):
- Escoba de bruja (Moniliophthora perniciosa): DEFORMACIÓN es la clave. En brotes/tallos: engrosamiento y proliferación de muchas ramas delgadas ("escoba"). En mazorca: frutos DEFORMES, asimétricos, con gibas o forma de "zanahoria"/"fresa"/"chirimoya", a menudo pequeños o atrofiados. Puede NO haber manchas ni polvo: la deformación por sí sola ya la sugiere. → Sospéchala SIEMPRE ante mazorcas o brotes deformados.
- Moniliasis / Monilia (Moniliophthora roreri): manchas marrones aceitosas en la mazorca + gibas/abultamientos, y sobre todo POLVO blanco-crema (esporulación) cubriendo la lesión. La diferencia con escoba de bruja: aquí domina el polvo blanco y la mancha aceitosa; en escoba domina la deformación de la forma sin polvo.
- Mazorca negra / Pudrición parda (Phytophthora spp.): manchas pardas/negras que avanzan rápido y uniformes sobre la mazorca, a veces moho blanco fino. La diferencia con monilia: la lesión es oscura y uniforme SIN gibas ni polvo blanco-crema abundante; la forma del fruto se mantiene (no se deforma).
- Mal del machete (Ceratocystis cacaofunesta): marchitez súbita del árbol, pardeamiento interno de la madera del tallo.
- Antracnosis (Colletotrichum spp.): manchas necróticas marrones con halo en hojas y frutos, defoliación, muerte de puntas.
- Deficiencias nutricionales: clorosis (amarillamiento) entre nervaduras, bordes quemados, patrones según el nutriente (N, K, Mg). No deforma la mazorca.
- Plagas (ácaros, trips, barrenadores, mosquilla/monalonion): punteaduras, raspaduras plateadas, perforaciones, manchas hundidas.
- Daño físico/abiótico: quemadura solar, heridas mecánicas, exceso/falta de agua (no es enfermedad). No produce proliferación de ramas ni polvo de hongo.

PROCESO DE ANÁLISIS (hazlo internamente, con calma y rigor, antes de responder):
1. Describe minuciosamente lo que ves en la imagen: parte de la planta, color, textura, forma, lesiones, manchas (color, borde, tamaño, distribución), presencia de hongos/polvo/moho, deformaciones, perforaciones.
2. Compara esos signos visuales contra la lista de enfermedades de arriba.
3. Asigna una probabilidad a CADA enfermedad candidata según qué tanto coinciden los signos observados. Las probabilidades de todas las candidatas (principal + diferenciales) deben sumar aproximadamente 100%.
4. La enfermedad con mayor probabilidad es el diagnóstico_principal; las demás van en diagnosticos_diferenciales ordenadas de mayor a menor probabilidad.
5. Si los signos no son claros o la planta luce sana, dilo honestamente con confianza "baja" o "media" — no inventes una enfermedad.

RESPONDE SOLO con JSON válido, sin texto extra, sin markdown:

{{
  "diagnostico_principal": {{
    "enfermedad": "nombre de la enfermedad más probable",
    "nombre_cientifico": "nombre científico o vacío",
    "probabilidad": "porcentaje estimado, ej: 65%",
    "confianza": "alta",
    "descripcion": "explicación basada en los signos VISIBLES en la imagen (qué viste y por qué apunta a esta enfermedad)"
  }},
  "diagnosticos_diferenciales": [
    {{"enfermedad": "segunda más probable", "probabilidad": "25%", "razon": "qué signo la sugiere y qué la diferencia de la principal"}},
    {{"enfermedad": "tercera opción", "probabilidad": "10%", "razon": "motivo basado en lo observado"}}
  ],
  "severidad": {{
    "nivel": "leve",
    "porcentaje_afectacion": "estimado del área",
    "etapa": "inicial"
  }},
  "sintomas_detectados": ["síntoma 1", "síntoma 2"],
  "factores_riesgo": ["factor 1"],
  "recomendaciones": {{
    "acciones_inmediatas": [
      "Acción concreta y urgente relacionada directamente con los síntomas detectados (ej: 'Retirar y quemar los frutos con manchas oscuras para evitar la dispersión de esporas')"
    ],
    "tratamiento": [
      "Producto o método específico con dosis o frecuencia (ej: 'Aplicar fungicida a base de cobre, 2-3 g/L, cada 15 días durante 2 meses')"
    ],
    "prevencion": [
      "Medida preventiva específica para la enfermedad detectada y las condiciones del suelo observadas"
    ],
    "monitoreo": "Indicar exactamente qué síntoma vigilar, con qué frecuencia y en qué parte de la planta, basado en la enfermedad diagnosticada"
  }},
  "requiere_asistencia_tecnica": false,
  "notas_adicionales": "Mencionar si el pH, humedad u otros datos del sensor favorecen o agravan la condición detectada"
}}

IMPORTANTE para las recomendaciones:
- Si no hay enfermedad: dar recomendaciones de mantenimiento preventivo específicas para el cacao saludable.
- Si hay enfermedad: cada recomendación debe mencionar el nombre de la enfermedad o síntoma específico encontrado.
- Monitoreo: nunca ser genérico — indicar parte de la planta, frecuencia exacta, síntoma puntual a vigilar.
- Tratamiento: incluir nombre del producto activo cuando sea posible.

REGLAS DE LOS DIFERENCIALES:
- Incluye SIEMPRE entre 2 y 4 diagnósticos diferenciales con su probabilidad en porcentaje, ordenados de mayor a menor.
- Las probabilidades de (principal + diferenciales) deben sumar aproximadamente 100%.
- Cada "razon" debe basarse en lo observado en la imagen, no en suposiciones.
- Si la planta luce sana, el diagnóstico_principal es "ninguna enfermedad visible" con alta probabilidad, y los diferenciales pueden listar enfermedades a vigilar con baja probabilidad.

RECORDATORIO FINAL: tu diagnóstico se decide por la OBSERVACIÓN VISUAL, no por los síntomas que reportó el usuario. Si la observación describe una planta sana, diagnostica "ninguna enfermedad visible" aunque el usuario haya marcado síntomas. La confianza debe reflejar qué tan claros son los signos descritos en la observación.

Valores exactos — confianza: "alta", "media" o "baja".
Severidad nivel: "leve", "moderado", "severo" o "crítico".
Severidad etapa: "inicial", "intermedia" o "avanzada".

RECORDATORIO DE IDIOMA: todo el contenido de texto del JSON debe estar en ESPAÑOL, salvo el nombre científico."""


# Lado máximo de la imagen que se envía al modelo.
#
# El tier gratuito de Groq limita a 8000 tokens por minuto y una foto a
# resolución completa consume varios miles ella sola: la petición supera el
# límite y falla con 413 sin importar cuánto se espere. A 768 px el modelo
# distingue igual manchas, polvo blanco y deformaciones.
LADO_MAX_IMAGEN = 640


def _url_reducida(url):
    """
    Pide a Cloudinary una versión reducida insertando la transformación en la URL.

    Se resuelve en el CDN, así que no hace falta procesar la imagen aquí ni
    añadir dependencias. Si la URL no es de Cloudinary se devuelve tal cual.
    """
    marca = "/image/upload/"
    if marca not in url:
        return url
    antes, despues = url.split(marca, 1)
    return f"{antes}{marca}c_limit,w_{LADO_MAX_IMAGEN},q_auto:good/{despues}"


def _descargar_imagen(url):
    try:
        resp = http_requests.get(_url_reducida(url), timeout=15)
        resp.raise_for_status()
        mime = resp.headers.get("Content-Type", "image/jpeg").split(";")[0].strip()
        logger.info("Imagen para IA: %d KB", len(resp.content) // 1024)
        return resp.content, mime
    except Exception as e:
        logger.warning("No se pudo descargar imagen: %s", e)
        return None, None


# Se mantiene el nombre por compatibilidad con quien ya lo importaba.
_extraer_json = extraer_json


def _mensaje_amigable(exc):
    txt = str(exc).lower()
    if "429" in txt or "rate" in txt or "quota" in txt or "limit" in txt:
        return "Límite de uso de la IA alcanzado. Espera un momento e intenta de nuevo."
    if "401" in txt or "403" in txt or "auth" in txt or "invalid" in txt:
        return "API key de IA inválida. Verifica GROQ_API_KEY en el archivo .env."
    if "timeout" in txt:
        return "La IA tardó demasiado. Intenta de nuevo."
    return "No se pudo conectar con la IA. Intenta de nuevo en unos momentos."


def _bloque_imagen(img_b64, mime_type):
    return {
        "type": "image_url",
        "image_url": {"url": f"data:{mime_type or 'image/jpeg'};base64,{img_b64}"},
    }


def _observar_imagen(client, model_name, img_b64, mime_type):
    """Pasada 1: el modelo describe lo que ve en la imagen, sin diagnosticar."""
    try:
        content = [
            {"type": "text", "text": PROMPT_OBSERVACION},
            _bloque_imagen(img_b64, mime_type),
        ]
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": content}],
            temperature=0.2,
            max_tokens=500,
            top_p=0.9,
            **opciones_razonamiento(model_name),
        )
        observacion = (response.choices[0].message.content or "").strip()
        logger.info("Observación visual (pasada 1) completada: %d caracteres", len(observacion))
        return observacion
    except Exception as e:
        # Si la pasada 1 falla, el diagnóstico continúa sin observación previa.
        logger.warning("Pasada de observación visual falló, se continúa sin ella: %s", e)
        return ""


def analizar_con_gemini(muestra, imagenes, parcela_nombre=""):
    """
    Llama a Groq (Llama 4 con visión) en DOS pasadas:
      1. Observación visual pura (el modelo describe lo que ve, sin diagnosticar).
      2. Diagnóstico estructurado a partir de esa observación + la imagen.
    Retorna (resultado_json, mensaje_error, modelo_usado).
    """
    api_key = os.getenv("GROQ_API_KEY", "")
    # Se puede sobrescribir con GROQ_VISION_MODEL en el .env, pero debe ser un
    # modelo con visión: si no analiza la imagen, el diagnóstico pierde su base.
    model_name = os.getenv("GROQ_VISION_MODEL", GROQ_VISION_MODEL_DEFAULT)

    if not api_key:
        return None, "GROQ_API_KEY no configurada en el archivo .env", ""

    try:
        datos_sensor = muestra.get("datosSensor") or {}
        sintomas = muestra.get("sintomas") or []

        client = Groq(api_key=api_key)

        # Descargar la imagen una sola vez (se reutiliza en ambas pasadas).
        img_b64, mime_type = None, None
        if imagenes:
            img_url = (imagenes[0] or {}).get("url")
            if img_url:
                img_bytes, mime_type = _descargar_imagen(img_url)
                if img_bytes:
                    img_b64 = base64.b64encode(img_bytes).decode("utf-8")

        # ── Pasada 1: observación visual ────────────────────────────────────────
        observacion_visual = ""
        if img_b64:
            observacion_visual = _observar_imagen(client, model_name, img_b64, mime_type)

        # ── Pasada 2: diagnóstico estructurado ──────────────────────────────────
        prompt = PROMPT_SISTEMA.format(
            observacion_visual=observacion_visual or "No disponible (analiza la imagen directamente).",
            parte_afectada=muestra.get("parteAfectada") or "no especificado",
            observaciones=muestra.get("observaciones") or "ninguna",
            sintomas=", ".join(sintomas) if sintomas else "ninguno reportado",
            nivel_afectacion=muestra.get("nivelAfectacion") or "no especificado",
            ph=datos_sensor.get("ph", "N/D"),
            humedad=datos_sensor.get("humedadSuelo", "N/D"),
            temperatura=datos_sensor.get("temperaturaSuelo", "N/D"),
            nitrogeno=datos_sensor.get("nitrogeno", "N/D"),
            fosforo=datos_sensor.get("fosforo", "N/D"),
            potasio=datos_sensor.get("potasio", "N/D"),
            conductividad=datos_sensor.get("conductividadElectrica", "N/D"),
            fecha=str(muestra.get("createdAt", "no especificada")),
            nombre_parcela=parcela_nombre or "no especificada",
        )

        # La imagen ya se analizó en la pasada 1 y su resultado viaja como texto
        # dentro del prompt. Reenviarla aquí duplicaría el costo en tokens y la
        # petición superaría el límite por minuto, que es lo que hacía fallar el
        # diagnóstico con 413. Solo se adjunta si no hubo observación previa.
        content = [{"type": "text", "text": prompt}]
        if img_b64 and not observacion_visual:
            content.append(_bloque_imagen(img_b64, mime_type))

        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": content}],
            temperature=0.1,           # análisis más determinista y riguroso
            # max_tokens cuenta contra el límite de tokens por minuto, no solo
            # la entrada. Con 3000 la petición completa superaba los 8000 del
            # tier gratuito y Groq la rechazaba con 413 antes de procesarla.
            max_tokens=1600,
            top_p=0.9,
            **opciones_razonamiento(model_name),
        )

        texto = response.choices[0].message.content.strip()
        resultado = _extraer_json(texto)

        if resultado is None:
            logger.warning("Respuesta de IA no es JSON válido: %s", texto[:200])
            return None, "La IA no devolvió un formato válido. Intenta de nuevo.", model_name

        logger.info("Groq respondió correctamente con modelo %s", model_name)
        return resultado, None, model_name

    except Exception as e:
        logger.error("Error en Groq: %s", e)
        return None, _mensaje_amigable(e), ""
