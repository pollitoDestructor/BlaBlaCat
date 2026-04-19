from functools import wraps
from flask import Blueprint, request, jsonify
from ..extensions import db
from ..model.usuarios import Usuario, RolEnum
from ..model.solicitudes import Solicitud
from ..model.valoraciones import Valoracion
from ..model.interesados import Interesado

admin_bp = Blueprint("admin", __name__)


# ─── Decorador de protección (#276) ───────────────────────────────────────────

def require_admin(f):
    """
    Comprueba que el usuario que hace la petición existe y tiene rol administrador.
    Lee 'usuario_id' de query params (GET/DELETE) o del body JSON (POST/PUT).
    """
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


# ─── Tarea #276 — Ver todos los usuarios ──────────────────────────────────────

@admin_bp.route("/usuarios", methods=["GET"])
@require_admin
def listar_usuarios():
    """
    GET /api/admin/usuarios?usuario_id=<admin_id>
    Devuelve todos los usuarios registrados en el sistema.
    """
    usuarios = Usuario.query.all()
    resultado = [
        {
            "id":         u.id,
            "username":   u.username,
            "email":      u.email,
            "rol":        u.rol.value,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in usuarios
    ]
    return jsonify(resultado), 200


# ─── Tarea #298 — Eliminar usuario en cascada ─────────────────────────────────

@admin_bp.route("/usuarios/<int:id>", methods=["DELETE"])
@require_admin
def eliminar_usuario(id):
    """
    DELETE /api/admin/usuarios/<id>?usuario_id=<admin_id>
    Elimina un usuario y todos sus datos asociados:
      - Valoraciones recibidas y dadas
      - Candidaturas (Interesado)
      - Solicitudes propias (y sus interesados en cascada)
      - Desvincula solicitudes donde era cuidador confirmado
    """
    usuario = db.session.get(Usuario, id)

    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    admin_id = int(
        request.args.get("usuario_id") or
        (request.get_json(silent=True) or {}).get("usuario_id")
    )
    if usuario.id == admin_id:
        return jsonify({"error": "Un administrador no puede eliminarse a sí mismo"}), 400

    # 1. Desvincular solicitudes donde era cuidador confirmado (SET NULL)
    Solicitud.query.filter_by(id_cuidador_confirmado=id).update(
        {"id_cuidador_confirmado": None}
    )

    # 2. Borrar valoraciones (recibidas y dadas)
    Valoracion.query.filter(
        (Valoracion.id_usuario_evaluado == id) |
        (Valoracion.id_usuario_autor == id)
    ).delete()

    # 3. Borrar candidaturas del usuario a solicitudes ajenas
    Interesado.query.filter_by(id_usuario_postulante=id).delete()

    # 4. Borrar solicitudes propias
    #    → sus interesados se eliminan en cascada (cascade="all, delete-orphan")
    for solicitud in usuario.solicitudes_creadas:
        db.session.delete(solicitud)

    # 5. Borrar el usuario
    db.session.delete(usuario)
    db.session.commit()

    return jsonify({"mensaje": f"Usuario {id} eliminado correctamente"}), 200


# ─── Tarea #300 — Ver catálogo completo de mascotas/solicitudes ───────────────

@admin_bp.route("/solicitudes", methods=["GET"])
@require_admin
def listar_todas_solicitudes():
    """
    GET /api/admin/solicitudes?usuario_id=<admin_id>
    Devuelve TODAS las solicitudes del sistema, sin filtro de fecha,
    con los datos de la mascota embebidos.
    """
    solicitudes = Solicitud.query.order_by(Solicitud.created_at.desc()).all()
    resultado = [
        {
            "id":                     s.id,
            "nombre":                 s.nombre,
            "especie":                s.especie,
            "raza":                   s.raza,
            "foto_url":               s.foto_url,
            "horario_inicio":         s.horario_inicio.isoformat() if s.horario_inicio else None,
            "horario_fin":            s.horario_fin.isoformat()    if s.horario_fin    else None,
            "especificaciones":       s.especificaciones,
            "usuario_id":             s.usuario_id,
            "usuario_username":       s.usuario.username if s.usuario else None,
            "cuidador_confirmado_id": s.id_cuidador_confirmado,
            "created_at":             s.created_at.isoformat() if s.created_at else None,
        }
        for s in solicitudes
    ]
    return jsonify(resultado), 200