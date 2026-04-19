from flask import Blueprint, request, jsonify
from ..extensions import db
from ..model.usuarios import Usuario
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/registro", methods=["POST"])
def registro():
    """
    POST /api/auth/registro
    Body: { "username": str, "email": str, "password": str }
    El rol se asigna siempre como 'estandar' por defecto.
    """
    data = request.get_json()

    if not data or not all(k in data for k in ("username", "email", "password")):
        return jsonify({"error": "Faltan campos obligatorios: username, email, password"}), 400

    if Usuario.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "El email ya está registrado"}), 409

    if Usuario.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "El nombre de usuario ya está en uso"}), 409

    nuevo_usuario = Usuario(
        username = data["username"],
        email    = data["email"],
        password = generate_password_hash(data["password"]),
        # rol = RolEnum.estandar  ← ya es el valor por defecto del modelo
    )
    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({"mensaje": "Usuario creado correctamente", "id": nuevo_usuario.id}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    POST /api/auth/login
    Body: { "email": str, "password": str }
    Devuelve usuario_id y rol para que el frontend pueda controlar el acceso.
    """
    data = request.get_json()

    if not data or not all(k in data for k in ("email", "password")):
        return jsonify({"error": "Faltan campos obligatorios: email, password"}), 400

    usuario = Usuario.query.filter_by(email=data["email"]).first()

    if not usuario or not check_password_hash(usuario.password, data["password"]):
        return jsonify({"error": "Credenciales incorrectas"}), 401

    return jsonify({
        "mensaje":    "Login correcto",
        "usuario_id": usuario.id,
        "rol":        usuario.rol.value,   # "estandar" o "administrador"
        "username":   usuario.username,
    }), 200