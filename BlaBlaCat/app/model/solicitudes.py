from ..extensions import db
from datetime import datetime

class Solicitud(db.Model):
    __tablename__ = "solicitudes"

    id         = db.Column(db.Integer, primary_key=True)
    nombre     = db.Column(db.String(20), nullable = False)
    especie    = db.Column(db.String(20), nullable = False)
    raza       = db.Column(db.String(20), nullable = True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Clave foránea al usuario que hace la solicitud
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    usuario    = db.relationship("Usuario", back_populates="solicitudes")

    def __repr__(self):
        return f"<Solicitud {self.id}>"