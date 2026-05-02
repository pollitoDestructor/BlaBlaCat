from flask import Blueprint, request, jsonify
from ..extensions import db
from ..model.usuarios import Usuario
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/registro", methods=["POST"])
def registro():
    data = request.get_json()

    if not data or not all(k in data for k in ("username", "email", "password")):
        return jsonify({"error": "Faltan campos obligatorios: username, email, password"}), 400

    if Usuario.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "El email ya está registrado"}), 409

    if Usuario.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "El nombre de usuario ya está en uso"}), 409

    nuevo = Usuario(
        username = data["username"],
        email    = data["email"],
        password = generate_password_hash(data["password"]),
    )
    db.session.add(nuevo)
    db.session.commit()

    return jsonify({"mensaje": "Usuario creado correctamente", "id": nuevo.id}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or not all(k in data for k in ("email", "password")):
        return jsonify({"error": "Faltan campos obligatorios: email, password"}), 400

    usuario = Usuario.query.filter_by(email=data["email"]).first()

    if not usuario or not check_password_hash(usuario.password, data["password"]):
        return jsonify({"error": "Credenciales incorrectas"}), 401

    return jsonify({
        "mensaje":    "Login correcto",
        "usuario_id": usuario.id,
        "rol":        usuario.rol.value,
        "username":   usuario.username,
    }), 200
