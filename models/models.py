from . import db

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Producto(db.Model):
    __tablename__ = 'produtos'  # Cambia el nombre de la tabla a 'produtos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    estatus = db.Column(db.String(10), nullable=False, default='Activo')

class Movimiento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)  # Actualiza la referencia a 'produtos'
    tipo = db.Column(db.String(50), nullable=False)  # Entrada o Salida
    cantidad = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
