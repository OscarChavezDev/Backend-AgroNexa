from flask import request
from flask_jwt_extended import get_jwt_identity
from app.modules.auth.service import register_user, login_user, get_me
from app.utils.response import success_response, error_response


def register():
    """
    Registrar un nuevo usuario
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - nombre
            - apellido
            - correo
            - password
          properties:
            nombre:
              type: string
              example: Juan
            apellido:
              type: string
              example: Perez
            correo:
              type: string
              example: juan@ejemplo.com
            password:
              type: string
              example: "Segura123!"
            telefono:
              type: string
              example: "987654321"
            rol:
              type: string
              enum: [productor, asociacion, institucion]
              example: productor
    responses:
      201:
        description: Usuario registrado correctamente
      400:
        description: Error de validación o correo ya registrado
    """
    data = request.get_json() or {}
    result, err = register_user(data)
    if err:
        return error_response(err)
    return success_response("Usuario registrado correctamente", result, 201)


def login():
    """
    Iniciar sesión
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - correo
            - password
          properties:
            correo:
              type: string
              example: juan@ejemplo.com
            password:
              type: string
              example: "Segura123!"
    responses:
      200:
        description: Inicio de sesión exitoso, retorna JWT token
      401:
        description: Credenciales inválidas o cuenta inactiva
    """
    data = request.get_json() or {}
    result, err = login_user(data)
    if err:
        return error_response(err, status=401)
    return success_response("Inicio de sesión exitoso", result)


def me():
    """
    Obtener datos del usuario autenticado
    ---
    tags:
      - Auth
    security:
      - Bearer: []
    responses:
      200:
        description: Datos del usuario autenticado
      404:
        description: Usuario no encontrado
    """
    user_id = get_jwt_identity()
    result, err = get_me(user_id)
    if err:
        return error_response(err, status=404)
    return success_response("Usuario autenticado", result)
