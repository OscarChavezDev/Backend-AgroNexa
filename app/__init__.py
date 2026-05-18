from flask import Flask
from flask_cors import CORS
from .config.config import Config
from .extensions.jwt import init_jwt
from .extensions.bcrypt import init_bcrypt
from .extensions.cloudinary import init_cloudinary
from .database.mongo import init_db
from .database.indexes import create_indexes, seed_initial_data


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, origins=app.config["CORS_ORIGINS"])

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

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(parcelas_bp, url_prefix="/api/parcelas")
    app.register_blueprint(muestras_bp, url_prefix="/api/muestras")
    app.register_blueprint(diagnostico_bp, url_prefix="/api/diagnosticos")
    app.register_blueprint(imagenes_bp, url_prefix="/api/imagenes")
    app.register_blueprint(suscripciones_bp, url_prefix="/api")

    return app
