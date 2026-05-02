from ..extensions import db
from datetime import datetime
import enum


class RolEnum(enum.Enum):
    estandar      = "estandar"
    administrador = "administrador"


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id                = db.Column(db.Integer, primary_key=True)
    username          = db.Column(db.String(80),  unique=True, nullable=False)
    email             = db.Column(db.String(120), unique=True, nullable=False)
    password          = db.Column(db.String(256), nullable=False)
    rol               = db.Column(db.Enum(RolEnum), nullable=False, default=RolEnum.estandar)
    asignacion_manual = db.Column(db.Boolean, default=False)
    created_at        = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    solicitudes   = db.relationship("Solicitud", foreign_keys="Solicitud.usuario_id",
                                    back_populates="usuario", lazy=True)
    inscripciones = db.relationship("Inscripcion", back_populates="usuario", lazy=True)

    def es_admin(self):
        return self.rol == RolEnum.administrador

    def __repr__(self):
        return f"<Usuario {self.username} [{self.rol.value}]>"
