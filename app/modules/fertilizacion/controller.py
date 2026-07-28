from flask import request
from flask_jwt_extended import get_jwt_identity

from app.modules.fertilizacion.service import (
    generar, obtener_ultimo, listar_historial, obtener_plan, previsualizar,
    mapa_suelo, PARCELA_NO_ENCONTRADA,
)
from app.utils.response import success_response, error_response


def generar_plan(parcela_id):
    """
    Generar un plan de fertilización para una parcela
    ---
    tags:
      - Fertilización
    security:
      - Bearer: []
    parameters:
      - in: path
        name: parcela_id
        type: string
        required: true
      - in: query
        name: reglas
        type: boolean
        required: false
        description: Si es true, omite la IA y usa solo el motor de reglas agronómicas
    responses:
      201:
        description: Plan de fertilización generado
      400:
        description: La parcela no tiene muestras con datos de suelo
      404:
        description: Parcela no encontrada
    """
    user_id = get_jwt_identity()
    forzar_reglas = request.args.get("reglas", "false").lower() == "true"

    result, err = generar(parcela_id, user_id, forzar_reglas)
    if err:
        status = 404 if err == PARCELA_NO_ENCONTRADA else 400
        return error_response(err, status=status)
    return success_response("Plan de fertilización generado", result, 201)


def ultimo_plan(parcela_id):
    """
    Obtener el último plan de fertilización de una parcela
    ---
    tags:
      - Fertilización
    security:
      - Bearer: []
    parameters:
      - in: path
        name: parcela_id
        type: string
        required: true
    responses:
      200:
        description: Plan obtenido
      404:
        description: Parcela no encontrada
    """
    user_id = get_jwt_identity()
    result, err = obtener_ultimo(parcela_id, user_id)
    if err:
        return error_response(err, status=404)
    return success_response("Plan obtenido", result)


def preview(parcela_id):
    """
    Lectura del suelo y ventana climática sin generar el plan completo
    ---
    tags:
      - Fertilización
    security:
      - Bearer: []
    parameters:
      - in: path
        name: parcela_id
        type: string
        required: true
    responses:
      200:
        description: Estado del suelo y del clima obtenido
      404:
        description: Parcela no encontrada
    """
    user_id = get_jwt_identity()
    result, err = previsualizar(parcela_id, user_id)
    if err:
        return error_response(err, status=404)
    return success_response("Estado del suelo y clima obtenido", result)


def mapa(parcela_id):
    """
    Estado del suelo nodo por nodo para pintar el mapa de la parcela
    ---
    tags:
      - Fertilización
    security:
      - Bearer: []
    parameters:
      - in: path
        name: parcela_id
        type: string
        required: true
    responses:
      200:
        description: Mapa de suelo obtenido
      404:
        description: Parcela no encontrada
    """
    user_id = get_jwt_identity()
    result, err = mapa_suelo(parcela_id, user_id)
    if err:
        return error_response(err, status=404)
    return success_response("Mapa de suelo obtenido", result)


def historial(parcela_id):
    """
    Listar los planes de fertilización generados para una parcela
    ---
    tags:
      - Fertilización
    security:
      - Bearer: []
    parameters:
      - in: path
        name: parcela_id
        type: string
        required: true
    responses:
      200:
        description: Historial obtenido
      404:
        description: Parcela no encontrada
    """
    user_id = get_jwt_identity()
    result, err = listar_historial(parcela_id, user_id)
    if err:
        return error_response(err, status=404)
    return success_response("Historial obtenido", result)


def detalle(plan_id):
    """
    Obtener un plan de fertilización por su id
    ---
    tags:
      - Fertilización
    security:
      - Bearer: []
    parameters:
      - in: path
        name: plan_id
        type: string
        required: true
    responses:
      200:
        description: Plan obtenido
      404:
        description: Plan no encontrado
    """
    result, err = obtener_plan(plan_id)
    if err:
        return error_response(err, status=404)
    return success_response("Plan obtenido", result)
