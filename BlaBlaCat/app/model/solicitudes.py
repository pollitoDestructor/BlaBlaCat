from ..extensions import db
from datetime import datetime


class Solicitud(db.Model):
    __tablename__ = "solicitudes"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ── Datos de la mascota (embebidos, sin tabla propia) ──
    nombre = db.Column(db.String(100), nullable=False)  # nombre de la mascota
    especie = db.Column(db.String(50), nullable=False)
    raza = db.Column(db.String(50), nullable=True)
    foto_url = db.Column(db.String(255), nullable=True)

    # ── Datos del cuidado ──────────────────────────────────
    horario_inicio = db.Column(db.DateTime, nullable=False)
    horario_fin = db.Column(db.DateTime, nullable=False)
    especificaciones = db.Column(db.Text, nullable=True)

    # ── Relaciones ─────────────────────────────────────────
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    usuario = db.relationship("Usuario", foreign_keys=[usuario_id],
                              back_populates="solicitudes_creadas")

    id_cuidador_confirmado = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    cuidador_confirmado = db.relationship("Usuario", foreign_keys=[id_cuidador_confirmado],
                                          back_populates="solicitudes_confirmadas")

    interesados = db.relationship("Interesado", back_populates="solicitud",
                                  cascade="all, delete-orphan", lazy=True)

    def __repr__(self):
        return f"<Solicitud {self.id} — {self.nombre}>"