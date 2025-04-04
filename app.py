from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from models import db 
from routes import inventario

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

# Configuración de MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  
app.config['MYSQL_PASSWORD'] = 'cristo123' 
app.config['MYSQL_DB'] = 'inventario_db'

# Configuración de SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventario.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

mysql = MySQL(app)
bcrypt = Bcrypt(app)

# Inicializar SQLAlchemy
db.init_app(app)

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Modelo de usuario
class User(UserMixin):
    def __init__(self, id, usuario, rol):
        self.id = id
        self.usuario = usuario
        self.rol = rol

@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    if user:
        return User(id=user[0], usuario=user[1], rol=user[3])
    return None

# Ruta para el inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena'] 

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE nombre = %s", (usuario,))
        user = cur.fetchone()
        cur.close()

        if user:
            usuario_obj = User(id=user[0], usuario=user[1], rol=user[3])
            login_user(usuario_obj)

            # Redirige según el rol del usuario
            if user[3] == "admin":
                flash('Inicio de sesión exitoso como Administrador', 'success')
                return redirect(url_for('dashboard'))
            elif user[3] == "almacenista":
                flash('Inicio de sesión exitoso como Almacenista', 'success')
                return redirect(url_for('inventario.listar_productos'))
            else:
                flash('Rol no autorizado', 'danger')
                return redirect(url_for('login'))
        else:
            flash('Usuario no encontrado', 'danger')

    return render_template('login.html')

# Ruta para el registro de usuarios
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.rol != 'admin':
        flash('Acceso denegado: Solo los administradores pueden acceder al dashboard.', 'danger')
        return redirect(url_for('login'))
    return render_template('dashboard.html', usuario=current_user.usuario)

# Ruta para salir de la sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('login'))

@app.route('/productos')
@login_required
def productos():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, nombre, precio, estatus FROM productos")
    data = cur.fetchall()
    cur.close()
    return render_template('productos.html', productos=data)

app.register_blueprint(inventario.bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

@app.route('/inventario')
@login_required
def inventario():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM productos")
    productos = cur.fetchall()
    cur.close()
    return render_template('inventario.html', productos=productos)

@app.route('/agregar_producto', methods=['GET', 'POST'])
@login_required
def agregar_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = float(request.form['precio'])
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO productos (nombre, descripcion, precio, cantidad, estatus) VALUES (%s, %s, %s, %s, %s)",
                    (nombre, descripcion, precio, 0, 'Activo'))
        mysql.connection.commit()
        cur.close()
        flash('Producto agregado correctamente', 'success')
        return redirect(url_for('inventario'))
    return render_template('agregar_producto.html')

@app.route('/movimiento/<tipo>/<int:producto_id>', methods=['POST'])
@login_required
def movimiento(tipo, producto_id):
    cantidad = int(request.form['cantidad'])
    cur = mysql.connection.cursor()
    cur.execute("SELECT cantidad FROM productos WHERE id = %s", (producto_id,))
    actual = cur.fetchone()[0]

    if tipo == 'entrada':
        nueva_cantidad = actual + cantidad
    elif tipo == 'salida':
        if cantidad > actual:
            flash('No puedes sacar más productos de los que hay en inventario', 'danger')
            return redirect(url_for('inventario'))
        nueva_cantidad = actual - cantidad

    # Actualiza inventario
    cur.execute("UPDATE productos SET cantidad = %s WHERE id = %s", (nueva_cantidad, producto_id))
    
    # Inserta en historial de movimientos
    cur.execute("INSERT INTO movimientos (producto_id, tipo, cantidad, usuario_id) VALUES (%s, %s, %s, %s)",
                (producto_id, tipo, cantidad, current_user.id))
    mysql.connection.commit()
    cur.close()
    flash(f'Movimiento de {tipo} registrado correctamente', 'success')
    return redirect(url_for('inventario'))

@app.route('/cambiar_estatus/<int:producto_id>', methods=['POST'])
@login_required
def cambiar_estatus(producto_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT estatus FROM productos WHERE id = %s", (producto_id,))
    estatus_actual = cur.fetchone()[0]

    nuevo_estatus = 'Inactivo' if estatus_actual == 'Activo' else 'Activo'
    cur.execute("UPDATE productos SET estatus = %s WHERE id = %s", (nuevo_estatus, producto_id))
    mysql.connection.commit()
    cur.close()
    flash(f"Estatus del producto cambiado a {nuevo_estatus}", 'success')
    return redirect(url_for('inventario'))

@app.route('/movimientos', methods=['GET'])
@login_required
def movimientos():
    filtro = request.args.get('filtro', '')  # 'entrada', 'salida' o ''
    cur = mysql.connection.cursor()

    query = """
        SELECT m.id, p.nombre AS producto_nombre, m.tipo AS tipo_movimiento, 
               m.cantidad, DATE_FORMAT(m.fecha, '%%d/%%m/%%Y %%H:%%i') AS fecha_hora, 
               u.username AS usuario_nombre
        FROM movimientos m
        JOIN produtos p ON m.producto_id = p.id
        JOIN usuarios u ON m.usuario_id = u.id
    """

    if filtro in ['entrada', 'salida']:
        query += " WHERE m.tipo = %s ORDER BY m.fecha DESC"
        cur.execute(query, (filtro,))
    else:
        query += " ORDER BY m.fecha DESC"
        cur.execute(query)

    movimientos = cur.fetchall()
    cur.close()

    return render_template('movimientos/index.html', movimientos=movimientos, filtro=filtro)

@app.route('/historial')
def historial():
    filtro = request.args.get('filtro', '')  # 'activo', 'inactivo' o ''
    cur = mysql.connection.cursor()

    # Consulta para obtener productos según el filtro
    if filtro == 'activo':
        cur.execute("SELECT id, nombre, cantidad, estatus FROM productos WHERE estatus = 'Activo'")
    elif filtro == 'inactivo':
        cur.execute("SELECT id, nombre, cantidad, estatus FROM productos WHERE estatus = 'Inactivo'")
    else:
        cur.execute("SELECT id, nombre, cantidad, estatus FROM productos")

    productos = cur.fetchall()
    cur.close()

    # Verifica si los datos se obtienen correctamente
    print("Productos obtenidos:", productos)

    return render_template('historial.html', productos=productos, filtro=filtro)

@app.route('/prueba_historial')
def prueba_historial():
    # Datos de prueba
    movimientos = [
        (1, "Producto A", "entrada", 10, "01/01/2023 10:00", "admin"),
        (2, "Producto B", "salida", 5, "02/01/2023 15:30", "admin"),
        (3, "Producto C", "entrada", 20, "03/01/2023 12:00", "admin")
    ]
    filtro = request.args.get('filtro', '')  # 'entrada', 'salida' o ''
    
    # Filtrar los datos de prueba según el filtro
    if filtro == 'entrada':
        movimientos = [m for m in movimientos if m[2] == 'entrada']
    elif filtro == 'salida':
        movimientos = [m for m in movimientos if m[2] == 'salida']

    return render_template('historial.html', movimientos=movimientos, filtro=filtro)
