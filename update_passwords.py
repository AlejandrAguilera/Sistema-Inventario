from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from app import app

# Inicializa MySQL y Bcrypt
mysql = MySQL(app)
bcrypt = Bcrypt(app) 

def is_valid_bcrypt_hash(password):
    try:
        # Comprueba que el hash es valido
        bcrypt.check_password_hash(password, "test")
        return True
    except (ValueError, TypeError):
        return False

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute("SELECT idUsuario, password FROM usuarios")
    usuarios = cur.fetchall()

    for usuario in usuarios:
        user_id, password = usuario
        if not is_valid_bcrypt_hash(password):
            # Genera un nuevo hash para la contraseña
            hashed_password = bcrypt.generate_password_hash("default_password").decode('utf-8')  # Usa una contraseña predeterminada
            cur.execute("UPDATE usuarios SET password = %s WHERE idUsuario = %s", (hashed_password, user_id))
            print(f"Contraseña actualizada para el usuario con ID {user_id}")

    mysql.connection.commit()
    cur.close()
