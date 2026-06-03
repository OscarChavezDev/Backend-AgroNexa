from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.modules.admin.controller import (
    listar_usuarios, obtener_usuario, cambiar_estado_usuario,
    eliminar_usuario, estadisticas, parcelas_usuario, historial_usuario,
    reingresos_usuarios, actividad_temporal,
)

admin_bp = Blueprint("admin", __name__)

admin_bp.get("/usuarios")(jwt_required()(listar_usuarios))
admin_bp.get("/usuarios/<user_id>")(jwt_required()(obtener_usuario))
admin_bp.get("/usuarios/<user_id>/parcelas")(jwt_required()(parcelas_usuario))
admin_bp.get("/usuarios/<user_id>/historial")(jwt_required()(historial_usuario))
admin_bp.put("/usuarios/<user_id>/estado")(jwt_required()(cambiar_estado_usuario))
admin_bp.delete("/usuarios/<user_id>")(jwt_required()(eliminar_usuario))
admin_bp.get("/estadisticas")(jwt_required()(estadisticas))
admin_bp.get("/sesiones")(jwt_required()(reingresos_usuarios))
admin_bp.get("/estadisticas/actividad")(jwt_required()(actividad_temporal))
