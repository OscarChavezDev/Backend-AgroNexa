from flask import request
from flask_jwt_extended import get_jwt_identity
from app.modules.parcelas.service import (
    create_parcela, list_parcelas, get_parcela,
    update_parcela, delete_parcela,
)
from app.utils.response import success_response, error_response


def crear():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    result, err = create_parcela(user_id, data)
    if err:
        return error_response(err)
    return success_response("Parcela registrada correctamente", result, 201)


def listar():
    user_id = get_jwt_identity()
    result, err = list_parcelas(user_id)
    if err:
        return error_response(err)
    return success_response("Parcelas obtenidas", result)


def detalle(parcela_id):
    user_id = get_jwt_identity()
    result, err = get_parcela(parcela_id, user_id)
    if err:
        return error_response(err, status=404)
    return success_response("Parcela obtenida", result)


def actualizar(parcela_id):
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    result, err = update_parcela(parcela_id, user_id, data)
    if err:
        return error_response(err, status=404)
    return success_response("Parcela actualizada correctamente", result)


def eliminar(parcela_id):
    user_id = get_jwt_identity()
    result, err = delete_parcela(parcela_id, user_id)
    if err:
        return error_response(err, status=404)
    return success_response("Parcela eliminada correctamente", result)
