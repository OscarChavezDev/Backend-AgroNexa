from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.modules.diagnostico.controller import generar_diagnostico, obtener_diagnostico

diagnostico_bp = Blueprint("diagnostico", __name__)

diagnostico_bp.post("/generar/<muestra_id>")(jwt_required()(generar_diagnostico))
diagnostico_bp.get("/<diagnostico_id>")(jwt_required()(obtener_diagnostico))
