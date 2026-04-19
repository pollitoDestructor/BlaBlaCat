# app/__init__.py
from flask import Flask, render_template
from .extensions import db, ma
from .config import Config

# Importar modelos antes de db.create_all() para que SQLAlchemy los registre
from .model.usuarios import Usuario
from .model.solicitudes import Solicitud
from .model.interesados import Interesado
from .model.valoraciones import Valoracion


def _seed_admin():
    """Crea el usuario admin por defecto si no existe todavía."""
    from werkzeug.security import generate_password_hash
    from .model.usuarios import RolEnum

    if not Usuario.query.filter_by(username="admin").first():
        admin = Usuario(
            username          = "admin",
            email             = "admin@blablacat.es",
            password          = generate_password_hash("admin"),
            rol               = RolEnum.administrador,
            asignacion_manual = True,
        )
        db.session.add(admin)
        db.session.commit()
        print("[BlaBlaCat] ✔ Admin creado  →  usuario: admin / contraseña: admin")
    else:
        print("[BlaBlaCat] ℹ Admin ya existe, no se vuelve a crear")


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    db.init_app(app)
    ma.init_app(app)

    from .routes.solicitudes import solicitudes_bp
    from .routes.auth        import auth_bp
    from .routes.admin       import admin_bp

    app.register_blueprint(solicitudes_bp, url_prefix="/api/solicitudes")
    app.register_blueprint(auth_bp,        url_prefix="/api/auth")
    app.register_blueprint(admin_bp,       url_prefix="/api/admin")

    with app.app_context():
        db.create_all()
        _seed_admin()

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_spa(path):
        return render_template("index.html")

    return app