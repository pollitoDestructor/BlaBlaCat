# app/__init__.py
from flask import Flask, render_template
from .extensions import db, ma
from .config import Config

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    db.init_app(app)
    ma.init_app(app)

    from .routes.solicitudes import solicitudes_bp
    from .routes.auth        import auth_bp
    from .routes.usuarios    import usuarios_bp

    app.register_blueprint(solicitudes_bp, url_prefix="/api/solicitudes")
    app.register_blueprint(auth_bp,        url_prefix="/api/auth")
    app.register_blueprint(usuarios_bp,    url_prefix="/api/usuarios")

    with app.app_context():
        from .model import Usuario, Solicitud, Inscripcion, Valoracion
        db.create_all()

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_spa(path):
        return render_template("index.html")

    return app
