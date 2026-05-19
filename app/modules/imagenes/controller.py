from flask import request
from flask_jwt_extended import get_jwt_identity
from app.modules.imagenes.service import subir_imagen, listar_imagenes, eliminar_imagen
from app.utils.response import success_response, error_response


def upload():
    """
    Subir una imagen asociada a una muestra
    ---
    tags:
      - Imágenes
    security:
      - Bearer: []
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: Archivo de imagen
      - in: formData
        name: muestraId
        type: string
        required: true
        description: ID de la muestra
      - in: formData
        name: tipoImagen
        type: string
        enum: [hoja, fruto, tallo, planta_completa, suelo]
        description: Tipo de imagen
      - in: formData
        name: descripcion
        type: string
        description: Descripción opcional
    responses:
      201:
        description: Imagen subida correctamente
      400:
        description: Error de validación
    """
    user_id = get_jwt_identity()
    file = request.files.get("file")
    data = {
        "muestraId": request.form.get("muestraId"),
        "tipoImagen": request.form.get("tipoImagen", "planta_completa"),
        "descripcion": request.form.get("descripcion", ""),
    }
    result, err = subir_imagen(user_id, file, data)
    if err:
        return error_response(err)
    return success_response("Imagen subida correctamente", result, 201)


def listar(muestra_id):
    """
    Listar imágenes de una muestra
    ---
    tags:
      - Imágenes
    security:
      - Bearer: []
    parameters:
      - in: path
        name: muestra_id
        type: string
        required: true
    responses:
      200:
        description: Imágenes obtenidas
      404:
        description: Muestra no encontrada
    """
    user_id = get_jwt_identity()
    result, err = listar_imagenes(muestra_id, user_id)
    if err:
        return error_response(err, status=404)
    return success_response("Imágenes obtenidas", result)


def eliminar(imagen_id):
    """
    Eliminar una imagen
    ---
    tags:
      - Imágenes
    security:
      - Bearer: []
    parameters:
      - in: path
        name: imagen_id
        type: string
        required: true
      - in: query
        name: muestraId
        type: string
        required: true
    responses:
      200:
        description: Imagen eliminada correctamente
      404:
        description: Imagen no encontrada
    """
    user_id = get_jwt_identity()
    muestra_id = request.args.get("muestraId")
    result, err = eliminar_imagen(user_id, imagen_id, muestra_id)
    if err:
        return error_response(err, status=404)
    return success_response("Imagen eliminada correctamente", result)
