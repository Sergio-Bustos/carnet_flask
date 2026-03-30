from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Aprendiz(db.Model):
    __tablename__ = 'aprendices'
    
    id = db.Column(db.Integer, primary_key=True)
    nis = db.Column(db.String(20), nullable=False, unique=True)
    primer_apellido = db.Column(db.String(100), nullable=False)
    segundo_apellido = db.Column(db.String(100), nullable=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo_documento = db.Column(db.String(20), nullable=False, default='CC')
    numero_documento = db.Column(db.String(20), nullable=False, unique=True)
    tipo_sangre = db.Column(db.String(5), nullable=False, default='O+')
    nombre_programa = db.Column(db.String(200), nullable=False)
    codigo_ficha = db.Column(db.String(20), nullable=False)
    centro_red_tecnologica = db.Column(db.String(200), nullable=False)
    fecha_finalizacion_programa = db.Column(db.Date, nullable=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Aprendiz {self.nombre} {self.primer_apellido}>'