from flask import request
from flask_jwt_extended import get_jwt_identity
from app.modules.muestras.service import (
    create_muestra, list_muestras, list_muestras_by_parcela,
    get_muestra, update_muestra, delete_muestra,
)
from app.utils.response import success_response, error_response


def crear():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    result, err = create_muestra(user_id, data)
    if err:
        return error_response(err)
    return success_response("Muestra registrada correctamente", result, 201)


def listar():
    user_id = get_jwt_identity()
    result, err = list_muestras(user_id)
    if err:
        return error_response(err)
    return success_response("Muestras obtenidas", result)


def listar_por_parcela(parcela_id):
    user_id = get_jwt_identity()
    result, err = list_muestras_by_parcela(parcela_id, user_id)
    if err:
        return error_response(err, status=404)
    return success_response("Muestras de la parcela obtenidas", result)


def detalle(muestra_id):
    user_id = get_jwt_identity()
    result, err = get_muestra(muestra_id, user_id)
    if err:
        return error_response(err, status=404)
    return success_response("Muestra obtenida", result)


def actualizar(muestra_id):
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    result, err = update_muestra(muestra_id, user_id, data)
    if err:
        return error_response(err, status=404)
    return success_response("Muestra actualizada correctamente", result)


def eliminar(muestra_id):
    user_id = get_jwt_identity()
    result, err = delete_muestra(muestra_id, user_id)
    if err:
        return error_response(err, status=404)
    return success_response("Muestra eliminada correctamente", result)
