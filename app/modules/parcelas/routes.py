from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.modules.parcelas.controller import crear, listar, detalle, actualizar, eliminar
from app.modules.muestras.controller import listar_por_parcela

parcelas_bp = Blueprint("parcelas", __name__)

parcelas_bp.post("/")(jwt_required()(crear))
parcelas_bp.get("/")(jwt_required()(listar))
parcelas_bp.get("/<parcela_id>")(jwt_required()(detalle))
parcelas_bp.put("/<parcela_id>")(jwt_required()(actualizar))
parcelas_bp.delete("/<parcela_id>")(jwt_required()(eliminar))
parcelas_bp.get("/<parcela_id>/muestras")(jwt_required()(listar_por_parcela))
