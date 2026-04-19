from ..extensions import db
from sqlalchemy import CheckConstraint


class Valoracion(db.Model):
    __tablename__ = "valoraciones"

    id = db.Column(db.Integer, primary_key=True)
    id_usuario_evaluado = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    id_usuario_autor = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    estrellas = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.Text, nullable=True)

    # Relaciones
    usuario_evaluado = db.relationship("Usuario", foreign_keys=[id_usuario_evaluado],
                                       back_populates="valoraciones_recibidas")
    usuario_autor = db.relationship("Usuario", foreign_keys=[id_usuario_autor],
                                    back_populates="valoraciones_dadas")

    __table_args__ = (
        CheckConstraint("estrellas >= 0 AND estrellas <= 5", name="ck_estrellas_rango"),
        # Un autor solo puede valorar una vez a cada usuario
        db.UniqueConstraint("id_usuario_evaluado", "id_usuario_autor", name="uq_valoracion"),
    )

    def __repr__(self):
        return f"<Valoracion {self.estrellas}★ de {self.id_usuario_autor} a {self.id_usuario_evaluado}>"