from ..extensions import db
from datetime import datetime

class Valoracion(db.Model):
    __tablename__ = "valoraciones"

    id         = db.Column(db.Integer, primary_key=True)
    puntuacion = db.Column(db.Integer, nullable=False)   # 1-5
    comentario = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Solicitud a la que pertenece (una valoración por solicitud)
    solicitud_id = db.Column(db.Integer, db.ForeignKey("solicitudes.id"),
                             nullable=False, unique=True)
    solicitud    = db.relationship("Solicitud", back_populates="valoracion")

    # Quién escribe (siempre el dueño)
    autor_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    autor    = db.relationship("Usuario", foreign_keys=[autor_id])

    def __repr__(self):
        return f"<Valoracion solicitud={self.solicitud_id}>"
