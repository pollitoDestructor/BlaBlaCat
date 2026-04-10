# app/routes/auth.py
from flask import Blueprint, request, jsonify
from ..extensions import db
from ..model.usuarios import Usuario
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/registro", methods=["POST"])
def registro():
    data = request.get_json()

    if Usuario.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "El email ya está registrado"}), 409

    nuevo_usuario = Usuario(
        username = data["username"],
        email    = data["email"],
        password = generate_password_hash(data["password"])
    )
    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({"mensaje": "Usuario creado correctamente"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    usuario = Usuario.query.filter_by(email=data["email"]).first()

    if not usuario or not check_password_hash(usuario.password, data["password"]):
        return jsonify({"error": "Credenciales incorrectas"}), 401

    return jsonify({"mensaje": "Login correcto", "usuario_id": usuario.id}), 200