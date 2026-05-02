from flask import Blueprint, request, jsonify
from datetime import datetime
from ..extensions import db
from ..model.solicitudes import Solicitud
from ..model.inscripciones import Inscripcion

solicitudes_bp = Blueprint("solicitudes", __name__)


def parse_dt(valor):
    if not valor:
        return None
    try:
        return datetime.fromisoformat(valor)
    except (ValueError, TypeError):
        return None


@solicitudes_bp.route("/", methods=["GET"])
def get_solicitudes():
    usuario_id         = request.args.get("usuario_id",         type=int)
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
            "id":               s.id,
            "usuario_id":       s.usuario_id,
            "cuidador_id":      s.cuidador_id,
            "nombre":           s.nombre,
            "especie":          s.especie,
            "raza":             s.raza,
            "foto_url":         s.foto_url,
            "horario_inicio":   s.horario_inicio.isoformat() if s.horario_inicio else None,
            "horario_fin":      s.horario_fin.isoformat()    if s.horario_fin    else None,
            "especificaciones": s.especificaciones,
            "registrado":       s.id in registros_existentes,
            "valorada":         s.valoracion is not None,
        }
        for s in solicitudes
    ]
    return jsonify(resultado), 200


@solicitudes_bp.route("/proximas", methods=["GET"])
def get_proximas():
    """Solicitudes con horario_inicio en el futuro — vista pública."""
    ahora = datetime.utcnow()
    solicitudes = Solicitud.query.filter(
        Solicitud.horario_inicio > ahora
    ).order_by(Solicitud.horario_inicio).all()

    resultado = [
        {
            "id":             s.id,
            "nombre":         s.nombre,
            "especie":        s.especie,
            "raza":           s.raza,
            "foto_url":       s.foto_url,
            "horario_inicio": s.horario_inicio.isoformat() if s.horario_inicio else None,
            "horario_fin":    s.horario_fin.isoformat()    if s.horario_fin    else None,
            "especificaciones": s.especificaciones,
            "cuidador_id":    s.cuidador_id,
            "registrado":     False,  # se calcula en cliente si hace falta
        }
        for s in solicitudes
    ]
    return jsonify(resultado), 200


@solicitudes_bp.route("/", methods=["POST"])
def crear_solicitud():
    data = request.get_json()

    if not data or not all(k in data for k in ("usuario_id", "nombre", "especie")):
        return jsonify({"error": "Faltan campos: usuario_id, nombre, especie"}), 400

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


@solicitudes_bp.route("/<int:id>", methods=["PUT"])
def modificar_solicitud(id):
    data      = request.get_json()
    solicitud = Solicitud.query.get_or_404(id)

    usuario_id = data.get("usuario_id")
    if usuario_id is not None and solicitud.usuario_id != int(usuario_id):
        return jsonify({"error": "No tienes permiso para modificar esta solicitud"}), 403

    solicitud.nombre           = data.get("nombre",           solicitud.nombre)
    solicitud.especie          = data.get("especie",          solicitud.especie)
    solicitud.raza             = data.get("raza",             solicitud.raza)
    solicitud.foto_url         = data.get("foto_url",         solicitud.foto_url)
    solicitud.especificaciones = data.get("especificaciones", solicitud.especificaciones)
    solicitud.horario_inicio   = parse_dt(data.get("horario_inicio")) or solicitud.horario_inicio
    solicitud.horario_fin      = parse_dt(data.get("horario_fin"))    or solicitud.horario_fin

    db.session.commit()
    return jsonify({"mensaje": "Solicitud modificada"}), 200


@solicitudes_bp.route("/<int:id>", methods=["DELETE"])
def eliminar_solicitud(id):
    solicitud = Solicitud.query.get_or_404(id)
    db.session.delete(solicitud)
    db.session.commit()
    return jsonify({"mensaje": "Solicitud eliminada"}), 200


@solicitudes_bp.route("/<int:id>/registrarse", methods=["POST"])
def registrarse_solicitud(id):
    data       = request.get_json() or {}
    usuario_id = data.get("usuario_id")
    if usuario_id is None:
        return jsonify({"error": "usuario_id requerido"}), 400

    solicitud = Solicitud.query.get_or_404(id)
    if solicitud.usuario_id == int(usuario_id):
        return jsonify({"error": "No puedes registrarte en tu propia solicitud"}), 403
    if Inscripcion.query.filter_by(solicitud_id=id, usuario_id=usuario_id).first():
        return jsonify({"error": "Ya estás registrado en esta solicitud"}), 409

    db.session.add(Inscripcion(usuario_id=usuario_id, solicitud_id=id))
    db.session.commit()
    return jsonify({"mensaje": "Registro correcto"}), 201


@solicitudes_bp.route("/<int:id>/registrarse", methods=["DELETE"])
def cancelar_registro_solicitud(id):
    data       = request.get_json() or {}
    usuario_id = data.get("usuario_id")
    if usuario_id is None:
        return jsonify({"error": "usuario_id requerido"}), 400

    inscripcion = Inscripcion.query.filter_by(solicitud_id=id, usuario_id=usuario_id).first()
    if not inscripcion:
        return jsonify({"error": "No estás registrado en esta solicitud"}), 404

    db.session.delete(inscripcion)
    db.session.commit()
    return jsonify({"mensaje": "Registro cancelado"}), 200


@solicitudes_bp.route("/<int:id>/aceptar", methods=["POST"])
def aceptar_cuidador(id):
    data        = request.get_json() or {}
    usuario_id  = data.get("usuario_id")
    cuidador_id = data.get("cuidador_id")

    if not usuario_id or not cuidador_id:
        return jsonify({"error": "usuario_id y cuidador_id son obligatorios"}), 400

    solicitud = Solicitud.query.get_or_404(id)
    if solicitud.usuario_id != int(usuario_id):
        return jsonify({"error": "Solo el dueño puede aceptar un cuidador"}), 403
    if solicitud.cuidador_id is not None:
        return jsonify({"error": "Esta solicitud ya tiene cuidador asignado"}), 409
    if not Inscripcion.query.filter_by(solicitud_id=id, usuario_id=cuidador_id).first():
        return jsonify({"error": "Ese usuario no está inscrito en esta solicitud"}), 404

    solicitud.cuidador_id = int(cuidador_id)
    db.session.commit()
    return jsonify({"mensaje": "Cuidador aceptado correctamente"}), 200


@solicitudes_bp.route("/<int:id>/inscritos", methods=["GET"])
def get_inscritos(id):
    solicitud = Solicitud.query.get_or_404(id)
    return jsonify([
        {"usuario_id": ins.usuario_id, "username": ins.usuario.username}
        for ins in solicitud.inscripciones
    ]), 200
