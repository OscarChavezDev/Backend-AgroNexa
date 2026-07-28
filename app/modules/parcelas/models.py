from app.utils.helpers import now_utc
from bson import ObjectId


def _es_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _punto(valor):
    """Normaliza un {lat, lng} suelto; devuelve None si no es un punto válido."""
    if not isinstance(valor, dict):
        return None
    lat = valor.get("lat")
    lng = valor.get("lng")
    if not _es_num(lat) or not _es_num(lng):
        return None
    return {"lat": float(lat), "lng": float(lng)}


def normalizar_nodos(nodos):
    """
    Nodos de muestreo dentro de la parcela.

    El id se asigna aquí y no en el cliente: es la referencia que guardan las
    muestras, así que debe ser estable aunque el usuario reordene o renombre.
    """
    if not isinstance(nodos, list):
        return []

    limpios = []
    for i, nodo in enumerate(nodos, start=1):
        if not isinstance(nodo, dict):
            continue
        punto = _punto(nodo)
        if not punto:
            continue

        nodo_id = str(nodo.get("id") or "").strip() or f"n{i}"
        limpios.append({
            "id": nodo_id,
            "nombre": str(nodo.get("nombre") or f"Nodo {i}").strip(),
            "lat": punto["lat"],
            "lng": punto["lng"],
            "descripcion": str(nodo.get("descripcion") or "").strip(),
        })

    return limpios


def normalizar_poligono(poligono):
    """Vértices del lindero, en orden. Menos de 3 puntos no encierran un área."""
    if not isinstance(poligono, list):
        return []

    puntos = [p for p in (_punto(v) for v in poligono) if p]
    return puntos if len(puntos) >= 3 else []


def centro_de(poligono, nodos, ubicacion):
    """
    Punto representativo de la parcela, para el clima y para centrar el mapa.
    Se prefiere el centroide del lindero; si no hay, el promedio de los nodos.
    """
    if poligono:
        return {
            "lat": sum(p["lat"] for p in poligono) / len(poligono),
            "lng": sum(p["lng"] for p in poligono) / len(poligono),
        }
    if nodos:
        return {
            "lat": sum(n["lat"] for n in nodos) / len(nodos),
            "lng": sum(n["lng"] for n in nodos) / len(nodos),
        }
    return ubicacion


def build_parcela(user_id, data):
    nodos = normalizar_nodos(data.get("nodos"))
    poligono = normalizar_poligono(data.get("poligono"))

    ubicacion = {
        "lat": data["ubicacion"]["lat"],
        "lng": data["ubicacion"]["lng"],
    }

    return {
        "userId": ObjectId(user_id),
        "nombre": data["nombre"],
        "cultivo": data["cultivo"],
        "ubicacion": ubicacion,
        "poligono": poligono,
        "nodos": nodos,
        "referencia": data["referencia"],
        "areaAproximada": data.get("areaAproximada"),
        "unidadArea": data.get("unidadArea", "ha"),
        "observaciones": data.get("observaciones", ""),
        "variedad": data.get("variedad", ""),
        "edadCultivo": data.get("edadCultivo", ""),
        "cantidadPlantas": data.get("cantidadPlantas"),
        "sistemaCultivo": data.get("sistemaCultivo", ""),
        "estado": "activo",
        "createdAt": now_utc(),
        "updatedAt": now_utc(),
    }
