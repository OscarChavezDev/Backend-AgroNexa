from flask import request
from flask_jwt_extended import get_jwt_identity
from app.modules.admin.service import (
    list_all_users, get_user_detail, change_user_status,
    delete_user, get_stats, get_user_parcelas, get_user_historial,
    get_reingresos, get_actividad_temporal,
    INACTIVIDAD_DIAS,
)
from app.modules.auth.models import build_role_filter
from app.middleware.role_middleware import role_required
from app.utils.response import success_response, error_response


@role_required("admin")
def listar_usuarios():
    """
    Listar todos los usuarios registrados
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - in: query
        name: rol
        type: string
        enum: [productor, asociacion, institucion, institucional]
        description: Filtrar por rol
      - in: query
        name: estado
        type: string
        enum: [activo, inactivo, suspendido]
        description: Filtrar por estado
    responses:
      200:
        description: Lista de usuarios obtenida
      403:
        description: Acceso no autorizado
    """
    rol = request.args.get("rol")
    estado = request.args.get("estado")
    filters = {}
    if rol:
        filters["rol"] = build_role_filter(rol)
    if estado:
        filters["estado"] = estado
    result, err = list_all_users(filters)
    if err:
        return error_response(err)
    return success_response("Usuarios obtenidos", result)


@role_required("admin")
def obtener_usuario(user_id):
    """
    Obtener detalle de un usuario
    ---
    tags:
      - Admin
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
    result, err = get_user_detail(user_id)
    if err:
        return error_response(err, status=404)
    return success_response("Usuario obtenido", result)


@role_required("admin")
def cambiar_estado_usuario(user_id):
    """
    Cambiar el estado de un usuario
    ---
    tags:
      - Admin
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
        description: Estado actualizado
      400:
        description: Estado inválido
      404:
        description: Usuario no encontrado
    """
    data = request.get_json() or {}
    estado = data.get("estado")
    if not estado:
        return error_response("El campo 'estado' es requerido")
    result, err = change_user_status(user_id, estado)
    if err:
        return error_response(err, status=404)
    return success_response("Estado del usuario actualizado", result)


@role_required("admin")
def eliminar_usuario(user_id):
    """
    Eliminar un usuario (no se puede eliminar administradores)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: string
        required: true
    responses:
      200:
        description: Usuario eliminado
      404:
        description: Usuario no encontrado
    """
    result, err = delete_user(user_id)
    if err:
        return error_response(err, status=404)
    return success_response("Usuario eliminado correctamente", result)


@role_required("admin")
def parcelas_usuario(user_id):
    """
    Parcelas de un usuario con conteos de muestras y diagnósticos
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: string
        required: true
    responses:
      200:
        description: Parcelas con estadísticas
    """
    result, err = get_user_parcelas(user_id)
    if err:
        return error_response(err, status=404)
    return success_response("Parcelas del usuario obtenidas", result)


@role_required("admin")
def historial_usuario(user_id):
    """
    Historial de cambios de estado de un usuario
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: string
        required: true
    responses:
      200:
        description: Historial obtenido (más reciente primero)
      404:
        description: Usuario no encontrado
    """
    result, err = get_user_historial(user_id)
    if err:
        return error_response(err, status=404)
    return success_response(
        f"Historial obtenido. Regla activa: inactividad automática tras {INACTIVIDAD_DIAS} días sin acceso.",
        result,
    )


@role_required("admin")
def estadisticas():
    """
    Estadísticas generales de la plataforma
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: Estadísticas obtenidas
      403:
        description: Acceso no autorizado
    """
    result, err = get_stats()
    if err:
        return error_response(err)
    return success_response("Estadísticas obtenidas", result)


@role_required("admin")
def reingresos_usuarios():
    """
    Historial de reingresos: usuarios que volvieron a iniciar sesión
    tras haber sido marcados como inactivos automáticamente.
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: Lista de eventos de reingreso (reactivado_automatico)
    """
    result, err = get_reingresos()
    if err:
        return error_response(err)
    return success_response("Reingresos obtenidos", result)


@role_required("admin")
def actividad_temporal():
    result, err = get_actividad_temporal()
    if err:
        return error_response(err)
    return success_response("Actividad temporal obtenida", result)
