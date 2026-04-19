from ..extensions import db


class Interesado(db.Model):
    __tablename__ = "interesados"

    id = db.Column(db.Integer, primary_key=True)
    id_solicitud = db.Column(db.Integer, db.ForeignKey("solicitudes.id"), nullable=False)
    id_usuario_postulante = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    # Relaciones
    solicitud = db.relationship("Solicitud", back_populates="interesados")
    usuario_postulante = db.relationship("Usuario", back_populates="candidaturas")

    # Un usuario no puede apuntarse dos veces a la misma solicitud
    __table_args__ = (
        db.UniqueConstraint("id_solicitud", "id_usuario_postulante", name="uq_interesado"),
    )

    def __repr__(self):
        return f"<Interesado usuario={self.id_usuario_postulante} solicitud={self.id_solicitud}>"