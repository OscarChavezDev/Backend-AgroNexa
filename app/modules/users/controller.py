from flask import request
from flask_jwt_extended import get_jwt_identity
from app.modules.users.service import (
    get_profile, update_profile, list_users, get_user, change_status,
)
from app.utils.response import success_response, error_response


def mi_perfil():
    user_id = get_jwt_identity()
    result, err = get_profile(user_id)
    if err:
        return error_response(err, status=404)
    return success_response("Perfil obtenido", result)


def actualizar_perfil():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    result, err = update_profile(user_id, data)
    if err:
        return error_response(err)
    return success_response("Perfil actualizado correctamente", result)


def listar_usuarios():
    rol = request.args.get("rol")
    result, err = list_users(rol)
    if err:
        return error_response(err)
    return success_response("Usuarios obtenidos", result)


def obtener_usuario(user_id):
    result, err = get_user(user_id)
    if err:
        return error_response(err, status=404)
    return success_response("Usuario obtenido", result)


def cambiar_estado(user_id):
    data = request.get_json() or {}
    estado = data.get("estado")
    if not estado:
        return error_response("El campo 'estado' es requerido")
    result, err = change_status(user_id, estado)
    if err:
        return error_response(err, status=404)
    return success_response("Estado actualizado correctamente", result)
