from flask import request
from flask_jwt_extended import get_jwt_identity
from app.modules.users.service import (
    get_profile, update_profile, list_users, get_user, change_status,
)
from app.utils.response import success_response, error_response


def mi_perfil():
    """
    Obtener perfil del usuario autenticado
    ---
    tags:
      - Usuarios
    security:
      - Bearer: []
    responses:
      200:
        description: Perfil obtenido
      404:
        description: Usuario no encontrado
    """
    user_id = get_jwt_identity()
    result, err = get_profile(user_id)
    if err:
        return error_response(err, status=404)
    return success_response("Perfil obtenido", result)


def actualizar_perfil():
    """
    Actualizar perfil del usuario autenticado
    ---
    tags:
      - Usuarios
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            nombre:
              type: string
            apellido:
              type: string
            telefono:
              type: string
    responses:
      200:
        description: Perfil actualizado correctamente
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    result, err = update_profile(user_id, data)
    if err:
        return error_response(err)
    return success_response("Perfil actualizado correctamente", result)


def listar_usuarios():
    """
    Listar usuarios
    ---
    tags:
      - Usuarios
    security:
      - Bearer: []
    parameters:
      - in: query
        name: rol
        type: string
        enum: [productor, asociacion, institucion]
    responses:
      200:
        description: Usuarios obtenidos
    """
    rol = request.args.get("rol")
    result, err = list_users(rol)
    if err:
        return error_response(err)
    return success_response("Usuarios obtenidos", result)


def obtener_usuario(user_id):
    """
    Obtener un usuario por ID
    ---
    tags:
      - Usuarios
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: string
        required: true
    responses:
      200:
        description: Usuario obtenido
      404:
        description: Usuario no encontrado
    """
    result, err = get_user(user_id)
    if err:
        return error_response(err, status=404)
    return success_response("Usuario obtenido", result)


def cambiar_estado(user_id):
    """
    Cambiar estado de un usuario
    ---
    tags:
      - Usuarios
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: string
        required: true
      - in: body
        name: body
        schema:
          type: object
          required:
            - estado
          properties:
            estado:
              type: string
              enum: [activo, inactivo, suspendido]
    responses:
      200:
        description: Estado actualizado correctamente
      404:
        description: Usuario no encontrado
    """
    data = request.get_json() or {}
    estado = data.get("estado")
    if not estado:
        return error_response("El campo 'estado' es requerido")
    result, err = change_status(user_id, estado)
    if err:
        return error_response(err, status=404)
    return success_response("Estado actualizado correctamente", result)
