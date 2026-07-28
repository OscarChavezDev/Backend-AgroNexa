"""
Motor de reglas agronómicas para fertilización de cacao (Theobroma cacao).

Funciona sin IA y sin conexión externa: interpreta los datos del sensor de suelo
registrados en la muestra y los cruza con el pronóstico de lluvia para decidir
qué aplicar, cuánto y cuándo.
"""

# ── Rangos de interpretación del suelo para cacao ────────────────────────────
# pH óptimo del cacao: ligeramente ácido. Debajo de 5.0 el fósforo se fija en el
# suelo (lo bloquean el aluminio y el hierro) y encalar pasa a ser prioritario.
RANGO_PH = {"optimo_min": 5.5, "optimo_max": 6.5}

# Valores en ppm típicos de un sensor NPK de suelo.
RANGOS_NPK = {
    "nitrogeno": {"bajo": 20, "medio": 40, "unidad": "ppm"},
    "fosforo": {"bajo": 10, "medio": 20, "unidad": "ppm"},
    "potasio": {"bajo": 100, "medio": 180, "unidad": "ppm"},
}

# Dosis de nutriente (kg/ha) según el nivel encontrado en el suelo.
DOSIS_NUTRIENTE = {
    "nitrogeno": {"bajo": 120, "medio": 80, "alto": 40},
    "fosforo": {"bajo": 60, "medio": 30, "alto": 15},
    "potasio": {"bajo": 180, "medio": 120, "alto": 60},
}

# Fuentes comerciales y su riqueza de nutriente.
FUENTES = {
    "urea": {"nombre": "Urea", "riqueza": 0.46, "nutriente": "N"},
    "sulfato_amonio": {"nombre": "Sulfato de amonio", "riqueza": 0.21, "nutriente": "N"},
    "superfosfato": {"nombre": "Superfosfato triple", "riqueza": 0.46, "nutriente": "P₂O₅"},
    "roca_fosforica": {"nombre": "Roca fosfórica", "riqueza": 0.30, "nutriente": "P₂O₅"},
    "sulfato_potasio": {"nombre": "Sulfato de potasio", "riqueza": 0.50, "nutriente": "K₂O"},
    "cloruro_potasio": {"nombre": "Cloruro de potasio", "riqueza": 0.60, "nutriente": "K₂O"},
}

UMBRAL_LLUVIA_EXCESIVA = 25.0   # mm en 72 h: el fertilizante se lava
UMBRAL_LLUVIA_IDEAL = 5.0       # mm en 72 h: humedad suficiente para disolverlo
UMBRAL_VIENTO = 25.0            # km/h: no aplicar foliares


def _es_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _nivel(valor, rangos):
    if not _es_num(valor):
        return "sin_dato"
    if valor < rangos["bajo"]:
        return "bajo"
    if valor < rangos["medio"]:
        return "medio"
    return "alto"


def _area_hectareas(parcela):
    area = parcela.get("areaAproximada")
    if not _es_num(area) or area <= 0:
        return None
    unidad = (parcela.get("unidadArea") or "ha").lower()
    if unidad in ("m2", "m²", "metros", "m"):
        return area / 10000.0
    return float(area)


def interpretar_suelo(datos_sensor):
    """Traduce las lecturas del sensor a niveles agronómicos legibles."""
    ph = datos_sensor.get("ph")
    ce = datos_sensor.get("conductividadElectrica")
    humedad = datos_sensor.get("humedadSuelo")

    if not _es_num(ph):
        estado_ph = "sin_dato"
    elif ph < 5.0:
        estado_ph = "muy_acido"
    elif ph < RANGO_PH["optimo_min"]:
        estado_ph = "acido"
    elif ph <= RANGO_PH["optimo_max"]:
        estado_ph = "optimo"
    elif ph <= 7.5:
        estado_ph = "alcalino"
    else:
        estado_ph = "muy_alcalino"

    if not _es_num(ce):
        estado_ce = "sin_dato"
    elif ce < 0.5:
        estado_ce = "bajo"
    elif ce <= 1.5:
        estado_ce = "optimo"
    elif ce <= 2.0:
        estado_ce = "elevado"
    else:
        estado_ce = "salino"

    if not _es_num(humedad):
        estado_humedad = "sin_dato"
    elif humedad < 40:
        estado_humedad = "seco"
    elif humedad <= 70:
        estado_humedad = "adecuado"
    else:
        estado_humedad = "saturado"

    return {
        "ph": {
            "valor": ph,
            "estado": estado_ph,
            "optimo": f"{RANGO_PH['optimo_min']} – {RANGO_PH['optimo_max']}",
        },
        "nitrogeno": {
            "valor": datos_sensor.get("nitrogeno"),
            "estado": _nivel(datos_sensor.get("nitrogeno"), RANGOS_NPK["nitrogeno"]),
            "unidad": "ppm",
        },
        "fosforo": {
            "valor": datos_sensor.get("fosforo"),
            "estado": _nivel(datos_sensor.get("fosforo"), RANGOS_NPK["fosforo"]),
            "unidad": "ppm",
        },
        "potasio": {
            "valor": datos_sensor.get("potasio"),
            "estado": _nivel(datos_sensor.get("potasio"), RANGOS_NPK["potasio"]),
            "unidad": "ppm",
        },
        "conductividadElectrica": {
            "valor": ce,
            "estado": estado_ce,
            "unidad": "dS/m",
        },
        "humedadSuelo": {
            "valor": humedad,
            "estado": estado_humedad,
            "unidad": "%",
        },
    }


def _dosificar(clave_fuente, kg_nutriente_ha, area_ha, plantas):
    """Convierte kg de nutriente/ha en kg de producto comercial y g por planta."""
    fuente = FUENTES[clave_fuente]
    kg_producto_ha = kg_nutriente_ha / fuente["riqueza"]

    dosis = {
        "producto": fuente["nombre"],
        "nutriente": fuente["nutriente"],
        "dosisHa": f"{round(kg_producto_ha)} kg/ha",
        "nutrienteHa": f"{round(kg_nutriente_ha)} kg {fuente['nutriente']}/ha",
    }

    if area_ha:
        total = kg_producto_ha * area_ha
        dosis["totalParcela"] = f"{round(total, 1)} kg para {round(area_ha, 2)} ha"
        if _es_num(plantas) and plantas > 0:
            dosis["dosisPlanta"] = f"{round(total * 1000 / plantas)} g por planta"

    return dosis


def _plan_ph(suelo, area_ha):
    """Encalado o acidificación. Debe resolverse ANTES que el NPK."""
    estado = suelo["ph"]["estado"]
    valor = suelo["ph"]["valor"]

    if estado == "muy_acido":
        dosis_ha = 2.0
        item = {
            "producto": "Cal dolomita",
            "nutriente": "Ca + Mg",
            "dosisHa": f"{dosis_ha} t/ha",
            "prioridad": "alta",
            "justificacion": (
                f"El pH de {valor} es fuertemente ácido. En este rango el fósforo queda "
                "fijado por el aluminio y el hierro, así que abonar con P antes de encalar "
                "sería desperdiciar el fertilizante. La dolomita también aporta magnesio, "
                "que el cacao necesita para la fotosíntesis."
            ),
            "momento": "60 días antes de la fertilización NPK, incorporada al suelo húmedo.",
        }
    elif estado == "acido":
        dosis_ha = 1.0
        item = {
            "producto": "Cal dolomita",
            "nutriente": "Ca + Mg",
            "dosisHa": f"{dosis_ha} t/ha",
            "prioridad": "media",
            "justificacion": (
                f"El pH de {valor} está apenas por debajo del óptimo del cacao "
                f"({RANGO_PH['optimo_min']}–{RANGO_PH['optimo_max']}). Un encalado ligero "
                "mejora la disponibilidad de nutrientes sin sobrecorregir."
            ),
            "momento": "30 a 45 días antes de aplicar el NPK.",
        }
    elif estado in ("alcalino", "muy_alcalino"):
        item = {
            "producto": "Azufre elemental o materia orgánica ácida",
            "nutriente": "S",
            "dosisHa": "300 – 500 kg/ha",
            "prioridad": "media",
            "justificacion": (
                f"El pH de {valor} está por encima del óptimo del cacao. En suelos alcalinos "
                "el hierro y el zinc se vuelven poco disponibles y aparece clorosis en hojas "
                "jóvenes. Usa sulfato de amonio como fuente de nitrógeno: acidifica mientras nutre."
            ),
            "momento": "Aplicación fraccionada, revisando el pH cada 3 meses.",
        }
    else:
        return None

    if area_ha and item.get("dosisHa", "").endswith("t/ha"):
        item["totalParcela"] = f"{round(dosis_ha * area_ha, 2)} t para {round(area_ha, 2)} ha"

    return item


def _elegir_fuente_n(estado_ph):
    # En suelo alcalino el sulfato de amonio acidifica; en suelo ya ácido lo agravaría.
    if estado_ph in ("alcalino", "muy_alcalino"):
        return "sulfato_amonio"
    return "urea"


def _elegir_fuente_p(estado_ph):
    # La roca fosfórica solo se solubiliza bien en suelos ácidos.
    if estado_ph in ("muy_acido", "acido"):
        return "roca_fosforica"
    return "superfosfato"


def _plan_npk(suelo, area_ha, plantas):
    estado_ph = suelo["ph"]["estado"]
    items = []

    justificaciones = {
        "nitrogeno": {
            "bajo": "El nitrógeno está por debajo del umbral crítico. Es el motor del crecimiento vegetativo: sin él las hojas amarillean y la producción de mazorcas cae.",
            "medio": "El nitrógeno está en un nivel intermedio. Se aplica una dosis de mantenimiento para sostener el follaje sin promover crecimiento excesivo.",
            "alto": "El nitrógeno es suficiente. Solo se repone lo que extrae la cosecha; un exceso favorece follaje sobre fruto y atrae plagas.",
        },
        "fosforo": {
            "bajo": "El fósforo está deficiente. Limita el desarrollo radicular y la floración, que es donde se define la cosecha.",
            "medio": "El fósforo es moderado. Una dosis de mantenimiento sostiene el enraizamiento y el cuaje de flores.",
            "alto": "El fósforo es adecuado. Se repone solo lo extraído para no bloquear la absorción de zinc.",
        },
        "potasio": {
            "bajo": "El potasio está bajo y es el nutriente que el cacao más extrae. Determina el llenado y el peso del grano, además de la tolerancia a sequía y enfermedades.",
            "medio": "El potasio es intermedio. Se refuerza porque la cosecha lo extrae en gran cantidad.",
            "alto": "El potasio es bueno. Se mantiene el nivel reponiendo lo que retira la cosecha.",
        },
    }

    momentos = {
        "nitrogeno": "Fraccionar en 2 o 3 aplicaciones al año, al inicio de las lluvias y en el desarrollo del fruto.",
        "fosforo": "Aplicación única al inicio del período lluvioso, enterrada en el área de goteo.",
        "potasio": "Fraccionar en 2 aplicaciones: una en floración y otra en llenado de mazorca.",
    }

    for nutriente, clave_fuente in (
        ("nitrogeno", _elegir_fuente_n(estado_ph)),
        ("fosforo", _elegir_fuente_p(estado_ph)),
        ("potasio", "sulfato_potasio"),
    ):
        estado = suelo[nutriente]["estado"]
        if estado == "sin_dato":
            continue

        kg_ha = DOSIS_NUTRIENTE[nutriente][estado]
        item = _dosificar(clave_fuente, kg_ha, area_ha, plantas)
        item["prioridad"] = "alta" if estado == "bajo" else ("media" if estado == "medio" else "baja")
        item["justificacion"] = justificaciones[nutriente][estado]
        item["momento"] = momentos[nutriente]

        if clave_fuente == "sulfato_potasio":
            item["nota"] = (
                "Se prefiere sulfato sobre cloruro de potasio: el cacao es sensible al cloruro, "
                "que en exceso quema los bordes de las hojas."
            )
        if clave_fuente == "roca_fosforica":
            item["nota"] = (
                "La roca fosfórica se eligió porque en suelo ácido se solubiliza de forma "
                "gradual y cuesta menos que el superfosfato."
            )
        if clave_fuente == "sulfato_amonio":
            item["nota"] = (
                "Se eligió sulfato de amonio en lugar de urea porque acidifica ligeramente "
                "el suelo, lo que ayuda a corregir el pH alto."
            )

        items.append(item)

    return items


def evaluar_ventana_aplicacion(clima):
    """
    Decide si conviene fertilizar ahora según la lluvia pronosticada.

    Es la regla que conecta el clima con la fertilización: demasiada lluvia lava
    el fertilizante antes de que la planta lo absorba; nada de lluvia lo deja
    sin disolver sobre el suelo.
    """
    if not clima:
        return {
            "apto": None,
            "estado": "sin_datos",
            "motivo": "No se pudo consultar el pronóstico del clima.",
        }

    lluvia_72h = clima.get("lluvia72hMm") or 0
    lluvia_7d = clima.get("lluvia7diasMm") or 0
    pronostico = clima.get("pronostico") or []
    viento = (clima.get("actual") or {}).get("viento")

    advertencias = []
    if _es_num(viento) and viento > UMBRAL_VIENTO:
        advertencias.append(
            f"Viento de {viento} km/h: evita aplicaciones foliares hoy, se dispersan y no llegan a la hoja."
        )

    if lluvia_72h > UMBRAL_LLUVIA_EXCESIVA:
        resultado = {
            "apto": False,
            "estado": "lluvia_excesiva",
            "motivo": (
                f"Se esperan {lluvia_72h} mm de lluvia en las próximas 72 horas. Aplicar ahora "
                "haría que el fertilizante se pierda por escorrentía y lixiviación antes de que "
                "las raíces lo absorban: perderías el producto y el dinero."
            ),
            "recomendacion": "Espera a que pase el frente de lluvia y aplica cuando el acumulado baje.",
        }
    elif lluvia_72h >= UMBRAL_LLUVIA_IDEAL:
        resultado = {
            "apto": True,
            "estado": "ideal",
            "motivo": (
                f"Se esperan {lluvia_72h} mm en 72 horas: es la condición ideal. La lluvia ligera "
                "disuelve el fertilizante y lo incorpora al suelo sin arrastrarlo."
            ),
            "recomendacion": "Aplica ahora, preferentemente en la mañana antes de la lluvia.",
        }
    elif lluvia_7d < 10:
        resultado = {
            "apto": False,
            "estado": "muy_seco",
            "motivo": (
                f"Solo se esperan {lluvia_7d} mm en 7 días. El fertilizante granulado necesita "
                "humedad para disolverse; sobre suelo seco se queda inerte y el nitrógeno de la "
                "urea se volatiliza."
            ),
            "recomendacion": "Aplica solo si cuentas con riego; si no, espera al inicio de las lluvias.",
        }
    else:
        resultado = {
            "apto": True,
            "estado": "aceptable",
            "motivo": (
                f"Se esperan {lluvia_72h} mm en 72 horas y {lluvia_7d} mm en la semana. "
                "Es una ventana aceptable para aplicar."
            ),
            "recomendacion": "Aplica y, de ser posible, incorpora el fertilizante al suelo con un ligero rastrillado.",
        }

    # Mejor día: el primero con lluvia suave (2–15 mm), que arrastra poco y disuelve bien.
    mejor = next(
        (d for d in pronostico if 2 <= (d.get("precipitacionMm") or 0) <= 15),
        None,
    )
    if mejor:
        resultado["mejorDia"] = {
            "fecha": mejor.get("fecha"),
            "precipitacionMm": mejor.get("precipitacionMm"),
            "descripcion": mejor.get("descripcion"),
            "porque": "Lluvia suave: suficiente para disolver el fertilizante sin arrastrarlo.",
        }

    resultado["lluvia72hMm"] = lluvia_72h
    resultado["lluvia7diasMm"] = lluvia_7d
    if advertencias:
        resultado["advertencias"] = advertencias

    return resultado


def _advertencias_suelo(suelo):
    avisos = []

    if suelo["conductividadElectrica"]["estado"] == "salino":
        avisos.append(
            f"Conductividad eléctrica de {suelo['conductividadElectrica']['valor']} dS/m: el suelo "
            "está salino. Reduce las dosis a la mitad y fracciónalas más; agregar más sales "
            "empeoraría el estrés de la planta."
        )
    if suelo["humedadSuelo"]["estado"] == "saturado":
        avisos.append(
            f"Humedad del suelo al {suelo['humedadSuelo']['valor']}%: el suelo está saturado. "
            "Revisa el drenaje antes de fertilizar, porque en encharcamiento la raíz no absorbe "
            "y se favorecen pudriciones como Phytophthora."
        )
    if suelo["humedadSuelo"]["estado"] == "seco":
        avisos.append(
            f"Humedad del suelo al {suelo['humedadSuelo']['valor']}%: el suelo está seco. "
            "Riega antes o aplica junto con la lluvia para que el fertilizante se disuelva."
        )

    sin_dato = [k for k in ("nitrogeno", "fosforo", "potasio", "ph") if suelo[k]["estado"] == "sin_dato"]
    if sin_dato:
        nombres = {"nitrogeno": "nitrógeno", "fosforo": "fósforo", "potasio": "potasio", "ph": "pH"}
        faltantes = ", ".join(nombres[k] for k in sin_dato)
        avisos.append(
            f"La muestra no registra {faltantes}. La recomendación se calculó solo con los datos "
            "disponibles; regístralos para afinar las dosis."
        )

    return avisos


def generar_plan(parcela, muestra, clima=None):
    """Arma el plan de fertilización completo a partir de suelo, parcela y clima."""
    datos_sensor = (muestra or {}).get("datosSensor") or {}
    suelo = interpretar_suelo(datos_sensor)

    area_ha = _area_hectareas(parcela or {})
    plantas = (parcela or {}).get("cantidadPlantas")

    correccion = _plan_ph(suelo, area_ha)
    fertilizantes = _plan_npk(suelo, area_ha, plantas)
    ventana = evaluar_ventana_aplicacion(clima)
    advertencias = _advertencias_suelo(suelo)

    materia_organica = {
        "producto": "Compost o gallinaza descompuesta",
        "dosisHa": "3 – 5 t/ha",
        "justificacion": (
            "La materia orgánica mejora la retención de agua y nutrientes, y alimenta la vida "
            "microbiana que libera el fósforo fijado. Es la base sobre la que el NPK rinde."
        ),
        "momento": "Una vez al año, al inicio de las lluvias, en el área de goteo del árbol.",
    }
    if area_ha:
        materia_organica["totalParcela"] = f"{round(3 * area_ha, 1)} – {round(5 * area_ha, 1)} t para {round(area_ha, 2)} ha"

    resumen = _resumen(suelo, correccion, fertilizantes, ventana)

    return {
        "resumen": resumen,
        "suelo": suelo,
        "correccionPh": correccion,
        "fertilizantes": fertilizantes,
        "materiaOrganica": materia_organica,
        "ventanaAplicacion": ventana,
        "advertencias": advertencias,
        "parcelaInfo": {
            "areaHa": round(area_ha, 2) if area_ha else None,
            "cantidadPlantas": plantas,
        },
    }


def _resumen(suelo, correccion, fertilizantes, ventana):
    deficientes = [
        nombre
        for clave, nombre in (("nitrogeno", "nitrógeno"), ("fosforo", "fósforo"), ("potasio", "potasio"))
        if suelo[clave]["estado"] == "bajo"
    ]

    if deficientes:
        base = f"El suelo presenta deficiencia de {', '.join(deficientes)}."
    elif fertilizantes:
        base = "Los niveles del suelo son aceptables; el plan es de mantenimiento."
    else:
        base = "No hay datos de suelo suficientes para calcular dosis."

    if correccion:
        base += f" Antes del NPK se debe corregir el pH con {correccion['producto'].lower()}."

    if ventana.get("apto") is True:
        base += " El clima acompaña: es buen momento para aplicar."
    elif ventana.get("apto") is False:
        base += " El clima NO acompaña en este momento."

    return base
