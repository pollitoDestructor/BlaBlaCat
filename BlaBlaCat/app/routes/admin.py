from functools import wraps
from flask import Blueprint, request, jsonify
from ..extensions import db
from ..model.usuarios import Usuario, RolEnum
from ..model.solicitudes import Solicitud
from ..model.valoraciones import Valoracion
from ..model.inscripciones import Inscripcion

admin_bp = Blueprint("admin", __name__)


def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        uid = request.args.get("usuario_id") or (
            request.get_json(silent=True) or {}
        ).get("usuario_id")
        if not uid:
            return jsonify({"error": "Se requiere usuario_id"}), 401
        usuario = db.session.get(Usuario, int(uid))
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404
        if not usuario.es_admin():
            return jsonify({"error": "Acceso restringido a administradores"}), 403
        return f(*args, **kwargs)
    return decorated


@admin_bp.route("/usuarios", methods=["GET"])
@require_admin
def listar_usuarios():
    usuarios = Usuario.query.all()
    return jsonify([
        {
            "id":         u.id,
            "username":   u.username,
            "email":      u.email,
            "rol":        u.rol.value,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in usuarios
    ]), 200


@admin_bp.route("/usuarios/<int:id>", methods=["DELETE"])
@require_admin
def eliminar_usuario(id):
    usuario = db.session.get(Usuario, id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    admin_id = int(
        request.args.get("usuario_id") or
        (request.get_json(silent=True) or {}).get("usuario_id")
    )
    if usuario.id == admin_id:
        return jsonify({"error": "Un administrador no puede eliminarse a sí mismo"}), 400

    # SET NULL en solicitudes donde era cuidador
    Solicitud.query.filter_by(cuidador_id=id).update({"cuidador_id": None})

    # Borrar valoraciones
    Valoracion.query.filter(
        (Valoracion.autor_id == id)
    ).delete()
    # Valoraciones donde era el evaluado (por solicitudes propias) se borran en cascada

    # Borrar inscripciones del usuario
    Inscripcion.query.filter_by(usuario_id=id).delete()

    # Borrar solicitudes propias (inscripciones en cascada)
    for s in usuario.solicitudes:
        db.session.delete(s)

    db.session.delete(usuario)
    db.session.commit()
    return jsonify({"mensaje": f"Usuario {id} eliminado correctamente"}), 200


@admin_bp.route("/solicitudes", methods=["GET"])
@require_admin
def listar_todas_solicitudes():
    solicitudes = Solicitud.query.order_by(Solicitud.created_at.desc()).all()
    return jsonify([
        {
            "id":               s.id,
            "nombre":           s.nombre,
            "especie":          s.especie,
            "raza":             s.raza,
            "foto_url":         s.foto_url,
            "horario_inicio":   s.horario_inicio.isoformat() if s.horario_inicio else None,
            "horario_fin":      s.horario_fin.isoformat()    if s.horario_fin    else None,
            "especificaciones": s.especificaciones,
            "usuario_id":       s.usuario_id,
            "usuario_username": s.usuario.username if s.usuario else None,
            "cuidador_id":      s.cuidador_id,
            "created_at":       s.created_at.isoformat() if s.created_at else None,
        }
        for s in solicitudes
    ]), 200
