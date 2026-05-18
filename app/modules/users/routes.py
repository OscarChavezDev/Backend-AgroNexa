from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.modules.users.controller import (
    mi_perfil, actualizar_perfil, listar_usuarios,
    obtener_usuario, cambiar_estado,
)

users_bp = Blueprint("users", __name__)

users_bp.get("/me")(jwt_required()(mi_perfil))
users_bp.put("/me")(jwt_required()(actualizar_perfil))
users_bp.get("/")(jwt_required()(listar_usuarios))
users_bp.get("/<user_id>")(jwt_required()(obtener_usuario))
users_bp.put("/<user_id>/status")(jwt_required()(cambiar_estado))
