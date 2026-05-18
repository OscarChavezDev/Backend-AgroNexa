from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.modules.suscripciones.controller import (
    planes, crear_suscripcion, suscripcion_actual, actualizar_plan,
)

suscripciones_bp = Blueprint("suscripciones", __name__)

suscripciones_bp.get("/planes")(planes)
suscripciones_bp.post("/suscripciones")(jwt_required()(crear_suscripcion))
suscripciones_bp.get("/suscripciones/actual")(jwt_required()(suscripcion_actual))
suscripciones_bp.put("/suscripciones/cambiar-plan")(jwt_required()(actualizar_plan))
