import logging

import requests as http_requests

logger = logging.getLogger(__name__)

# Open-Meteo es gratuito y no requiere API key ni registro.
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# Códigos WMO devueltos por Open-Meteo, traducidos a texto legible.
CODIGOS_CLIMA = {
    0: "Despejado",
    1: "Mayormente despejado",
    2: "Parcialmente nublado",
    3: "Nublado",
    45: "Neblina",
    48: "Neblina con escarcha",
    51: "Llovizna ligera",
    53: "Llovizna moderada",
    55: "Llovizna intensa",
    56: "Llovizna helada ligera",
    57: "Llovizna helada intensa",
    61: "Lluvia ligera",
    63: "Lluvia moderada",
    65: "Lluvia fuerte",
    66: "Lluvia helada ligera",
    67: "Lluvia helada fuerte",
    71: "Nevada ligera",
    73: "Nevada moderada",
    75: "Nevada fuerte",
    77: "Granizo fino",
    80: "Chubascos ligeros",
    81: "Chubascos moderados",
    82: "Chubascos violentos",
    85: "Chubascos de nieve ligeros",
    86: "Chubascos de nieve fuertes",
    95: "Tormenta eléctrica",
    96: "Tormenta con granizo ligero",
    99: "Tormenta con granizo fuerte",
}


def describir_codigo(codigo):
    return CODIGOS_CLIMA.get(codigo, "Sin datos")


def _dia(diario, i):
    def val(clave, defecto=None):
        serie = diario.get(clave) or []
        return serie[i] if i < len(serie) else defecto

    codigo = val("weather_code")
    return {
        "fecha": val("time"),
        "tempMax": val("temperature_2m_max"),
        "tempMin": val("temperature_2m_min"),
        "precipitacionMm": val("precipitation_sum") or 0,
        "probabilidadLluvia": val("precipitation_probability_max") or 0,
        "vientoMax": val("wind_speed_10m_max"),
        "codigo": codigo,
        "descripcion": describir_codigo(codigo),
    }


def obtener_pronostico(lat, lng, dias=7):
    """
    Consulta Open-Meteo y devuelve (clima, error).

    clima = {
        "actual": {...},
        "pronostico": [ {...} x dias ],
        "lluvia72hMm": float,     # acumulado próximas 72 h
        "lluvia7diasMm": float,
    }
    """
    try:
        lat = float(lat)
        lng = float(lng)
    except (TypeError, ValueError):
        return None, "La parcela no tiene coordenadas válidas"

    params = {
        "latitude": lat,
        "longitude": lng,
        "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m",
        "daily": (
            "weather_code,temperature_2m_max,temperature_2m_min,"
            "precipitation_sum,precipitation_probability_max,wind_speed_10m_max"
        ),
        "timezone": "auto",
        "forecast_days": dias,
    }

    try:
        resp = http_requests.get(OPEN_METEO_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.warning("No se pudo consultar Open-Meteo: %s", e)
        return None, "No se pudo obtener el clima en este momento."

    actual = data.get("current") or {}
    diario = data.get("daily") or {}
    fechas = diario.get("time") or []

    pronostico = [_dia(diario, i) for i in range(len(fechas))]
    lluvia_72h = sum(d["precipitacionMm"] or 0 for d in pronostico[:3])
    lluvia_7d = sum(d["precipitacionMm"] or 0 for d in pronostico)

    codigo_actual = actual.get("weather_code")
    clima = {
        "actual": {
            "temperatura": actual.get("temperature_2m"),
            "humedadRelativa": actual.get("relative_humidity_2m"),
            "precipitacionMm": actual.get("precipitation"),
            "viento": actual.get("wind_speed_10m"),
            "codigo": codigo_actual,
            "descripcion": describir_codigo(codigo_actual),
        },
        "pronostico": pronostico,
        "lluvia72hMm": round(lluvia_72h, 1),
        "lluvia7diasMm": round(lluvia_7d, 1),
        "zonaHoraria": data.get("timezone"),
        "coordenadas": {"lat": lat, "lng": lng},
    }
    return clima, None
