from flask import request
from flask_jwt_extended import get_jwt_identity
from app.modules.imagenes.service import subir_imagen, listar_imagenes, eliminar_imagen
from app.utils.response import success_response, error_response


def upload():
    user_id = get_jwt_identity()
    file = request.files.get("file")
    data = {
        "muestraId": request.form.get("muestraId"),
        "tipo": request.form.get("tipo", "general"),
        "descripcion": request.form.get("descripcion", ""),
    }
    result, err = subir_imagen(user_id, file, data)
    if err:
        return error_response(err)
    return success_response("Imagen subida correctamente", result, 201)


def listar(muestra_id):
    user_id = get_jwt_identity()
    result, err = listar_imagenes(muestra_id, user_id)
    if err:
        return error_response(err, status=404)
    return success_response("Imágenes obtenidas", result)


def eliminar(imagen_id):
    user_id = get_jwt_identity()
    muestra_id = request.args.get("muestraId")
    result, err = eliminar_imagen(user_id, imagen_id, muestra_id)
    if err:
        return error_response(err, status=404)
    return success_response("Imagen eliminada correctamente", result)
