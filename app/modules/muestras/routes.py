from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.modules.muestras.controller import (
    crear, listar, detalle, actualizar, eliminar,
)
from app.modules.diagnostico.controller import diagnostico_por_muestra
from app.modules.imagenes.controller import listar as listar_imagenes

muestras_bp = Blueprint("muestras", __name__)

muestras_bp.post("/")(jwt_required()(crear))
muestras_bp.get("/")(jwt_required()(listar))
muestras_bp.get("/<muestra_id>")(jwt_required()(detalle))
muestras_bp.put("/<muestra_id>")(jwt_required()(actualizar))
muestras_bp.delete("/<muestra_id>")(jwt_required()(eliminar))
muestras_bp.get("/<muestra_id>/diagnostico")(jwt_required()(diagnostico_por_muestra))
muestras_bp.get("/<muestra_id>/imagenes")(jwt_required()(listar_imagenes))
