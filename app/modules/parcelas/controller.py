from flask import request
from flask_jwt_extended import get_jwt_identity
from app.modules.parcelas.service import (
    create_parcela, list_parcelas, get_parcela,
    update_parcela, delete_parcela,
)
from app.utils.response import success_response, error_response


def crear():
    """
    Registrar una nueva parcela
    ---
    tags:
      - Parcelas
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - nombre
            - cultivo
            - ubicacion
            - referencia
          properties:
            nombre:
              type: string
              example: Parcela Norte
            cultivo:
              type: string
              example: Cacao
            ubicacion:
              type: object
              required:
                - lat
                - lng
              properties:
                lat:
                  type: number
                  example: -6.7714
                lng:
                  type: number
                  example: -79.8409
            referencia:
              type: string
              example: Cerca del río, entrada principal
            areaAproximada:
              type: number
              example: 2.5
            unidadArea:
              type: string
              example: ha
            observaciones:
              type: string
              example: Zona con pendiente moderada
            variedad:
              type: string
              example: CCN-51
            edadCultivo:
              type: string
              example: 3 años
            cantidadPlantas:
              type: integer
              example: 500
            sistemaCultivo:
              type: string
              example: Bajo sombra
    responses:
      201:
        description: Parcela registrada correctamente
      400:
        description: Campos requeridos faltantes
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    result, err = create_parcela(user_id, data)
    if err:
        return error_response(err)
    return success_response("Parcela registrada correctamente", result, 201)


def listar():
    """
    Listar parcelas del usuario autenticado
    ---
    tags:
      - Parcelas
    security:
      - Bearer: []
    responses:
      200:
        description: Lista de parcelas obtenida
    """
    user_id = get_jwt_identity()
    result, err = list_parcelas(user_id)
    if err:
        return error_response(err)
    return success_response("Parcelas obtenidas", result)


def detalle(parcela_id):
    """
    Obtener detalle de una parcela
    ---
    tags:
      - Parcelas
    security:
      - Bearer: []
    parameters:
      - in: path
        name: parcela_id
        type: string
        required: true
    responses:
      200:
        description: Parcela obtenida
      404:
        description: Parcela no encontrada
    """
    user_id = get_jwt_identity()
    result, err = get_parcela(parcela_id, user_id)
    if err:
        return error_response(err, status=404)
    return success_response("Parcela obtenida", result)


def actualizar(parcela_id):
    """
    Actualizar una parcela
    ---
    tags:
      - Parcelas
    security:
      - Bearer: []
    parameters:
      - in: path
        name: parcela_id
        type: string
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            nombre:
              type: string
            cultivo:
              type: string
            referencia:
              type: string
            areaAproximada:
              type: number
            observaciones:
              type: string
    responses:
      200:
        description: Parcela actualizada correctamente
      404:
        description: Parcela no encontrada
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    result, err = update_parcela(parcela_id, user_id, data)
    if err:
        return error_response(err, status=404)
    return success_response("Parcela actualizada correctamente", result)


def eliminar(parcela_id):
    """
    Eliminar (desactivar) una parcela
    ---
    tags:
      - Parcelas
    security:
      - Bearer: []
    parameters:
      - in: path
        name: parcela_id
        type: string
        required: true
    responses:
      200:
        description: Parcela eliminada correctamente
      404:
        description: Parcela no encontrada
    """
    user_id = get_jwt_identity()
    result, err = delete_parcela(parcela_id, user_id)
    if err:
        return error_response(err, status=404)
    return success_response("Parcela eliminada correctamente", result)
