from flask_jwt_extended import get_jwt_identity
from app.modules.diagnostico.service import generar, regenerar, get_diagnostico, get_diagnostico_by_muestra
from app.utils.response import success_response, error_response


def generar_diagnostico(muestra_id):
    """
    Generar diagnóstico IA para una muestra
    ---
    tags:
      - Diagnóstico
    security:
      - Bearer: []
    parameters:
      - in: path
        name: muestra_id
        type: string
        required: true
    responses:
      201:
        description: Diagnóstico generado correctamente
      400:
        description: Ya existe un diagnóstico (usar regenerar)
      404:
        description: Muestra no encontrada
    """
    user_id = get_jwt_identity()
    result, err = generar(muestra_id, user_id)
    if err:
        return error_response(err)
    return success_response("Diagnóstico generado correctamente", result, 201)


def regenerar_diagnostico(muestra_id):
    """
    Regenerar diagnóstico IA para una muestra (segunda opinión)
    ---
    tags:
      - Diagnóstico
    security:
      - Bearer: []
    parameters:
      - in: path
        name: muestra_id
        type: string
        required: true
    responses:
      201:
        description: Diagnóstico regenerado correctamente
      404:
        description: Muestra no encontrada
    """
    user_id = get_jwt_identity()
    result, err = regenerar(muestra_id, user_id)
    if err:
        return error_response(err)
    return success_response("Diagnóstico regenerado correctamente", result, 201)


def obtener_diagnostico(diagnostico_id):
    """
    Obtener un diagnóstico por ID
    ---
    tags:
      - Diagnóstico
    security:
      - Bearer: []
    parameters:
      - in: path
        name: diagnostico_id
        type: string
        required: true
    responses:
      200:
        description: Diagnóstico obtenido
      404:
        description: Diagnóstico no encontrado
    """
    result, err = get_diagnostico(diagnostico_id)
    if err:
        return error_response(err, status=404)
    return success_response("Diagnóstico obtenido", result)


def diagnostico_por_muestra(muestra_id):
    """
    Obtener diagnóstico de una muestra
    ---
    tags:
      - Diagnóstico
    security:
      - Bearer: []
    parameters:
      - in: path
        name: muestra_id
        type: string
        required: true
    responses:
      200:
        description: Diagnóstico obtenido
      404:
        description: Muestra no encontrada
    """
    user_id = get_jwt_identity()
    result, err = get_diagnostico_by_muestra(muestra_id, user_id)
    if err:
        return error_response(err, status=404)
    return success_response("Diagnóstico obtenido", result)
