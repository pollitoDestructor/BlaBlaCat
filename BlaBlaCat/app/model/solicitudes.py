from ..extensions import db
from datetime import datetime

class Solicitud(db.Model):
    __tablename__ = "solicitudes"

    id         = db.Column(db.Integer, primary_key=True)
    nombre     = db.Column(db.String(20), nullable=False)
    especie    = db.Column(db.String(20), nullable=False)
    raza       = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Dueño de la mascota
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    usuario    = db.relationship("Usuario", back_populates="solicitudes",
                                 foreign_keys=[usuario_id])

    # Cuidador aceptado (se rellena cuando el dueño acepta una inscripción)
    cuidador_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)

    inscripciones = db.relationship("Inscripcion", back_populates="solicitud", lazy=True)

    # Valoración ligada (máximo una)
    valoracion = db.relationship("Valoracion", back_populates="solicitud", uselist=False)

    def __repr__(self):
        return f"<Solicitud {self.id}>"
