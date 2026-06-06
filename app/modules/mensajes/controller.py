from flask import request
from flask_jwt_extended import get_jwt_identity
from app.modules.mensajes.service import (
    enviar_feedback, listar_mensajes, conteo,
    marcar_leido, marcar_todos_leidos
)
from app.modules.auth.repository import find_by_id
from app.utils.response import success_response, error_response
from app.middleware.role_middleware import role_required


def enviar():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    mensaje_texto = data.get("mensaje", "")

    # Obtener datos del usuario para personalizar la notificación
    user = find_by_id(user_id)
    if not user:
        return error_response("Usuario no encontrado", status=404)

    result, err = enviar_feedback(
        user_id  = user_id,
        nombre   = user.get("nombre", ""),
        apellido = user.get("apellido", ""),
        correo   = user.get("correo", ""),
        mensaje  = mensaje_texto,
    )
    if err:
        return error_response(err)
    return success_response("Mensaje enviado correctamente", result)


@role_required("admin")
def listar():
    result, err = listar_mensajes()
    if err:
        return error_response(err)
    return success_response("Mensajes obtenidos", result)


@role_required("admin")
def obtener_conteo():
    result, err = conteo()
    if err:
        return error_response(err)
    return success_response("Conteo obtenido", result)


@role_required("admin")
def leer_mensaje(mensaje_id):
    result, err = marcar_leido(mensaje_id)
    if err:
        return error_response(err)
    return success_response("Mensaje marcado como leído", result)


@role_required("admin")
def leer_todos():
    result, err = marcar_todos_leidos()
    if err:
        return error_response(err)
    return success_response("Todos los mensajes marcados como leídos", result)
