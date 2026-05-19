from flask import Flask, jsonify
from flask_cors import CORS
from flasgger import Swagger
from .config.config import Config
from .extensions.jwt import init_jwt
from .extensions.bcrypt import init_bcrypt
from .extensions.cloudinary import init_cloudinary
from .database.mongo import init_db
from .database.indexes import create_indexes, seed_initial_data

SWAGGER_TEMPLATE = {
    "info": {
        "title": "AgroNexa API",
        "description": (
            "API REST para la plataforma de diagnóstico agrícola AgroNexa. "
            "Incluye gestión de parcelas, muestras, diagnósticos e imágenes."
        ),
        "version": "1.0.0",
        "contact": {"email": "admin@agronexa.com"},
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": (
                'Ingresa el token con el formato: **Bearer &lt;token&gt;**\n\n'
                'Ejemplo: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`'
            ),
        }
    },
}

SWAGGER_CONFIG = {
    "headers": [],
    "specs": [{"endpoint": "apispec", "route": "/apispec.json"}],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs",
}


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, origins=app.config["CORS_ORIGINS"])

    Swagger(app, config=SWAGGER_CONFIG, template=SWAGGER_TEMPLATE)

    init_jwt(app)
    init_bcrypt(app)
    init_cloudinary(app)
    init_db(app)
    create_indexes()
    seed_initial_data()

    from .modules.auth.routes import auth_bp
    from .modules.users.routes import users_bp
    from .modules.parcelas.routes import parcelas_bp
    from .modules.muestras.routes import muestras_bp
    from .modules.diagnostico.routes import diagnostico_bp
    from .modules.imagenes.routes import imagenes_bp
    from .modules.suscripciones.routes import suscripciones_bp
    from .modules.admin.routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(parcelas_bp, url_prefix="/api/parcelas")
    app.register_blueprint(muestras_bp, url_prefix="/api/muestras")
    app.register_blueprint(diagnostico_bp, url_prefix="/api/diagnosticos")
    app.register_blueprint(imagenes_bp, url_prefix="/api/imagenes")
    app.register_blueprint(suscripciones_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    @app.get("/api/config/maps")
    def maps_config():
        """
        Obtener la clave pública de Google Maps
        ---
        tags:
          - Configuración
        responses:
          200:
            description: API key de Google Maps
        """
        return jsonify({"apiKey": app.config.get("GOOGLE_MAPS_API_KEY", "")})

    return app
