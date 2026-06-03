import os
import json
import logging
import base64
import re

import requests as http_requests
from groq import Groq

logger = logging.getLogger(__name__)

PROMPT_SISTEMA = """Eres un experto fitopatólogo especializado en cultivos de cacao (Theobroma cacao).
Analiza la imagen proporcionada junto con los datos de contexto y diagnostica posibles enfermedades.

DATOS DE LA MUESTRA:
- Parte afectada: {parte_afectada}
- Observaciones: {observaciones}
- Síntomas reportados: {sintomas}
- Nivel de afectación: {nivel_afectacion}
- Datos del suelo: pH={ph}, Humedad={humedad}%, Temperatura={temperatura}°C, N={nitrogeno} ppm, P={fosforo} ppm, K={potasio} ppm, CE={conductividad} dS/m
- Fecha: {fecha}
- Parcela: {nombre_parcela}

Enfermedades comunes del cacao a considerar:
- Moniliasis (Moniliophthora roreri)
- Mazorca negra (Phytophthora spp.)
- Escoba de bruja (Moniliophthora perniciosa)
- Mal del machete (Ceratocystis cacaofunesta)
- Antracnosis (Colletotrichum spp.)
- Deficiencias nutricionales
- Plagas (ácaros, trips, barrenadores)

RESPONDE SOLO con JSON válido, sin texto extra, sin markdown:

{{
  "diagnostico_principal": {{
    "enfermedad": "nombre de la enfermedad",
    "nombre_cientifico": "nombre científico o vacío",
    "confianza": "alta",
    "descripcion": "explicación breve"
  }},
  "diagnosticos_diferenciales": [
    {{"enfermedad": "otra enfermedad", "probabilidad": "25%", "razon": "motivo"}}
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

Valores exactos — confianza: "alta", "media" o "baja".
Severidad nivel: "leve", "moderado", "severo" o "crítico".
Severidad etapa: "inicial", "intermedia" o "avanzada"."""


def _descargar_imagen(url):
    try:
        resp = http_requests.get(url, timeout=15)
        resp.raise_for_status()
        mime = resp.headers.get("Content-Type", "image/jpeg").split(";")[0].strip()
        return resp.content, mime
    except Exception as e:
        logger.warning("No se pudo descargar imagen: %s", e)
        return None, None


def _extraer_json(texto):
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        pass
    match = re.search(r'\{[\s\S]*\}', texto)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return None


def _mensaje_amigable(exc):
    txt = str(exc).lower()
    if "429" in txt or "rate" in txt or "quota" in txt or "limit" in txt:
        return "Límite de uso de la IA alcanzado. Espera un momento e intenta de nuevo."
    if "401" in txt or "403" in txt or "auth" in txt or "invalid" in txt:
        return "API key de IA inválida. Verifica GROQ_API_KEY en el archivo .env."
    if "timeout" in txt:
        return "La IA tardó demasiado. Intenta de nuevo."
    return "No se pudo conectar con la IA. Intenta de nuevo en unos momentos."


def analizar_con_gemini(muestra, imagenes, parcela_nombre=""):
    """
    Llama a Groq (Llama 4 con visión) con la imagen y datos de la muestra.
    Retorna (resultado_json, mensaje_error, modelo_usado).
    """
    api_key = os.getenv("GROQ_API_KEY", "")
    model_name = os.getenv("GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")

    if not api_key:
        return None, "GROQ_API_KEY no configurada en el archivo .env", ""

    try:
        datos_sensor = muestra.get("datosSensor") or {}
        sintomas = muestra.get("sintomas") or []

        prompt = PROMPT_SISTEMA.format(
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

        # Construir mensaje con imagen si existe
        content = [{"type": "text", "text": prompt}]

        if imagenes:
            img_url = (imagenes[0] or {}).get("url")
            if img_url:
                img_bytes, mime_type = _descargar_imagen(img_url)
                if img_bytes:
                    img_b64 = base64.b64encode(img_bytes).decode("utf-8")
                    content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type or 'image/jpeg'};base64,{img_b64}"
                        }
                    })

        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": content}],
            temperature=0.2,
            max_tokens=2048,
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
