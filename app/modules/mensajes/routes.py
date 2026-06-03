from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.modules.mensajes.controller import (
    enviar, listar, obtener_conteo, leer_mensaje, leer_todos
)

mensajes_bp = Blueprint("mensajes", __name__)

mensajes_bp.post("/")       (jwt_required()(enviar))
mensajes_bp.get("/")        (jwt_required()(listar))
mensajes_bp.get("/conteo")  (jwt_required()(obtener_conteo))
mensajes_bp.put("/leer-todos")(jwt_required()(leer_todos))
mensajes_bp.put("/<mensaje_id>/leer")(jwt_required()(leer_mensaje))
