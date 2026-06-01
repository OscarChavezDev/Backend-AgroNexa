from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.modules.auth.controller import register, login, me, google_login

auth_bp = Blueprint("auth", __name__)

auth_bp.post("/register")(register)
auth_bp.post("/login")(login)
auth_bp.post("/google")(google_login)
auth_bp.get("/me")(jwt_required()(me))

