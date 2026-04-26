from ..extensions import db
from datetime import datetime

class Inscripcion(db.Model):
    __tablename__ = "inscripciones"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    solicitud_id = db.Column(db.Integer, db.ForeignKey("solicitudes.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship("Usuario", back_populates="inscripciones")
    solicitud = db.relationship("Solicitud", back_populates="inscripciones")

    def __repr__(self):
        return f"<Inscripcion {self.id} usuario={self.usuario_id} solicitud={self.solicitud_id}>"