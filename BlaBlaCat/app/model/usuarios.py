from ..extensions import db
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = "usuarios"

    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80), unique=True, nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Un usuario puede tener varias solicitudes
    solicitudes = db.relationship("Solicitud", back_populates="usuario", lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"