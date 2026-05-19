from flask import request
from flask_jwt_extended import get_jwt_identity
from app.modules.muestras.service import (
    create_muestra, list_muestras, list_muestras_by_parcela,
    get_muestra, update_muestra, delete_muestra,
)
from app.utils.response import success_response, error_response


def crear():
    """
    Registrar una nueva muestra
    ---
    tags:
      - Muestras
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - parcelaId
            - parteAfectada
            - nivelAfectacion
            - sintomas
          properties:
            parcelaId:
              type: string
              example: 64a1b2c3d4e5f6a7b8c9d0e1
            parteAfectada:
              type: string
              enum: [hoja, fruto, tallo, raiz, flor, planta_completa]
              example: fruto
            nivelAfectacion:
              type: string
              enum: [leve, moderado, severo]
              example: moderado
            sintomas:
              type: array
              items:
                type: string
              example: ["manchas oscuras", "pudricion"]
            observaciones:
              type: string
              example: Problema apareció después de las lluvias
            datosSensor:
              type: object
              properties:
                ph:
                  type: number
                  example: 6.5
                nitrogeno:
                  type: number
                  example: 45.0
                fosforo:
                  type: number
                  example: 30.0
                potasio:
                  type: number
                  example: 120.0
                humedadSuelo:
                  type: number
                  example: 65.0
                temperaturaSuelo:
                  type: number
                  example: 22.0
                conductividadElectrica:
                  type: number
                  example: 1.2
    responses:
      201:
        description: Muestra registrada correctamente
      400:
        description: Campos requeridos faltantes
      404:
        description: Parcela no encontrada
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    result, err = create_muestra(user_id, data)
    if err:
        return error_response(err)
    return success_response("Muestra registrada correctamente", result, 201)


def listar():
    """
    Listar muestras del usuario autenticado
    ---
    tags:
      - Muestras
    security:
      - Bearer: []
    responses:
      200:
        description: Lista de muestras obtenida
    """
    user_id = get_jwt_identity()
    result, err = list_muestras(user_id)
    if err:
        return error_response(err)
    return success_response("Muestras obtenidas", result)


def listar_por_parcela(parcela_id):
    """
    Listar muestras de una parcela específica
    ---
    tags:
      - Muestras
    security:
      - Bearer: []
    parameters:
      - in: path
        name: parcela_id
        type: string
        required: true
    responses:
      200:
        description: Muestras de la parcela obtenidas
      404:
        description: Parcela no encontrada
    """
    user_id = get_jwt_identity()
    result, err = list_muestras_by_parcela(parcela_id, user_id)
    if err:
        return error_response(err, status=404)
    return success_response("Muestras de la parcela obtenidas", result)


def detalle(muestra_id):
    """
    Obtener detalle de una muestra
    ---
    tags:
      - Muestras
    security:
      - Bearer: []
    parameters:
      - in: path
        name: muestra_id
        type: string
        required: true
    responses:
      200:
        description: Muestra obtenida
      404:
        description: Muestra no encontrada
    """
    user_id = get_jwt_identity()
    result, err = get_muestra(muestra_id, user_id)
    if err:
        return error_response(err, status=404)
    return success_response("Muestra obtenida", result)


def actualizar(muestra_id):
    """
    Actualizar una muestra
    ---
    tags:
      - Muestras
    security:
      - Bearer: []
    parameters:
      - in: path
        name: muestra_id
        type: string
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            parteAfectada:
              type: string
              enum: [hoja, fruto, tallo, raiz, flor, planta_completa]
            nivelAfectacion:
              type: string
              enum: [leve, moderado, severo]
            sintomas:
              type: array
              items:
                type: string
            observaciones:
              type: string
            datosSensor:
              type: object
    responses:
      200:
        description: Muestra actualizada correctamente
      404:
        description: Muestra no encontrada
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    result, err = update_muestra(muestra_id, user_id, data)
    if err:
        return error_response(err, status=404)
    return success_response("Muestra actualizada correctamente", result)


def eliminar(muestra_id):
    """
    Eliminar una muestra
    ---
    tags:
      - Muestras
    security:
      - Bearer: []
    parameters:
      - in: path
        name: muestra_id
        type: string
        required: true
    responses:
      200:
        description: Muestra eliminada correctamente
      404:
        description: Muestra no encontrada
    """
    user_id = get_jwt_identity()
    result, err = delete_muestra(muestra_id, user_id)
    if err:
        return error_response(err, status=404)
    return success_response("Muestra eliminada correctamente", result)
