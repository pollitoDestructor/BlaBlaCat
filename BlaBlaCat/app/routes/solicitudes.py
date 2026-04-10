# app/routes/solicitudes.py
from flask import Blueprint, request, jsonify
from ..extensions import db
from ..model.solicitudes import Solicitud

solicitudes_bp = Blueprint("solicitudes", __name__)

@solicitudes_bp.route("/", methods=["GET"])
def get_solicitudes():
    #solicitudes = Solicitud.query.all()
    #resultado = [{"id": s.id, "usuario_id": s.usuario_id, "created_at": str(s.created_at)} for s in solicitudes]
    #return jsonify(resultado), 200
    return None


@solicitudes_bp.route("/", methods=["POST"])
def crear_solicitud():
    data = request.get_json()

    nueva = Solicitud(
        usuario_id=data["usuario_id"],
        nombre = data["nombre"],
        especie = data["especie"],
        raza = data["raza"])
    
    db.session.add(nueva)
    db.session.commit()

    return jsonify({"mensaje": "Solicitud creada", "id": nueva.id}), 201


@solicitudes_bp.route("/<int:id>", methods=["DELETE"])
def eliminar_solicitud(id):
    solicitud = Solicitud.query.get_or_404(id)
    db.session.delete(solicitud)
    db.session.commit()

    return jsonify({"mensaje": "Solicitud eliminada"}), 200