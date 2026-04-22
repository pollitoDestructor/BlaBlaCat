# app/routes/solicitudes.py
from flask import Blueprint, request, jsonify
from ..extensions import db
from ..model.solicitudes import Solicitud

solicitudes_bp = Blueprint("solicitudes", __name__)

@solicitudes_bp.route("/", methods=["GET"])
def get_solicitudes():
    usuario_id = request.args.get("usuario_id")
    query = Solicitud.query
    if usuario_id:
        query = query.filter_by(usuario_id=usuario_id)

    solicitudes = query.all()
    resultado = [
        {
            "id":         s.id,
            "usuario_id": s.usuario_id,
            "nombre":     s.nombre,
            "especie":    s.especie,
            "raza":       s.raza,
        }
        for s in solicitudes
    ]
    return jsonify(resultado), 200


@solicitudes_bp.route("/", methods=["POST"])
def crear_solicitud():
    data = request.get_json()

    nueva = Solicitud(
        usuario_id=data["usuario_id"],
        nombre = data["nombre"],
        especie = data["especie"],
        raza = data.get("raza"))
    
    db.session.add(nueva)
    db.session.commit()

    return jsonify({"mensaje": "Solicitud creada", "id": nueva.id}), 201


@solicitudes_bp.route("/<int:id>", methods=["PUT"])
def modificar_solicitud(id):
    data = request.get_json()
    solicitud = Solicitud.query.get_or_404(id)

    if solicitud.usuario_id != data.get("usuario_id"):
        return jsonify({"error": "No tienes permiso para modificar esta solicitud"}), 403

    solicitud.nombre = data.get("nombre", solicitud.nombre)
    solicitud.especie = data.get("especie", solicitud.especie)
    solicitud.raza = data.get("raza", solicitud.raza)

    db.session.commit()
    return jsonify({"mensaje": "Solicitud modificada"}), 200


@solicitudes_bp.route("/<int:id>", methods=["DELETE"])
def eliminar_solicitud(id):
    solicitud = Solicitud.query.get_or_404(id)
    db.session.delete(solicitud)
    db.session.commit()

    return jsonify({"mensaje": "Solicitud eliminada"}), 200