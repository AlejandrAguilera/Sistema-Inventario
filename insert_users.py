from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import MySQLdb

# Conecta la BD
db = MySQLdb.connect(host="localhost", user="tu_usuario", passwd="tu_contraseña", db="inventario")
cursor = db.cursor()
bcrypt = Bcrypt()

# Insertar usuarios con contraseñas encriptadas
usuarios = [
    ("admin", bcrypt.generate_password_hash("admin123").decode('utf-8'), "admin"),
    ("almacenista", bcrypt.generate_password_hash("almacen123").decode('utf-8'), "almacenista")
]

for usuario in usuarios:
    cursor.execute("INSERT INTO usuarios (nombre, password, rol) VALUES (%s, %s, %s)", usuario)  # Cambia 'usuario' por 'nombre'

db.commit()
db.close()

print("Usuarios insertados correctamente con contraseñas encriptadas.")
