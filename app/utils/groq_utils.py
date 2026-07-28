"""
Utilidades comunes para las llamadas a Groq.

Los modelos actuales (Qwen 3.6, GPT-OSS) razonan antes de responder y, por
defecto, devuelven ese razonamiento junto al resultado. Para un JSON estructurado
eso es ruido que rompe el parseo, así que aquí se centraliza cómo silenciarlo.
"""

import json
import re

# Modelo con visión y modo JSON. Groq dio de baja los Llama 4 (Maverick el
# 09/03/2026, Scout el 17/07/2026) y llama-3.3-70b-versatile el 17/06/2026.
GROQ_MODEL_DEFAULT = "qwen/qwen3.6-27b"

_BLOQUE_THINK = re.compile(r"<think>[\s\S]*?</think>", re.IGNORECASE)


def opciones_razonamiento(model_name):
    """
    Parámetros para que el modelo devuelva solo la respuesta final.

    Ojo con la diferencia entre ocultar y desactivar: con `reasoning_format`
    "hidden" el modelo razona igual y esos tokens SÍ consumen el presupuesto de
    max_tokens, así que en respuestas largas se agota pensando y devuelve
    contenido vacío. Qwen 3.6 admite apagar el razonamiento del todo, que es lo
    que necesitamos para obtener JSON completo.
    """
    nombre = model_name or ""

    if nombre.startswith("openai/gpt-oss"):
        return {"include_reasoning": False}
    if nombre.startswith("qwen/"):
        return {"reasoning_effort": "none"}
    return {"reasoning_format": "hidden"}


def extraer_json(texto):
    """
    Obtiene el primer objeto JSON del texto devuelto por el modelo.

    Se descartan antes los bloques <think>…</think>: aunque se pida ocultarlos,
    un modelo puede colarlos y sus llaves confundirían la búsqueda del JSON.
    """
    if not texto:
        return None

    limpio = _BLOQUE_THINK.sub("", texto).strip()

    try:
        return json.loads(limpio)
    except json.JSONDecodeError:
        pass

    # Fallback: el modelo pudo envolver el JSON en texto o en ```json … ```
    match = re.search(r'\{[\s\S]*\}', limpio)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return None
