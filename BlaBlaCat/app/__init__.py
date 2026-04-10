# app/__init__.py
from flask import Flask, render_template
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
    from .routes.solicitudes import solicitudes_bp
    from .routes.auth import auth_bp

    app.register_blueprint(solicitudes_bp, url_prefix="/api/users")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    # Crear tablas si no existen
    with app.app_context():
        db.create_all()
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_spa(path):
        return render_template("index.html")
    return app