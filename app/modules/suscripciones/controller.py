from flask import request
from flask_jwt_extended import get_jwt_identity
from app.modules.suscripciones.service import (
    list_planes, suscribir, get_suscripcion_actual, cambiar_plan,
)
from app.utils.response import success_response, error_response


def planes():
    result, err = list_planes()
    if err:
        return error_response(err)
    return success_response("Planes obtenidos", result)


def crear_suscripcion():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    result, err = suscribir(user_id, data)
    if err:
        return error_response(err)
    return success_response("Suscripción registrada correctamente", result, 201)


def suscripcion_actual():
    user_id = get_jwt_identity()
    result, err = get_suscripcion_actual(user_id)
    if err:
        return error_response(err, status=404)
    return success_response("Suscripción activa obtenida", result)


def actualizar_plan():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    result, err = cambiar_plan(user_id, data)
    if err:
        return error_response(err)
    return success_response("Plan actualizado correctamente", result)
