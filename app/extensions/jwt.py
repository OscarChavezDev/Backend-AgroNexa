from flask import jsonify
from flask_jwt_extended import JWTManager

jwt = JWTManager()


def init_jwt(app):
    jwt.init_app(app)

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        return jsonify({"msg": f"Token inválido: {error_string}"}), 422

    @jwt.unauthorized_loader
    def missing_token_callback(error_string):
        return jsonify({"msg": "Token de autorización requerido"}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"msg": "El token ha expirado"}), 401
