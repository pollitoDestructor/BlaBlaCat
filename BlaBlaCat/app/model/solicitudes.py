from ..extensions import db
from datetime import datetime

class Solicitud(db.Model):
    __tablename__ = "solicitudes"

    id         = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Clave foránea al usuario que hace la solicitud
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    usuario    = db.relationship("Usuario", back_populates="solicitudes")

    def __repr__(self):
        return f"<Solicitud {self.id}>"