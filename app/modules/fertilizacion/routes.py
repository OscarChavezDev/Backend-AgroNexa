from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.modules.fertilizacion.controller import (
    generar_plan, ultimo_plan, preview, historial, detalle, mapa,
)

fertilizacion_bp = Blueprint("fertilizacion", __name__)

fertilizacion_bp.post("/generar/<parcela_id>")(jwt_required()(generar_plan))
fertilizacion_bp.get("/parcela/<parcela_id>")(jwt_required()(ultimo_plan))
fertilizacion_bp.get("/parcela/<parcela_id>/preview")(jwt_required()(preview))
fertilizacion_bp.get("/parcela/<parcela_id>/mapa-suelo")(jwt_required()(mapa))
fertilizacion_bp.get("/parcela/<parcela_id>/historial")(jwt_required()(historial))
fertilizacion_bp.get("/<plan_id>")(jwt_required()(detalle))
