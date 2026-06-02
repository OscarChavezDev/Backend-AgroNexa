from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.modules.imagenes.controller import upload, eliminar, validar

imagenes_bp = Blueprint("imagenes", __name__)

imagenes_bp.post("/upload")(jwt_required()(upload))
imagenes_bp.post("/validar")(jwt_required()(validar))
imagenes_bp.delete("/<imagen_id>")(jwt_required()(eliminar))
