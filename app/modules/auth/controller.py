from flask import request
from flask_jwt_extended import get_jwt_identity
from app.modules.auth.service import (
    register_user, login_user, get_me, google_login_user, check_email_availability,
    ERR_DUPLICATE_EMAIL, ERR_INTERNAL,
)
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
    result, err, err_code = register_user(data)
    if err:
        if err_code == ERR_DUPLICATE_EMAIL:
            return error_response(err, status=409)   # 409 Conflict
        if err_code == ERR_INTERNAL:
            return error_response(err, status=500)   # 500 Internal Server Error
        return error_response(err, status=400)       # 400 Bad Request (validación)
    return success_response("Usuario registrado correctamente", result, 201)


def check_email():
    """
    Verificar disponibilidad de un correo antes de registrarse
    ---
    tags:
      - Auth
    parameters:
      - in: query
        name: correo
        required: true
        type: string
        example: juan@ejemplo.com
    responses:
      200:
        description: Devuelve si el correo está disponible
      400:
        description: Correo inválido o faltante
    """
    correo = request.args.get("correo", "")
    result, err, err_code = check_email_availability(correo)
    if err:
        if err_code == ERR_INTERNAL:
            return error_response(err, status=500)
        return error_response(err, status=400)
    return success_response("Verificación de correo", result)


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


def google_login():
    """
    Iniciar sesión con Google
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
            - idToken
          properties:
            idToken:
              type: string
              example: "eyJhbGciOiJSUzI1NiIsImtpZCI6..."
    responses:
      200:
        description: Inicio de sesión exitoso, retorna JWT token
      400:
        description: Token inválido o error en la autenticación
    """
    data = request.get_json() or {}
    result, err = google_login_user(data)
    if err:
        return error_response(err, status=400)
    return success_response("Inicio de sesión exitoso con Google", result)

