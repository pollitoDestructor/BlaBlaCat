# app/routes/usuarios.py
from flask import Blueprint, jsonify, request
from ..extensions import db
from ..model.usuarios import Usuario
from ..model.solicitudes import Solicitud
from ..model.valoraciones import Valoracion

usuarios_bp = Blueprint("usuarios", __name__)


@usuarios_bp.route("/", methods=["GET"])
def get_usuarios():
    """Todos los usuarios con su valoración media como cuidador."""
    usuarios = Usuario.query.all()
    resultado = []
    for u in usuarios:
        valoraciones = (
            db.session.query(Valoracion)
            .join(Solicitud, Valoracion.solicitud_id == Solicitud.id)
            .filter(Solicitud.cuidador_id == u.id)
            .all()
        )
        puntuaciones = [v.puntuacion for v in valoraciones]
        media = round(sum(puntuaciones) / len(puntuaciones), 1) if puntuaciones else None
        resultado.append({
            "id":               u.id,
            "username":         u.username,
            "media":            media,
            "num_valoraciones": len(puntuaciones),
        })
    return jsonify(resultado), 200


@usuarios_bp.route("/<int:id>", methods=["GET"])
def get_perfil(id):
    """Perfil de un usuario con todas sus valoraciones recibidas como cuidador."""
    usuario = Usuario.query.get_or_404(id)

    valoraciones_recibidas = (
        db.session.query(Valoracion)
        .join(Solicitud, Valoracion.solicitud_id == Solicitud.id)
        .filter(Solicitud.cuidador_id == id)
        .all()
    )

    valoraciones = [
        {
            "id":           v.id,
            "puntuacion":   v.puntuacion,
            "comentario":   v.comentario,
            "autor":        v.autor.username,
            "autor_id":     v.autor_id,
            "solicitud_id": v.solicitud_id,
            "created_at":   v.created_at.isoformat(),
        }
        for v in valoraciones_recibidas
    ]

    media = (
        round(sum(v["puntuacion"] for v in valoraciones) / len(valoraciones), 1)
        if valoraciones else None
    )

    return jsonify({
        "id":           usuario.id,
        "username":     usuario.username,
        "media":        media,
        "valoraciones": valoraciones,
    }), 200


@usuarios_bp.route("/<int:id>/valoraciones", methods=["POST"])
def crear_valoracion(id):
    """El dueño valora al cuidador de una solicitud concreta."""
    data = request.get_json()
    autor_id     = data.get("autor_id")
    solicitud_id = data.get("solicitud_id")

    if not autor_id or not solicitud_id:
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    solicitud = Solicitud.query.get_or_404(solicitud_id)

    if not solicitud.cuidador_id:
        return jsonify({"error": "Esta solicitud aún no tiene cuidador aceptado"}), 400

    if int(autor_id) != solicitud.usuario_id:
        return jsonify({"error": "Solo el dueño puede valorar esta solicitud"}), 403

    if id != solicitud.cuidador_id:
        return jsonify({"error": "Solo puedes valorar al cuidador de esta solicitud"}), 403

    if solicitud.valoracion:
        return jsonify({"error": "Esta solicitud ya ha sido valorada"}), 409

    puntuacion = data.get("puntuacion")
    comentario = data.get("comentario", "").strip()

    if not puntuacion or not comentario:
        return jsonify({"error": "Puntuación y comentario son obligatorios"}), 400

    if not (1 <= int(puntuacion) <= 5):
        return jsonify({"error": "La puntuación debe ser entre 1 y 5"}), 400

    nueva = Valoracion(
        solicitud_id = solicitud_id,
        autor_id     = int(autor_id),
        puntuacion   = int(puntuacion),
        comentario   = comentario,
    )
    db.session.add(nueva)
    db.session.commit()

    return jsonify({"mensaje": "Valoración creada", "id": nueva.id}), 201
