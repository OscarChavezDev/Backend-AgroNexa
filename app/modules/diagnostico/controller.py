from flask_jwt_extended import get_jwt_identity
from app.modules.diagnostico.service import generar, get_diagnostico, get_diagnostico_by_muestra
from app.utils.response import success_response, error_response


def generar_diagnostico(muestra_id):
    user_id = get_jwt_identity()
    result, err = generar(muestra_id, user_id)
    if err:
        return error_response(err)
    return success_response("Diagnóstico generado correctamente", result, 201)


def obtener_diagnostico(diagnostico_id):
    result, err = get_diagnostico(diagnostico_id)
    if err:
        return error_response(err, status=404)
    return success_response("Diagnóstico obtenido", result)


def diagnostico_por_muestra(muestra_id):
    user_id = get_jwt_identity()
    result, err = get_diagnostico_by_muestra(muestra_id, user_id)
    if err:
        return error_response(err, status=404)
    return success_response("Diagnóstico obtenido", result)
