# app/routes/solicitudes.py
from flask import Blueprint, request, jsonify
from ..extensions import db
from ..model.solicitudes import Solicitud
from ..model.inscripciones import Inscripcion

solicitudes_bp = Blueprint("solicitudes", __name__)

@solicitudes_bp.route("/", methods=["GET"])
def get_solicitudes():
    usuario_id = request.args.get("usuario_id", type=int)
    exclude_usuario_id = request.args.get("exclude_usuario_id", type=int)
    current_usuario_id = request.args.get("current_usuario_id", type=int)

    query = Solicitud.query
    if usuario_id is not None:
        query = query.filter_by(usuario_id=usuario_id)
    if exclude_usuario_id is not None:
        query = query.filter(Solicitud.usuario_id != exclude_usuario_id)

    solicitudes = query.all()

    registros_existentes = set()
    if current_usuario_id is not None:
        registros_existentes = {
            ins.solicitud_id
            for ins in Inscripcion.query.filter_by(usuario_id=current_usuario_id).all()
        }

    resultado = [
        {
            "id":         s.id,
            "usuario_id": s.usuario_id,
            "nombre":     s.nombre,
            "especie":    s.especie,
            "raza":       s.raza,
            "registrado": s.id in registros_existentes,
        }
        for s in solicitudes
    ]
    return jsonify(resultado), 200

@solicitudes_bp.route("/<int:id>/registrarse", methods=["POST"])
def registrarse_solicitud(id):
    data = request.get_json() or {}
    usuario_id = data.get("usuario_id")

    if usuario_id is None:
        return jsonify({"error": "usuario_id requerido"}), 400

    solicitud = Solicitud.query.get_or_404(id)

    if solicitud.usuario_id == int(usuario_id):
        return jsonify({"error": "No puedes registrarte en tu propia solicitud"}), 403

    if Inscripcion.query.filter_by(solicitud_id=id, usuario_id=usuario_id).first():
        return jsonify({"error": "Ya estás registrado en esta solicitud"}), 409

    nueva_inscripcion = Inscripcion(
        usuario_id=usuario_id,
        solicitud_id=id,
    )
    db.session.add(nueva_inscripcion)
    db.session.commit()

    return jsonify({"mensaje": "Te has registrado en la solicitud correctamente"}), 201

@solicitudes_bp.route("/<int:id>/registrarse", methods=["DELETE"])
def cancelar_registro_solicitud(id):
    data = request.get_json() or {}
    usuario_id = data.get("usuario_id")

    if usuario_id is None:
        return jsonify({"error": "usuario_id requerido"}), 400

    inscripcion = Inscripcion.query.filter_by(solicitud_id=id, usuario_id=usuario_id).first()
    if not inscripcion:
        return jsonify({"error": "No estás registrado en esta solicitud"}), 404

    db.session.delete(inscripcion)
    db.session.commit()

    return jsonify({"mensaje": "Registro cancelado correctamente"}), 200


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

    usuario_id = data.get("usuario_id")
    if usuario_id is not None:
        usuario_id = int(usuario_id)

    if solicitud.usuario_id != usuario_id:
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


