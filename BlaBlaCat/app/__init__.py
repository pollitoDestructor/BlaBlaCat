# app/__init__.py
from flask import Flask, render_template
from .extensions import db, ma
from .config import Config

# Modelos — deben importarse antes de db.create_all()
from .model.usuarios import Usuario
from .model.solicitudes import Solicitud
from .model.interesados import Interesado
from .model.valoraciones import Valoracion

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Inicializar extensiones
    db.init_app(app)
    ma.init_app(app)

    # Registrar blueprints
    from .routes.solicitudes import solicitudes_bp
    from .routes.auth import auth_bp
    from .routes.admin import admin_bp

    app.register_blueprint(solicitudes_bp, url_prefix="/api/solicitudes")
    app.register_blueprint(auth_bp,        url_prefix="/api/auth")
    app.register_blueprint(admin_bp,       url_prefix="/api/admin")

    # Crear tablas si no existen
    with app.app_context():
        db.create_all()

    # SPA catch-all
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_spa(path):
        return render_template("index.html")

    return app