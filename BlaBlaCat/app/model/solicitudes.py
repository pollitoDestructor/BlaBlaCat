from ..extensions import db
from datetime import datetime


class Solicitud(db.Model):
    __tablename__ = "solicitudes"

    id         = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Datos de la mascota
    nombre           = db.Column(db.String(100), nullable=False)
    especie          = db.Column(db.String(50),  nullable=False)
    raza             = db.Column(db.String(50),  nullable=True)
    foto_url         = db.Column(db.String(255), nullable=True)

    # Datos del cuidado
    horario_inicio   = db.Column(db.DateTime, nullable=True)
    horario_fin      = db.Column(db.DateTime, nullable=True)
    especificaciones = db.Column(db.Text, nullable=True)

    # Dueño de la mascota
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    usuario    = db.relationship("Usuario", foreign_keys=[usuario_id],
                                 back_populates="solicitudes")

    # Cuidador aceptado
    cuidador_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)

    # Inscripciones de candidatos
    inscripciones = db.relationship("Inscripcion", back_populates="solicitud", lazy=True,
                                    cascade="all, delete-orphan")

    # Valoración (máximo una)
    valoracion = db.relationship("Valoracion", back_populates="solicitud", uselist=False)

    def __repr__(self):
        return f"<Solicitud {self.id} — {self.nombre}>"
