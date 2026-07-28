from flask import request
from flask_jwt_extended import get_jwt_identity

from app.modules.clima.service import obtener_pronostico
from app.modules.parcelas.repository import find_by_id_and_user
from app.utils.response import success_response, error_response


def clima_por_coordenadas():
    """
    Consultar el clima y pronóstico por coordenadas
    ---
    tags:
      - Clima
    security:
      - Bearer: []
    parameters:
      - in: query
        name: lat
        type: number
        required: true
        example: -6.7714
      - in: query
        name: lng
        type: number
        required: true
        example: -79.8409
      - in: query
        name: dias
        type: integer
        required: false
        example: 7
    responses:
      200:
        description: Clima obtenido
      400:
        description: Coordenadas inválidas
    """
    lat = request.args.get("lat")
    lng = request.args.get("lng")
    if lat is None or lng is None:
        return error_response("Debes indicar lat y lng")

    dias = request.args.get("dias", 7, type=int)
    clima, err = obtener_pronostico(lat, lng, dias)
    if err:
        return error_response(err)
    return success_response("Clima obtenido", clima)


def clima_por_parcela(parcela_id):
    """
    Consultar el clima de una parcela usando su ubicación registrada
    ---
    tags:
      - Clima
    security:
      - Bearer: []
    parameters:
      - in: path
        name: parcela_id
        type: string
        required: true
      - in: query
        name: dias
        type: integer
        required: false
    responses:
      200:
        description: Clima de la parcela obtenido
      404:
        description: Parcela no encontrada
    """
    user_id = get_jwt_identity()
    parcela = find_by_id_and_user(parcela_id, user_id)
    if not parcela:
        return error_response("Parcela no encontrada", status=404)

    ubicacion = parcela.get("ubicacion") or {}
    dias = request.args.get("dias", 7, type=int)
    clima, err = obtener_pronostico(ubicacion.get("lat"), ubicacion.get("lng"), dias)
    if err:
        return error_response(err)

    clima["parcela"] = {"id": parcela_id, "nombre": parcela.get("nombre", "")}
    return success_response("Clima de la parcela obtenido", clima)
