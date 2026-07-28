from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.modules.clima.controller import clima_por_coordenadas, clima_por_parcela

clima_bp = Blueprint("clima", __name__)

clima_bp.get("/")(jwt_required()(clima_por_coordenadas))
clima_bp.get("/parcela/<parcela_id>")(jwt_required()(clima_por_parcela))
