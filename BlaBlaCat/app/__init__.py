# app/__init__.py
from flask import Flask
from .extensions import db, ma
from .config import Config
from .model.usuarios import Usuario
from .model.solicitudes import Solicitud

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Inicializar extensiones
    db.init_app(app)
    ma.init_app(app)

    # Registrar blueprints
    from .routes.users import users_bp
    from .routes.auth import auth_bp

    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    # Crear tablas si no existen
    with app.app_context():
        db.create_all()

    return app