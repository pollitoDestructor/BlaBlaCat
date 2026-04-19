# app/routes/solicitudes.py
from flask import Blueprint, request, jsonify
from ..extensions import db
from ..model.solicitudes import Solicitud

solicitudes_bp = Blueprint("solicitudes", __name__)


@solicitudes_bp.route("/", methods=["GET"])
def get_solicitudes():
    """Devuelve todas las solicitudes del usuario logueado."""
    usuario_id = request.args.get("usuario_id")

    if usuario_id:
        solicitudes = Solicitud.query.filter_by(usuario_id=int(usuario_id)).all()
    else:
        solicitudes = Solicitud.query.all()

    resultado = [
        {
            "id":               s.id,               # ← antes faltaba este campo
            "nombre":           s.nombre,
            "especie":          s.especie,
            "raza":             s.raza,
            "foto_url":         s.foto_url,
            "horario_inicio":   s.horario_inicio.isoformat() if s.horario_inicio else None,
            "horario_fin":      s.horario_fin.isoformat()    if s.horario_fin    else None,
            "especificaciones": s.especificaciones,
        }
        for s in solicitudes
    ]
    return jsonify(resultado), 200


@solicitudes_bp.route("/", methods=["POST"])
def crear_solicitud():
    data = request.get_json()

    if not data or not all(k in data for k in ("usuario_id", "nombre", "especie")):
        return jsonify({"error": "Faltan campos: usuario_id, nombre, especie"}), 400

    # Convertir horarios si vienen como string ISO
    from datetime import datetime

    def parse_dt(valor):
        if not valor:
            return None
        try:
            return datetime.fromisoformat(valor)
        except (ValueError, TypeError):
            return None

    nueva = Solicitud(
        usuario_id       = data["usuario_id"],
        nombre           = data["nombre"],
        especie          = data["especie"],
        raza             = data.get("raza"),
        foto_url         = data.get("foto_url"),
        horario_inicio   = parse_dt(data.get("horario_inicio")),
        horario_fin      = parse_dt(data.get("horario_fin")),
        especificaciones = data.get("especificaciones"),
    )
    db.session.add(nueva)
    db.session.commit()

    return jsonify({"mensaje": "Solicitud creada", "id": nueva.id}), 201


@solicitudes_bp.route("/<int:id>", methods=["DELETE"])
def eliminar_solicitud(id):
    solicitud = db.session.get(Solicitud, id)
    if not solicitud:
        return jsonify({"error": "Solicitud no encontrada"}), 404

    db.session.delete(solicitud)
    db.session.commit()
    return jsonify({"mensaje": "Solicitud eliminada"}), 200