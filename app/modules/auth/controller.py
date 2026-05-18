from flask import request
from flask_jwt_extended import get_jwt_identity
from app.modules.auth.service import register_user, login_user, get_me
from app.utils.response import success_response, error_response


def register():
    data = request.get_json() or {}
    result, err = register_user(data)
    if err:
        return error_response(err)
    return success_response("Usuario registrado correctamente", result, 201)


def login():
    data = request.get_json() or {}
    result, err = login_user(data)
    if err:
        return error_response(err, status=401)
    return success_response("Inicio de sesión exitoso", result)


def me():
    user_id = get_jwt_identity()
    result, err = get_me(user_id)
    if err:
        return error_response(err, status=404)
    return success_response("Usuario autenticado", result)
