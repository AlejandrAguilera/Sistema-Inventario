from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.models import Producto, Movimiento, Usuario  # Ensure Usuario is imported
from models import db
from datetime import datetime

bp = Blueprint('inventario', __name__, url_prefix='/inventario')

# Verifica si el usuario es administrador
def admin_required(func):
    def wrapper(*args, **kwargs):
        if current_user.rol != 'admin':
            flash('Acceso denegado: Solo los administradores pueden acceder a esta página.', 'danger')
            return redirect(url_for('inventario.listar_productos'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# Verifica si el usuario es almacenista
def almacenista_required(func):
    def wrapper(*args, **kwargs):
        if current_user.rol not in ['admin', 'almacenista']:
            flash('Acceso denegado: Solo los almacenistas o administradores pueden acceder a esta página.', 'danger')
            return redirect(url_for('dashboard'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# Ruta para listar productos (acceso para almacenistas y administradores)
@bp.route('/productos')
@login_required
@almacenista_required
def listar_productos():
    productos = Producto.query.all()
    return render_template('inventario/productos.html', productos=productos)

# Ruta para agregar un producto (solo administradores)
@bp.route('/productos/agregar', methods=['GET', 'POST'])
@login_required
@admin_required
def agregar_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        cantidad = int(request.form['cantidad'])
        precio = float(request.form['precio'])

        nuevo_producto = Producto(nombre=nombre, cantidad=cantidad)
        db.session.add(nuevo_producto)
        db.session.commit()

        flash('Producto agregado correctamente', 'success')
        return redirect(url_for('inventario.listar_productos'))

    return render_template('inventario/agregar_producto.html')

# Ruta para dar de baja un producto (solo administradores)
@bp.route('/productos/baja/<int:producto_id>', methods=['POST'])
@login_required
@admin_required
def dar_baja_producto(producto_id):
    producto = Producto.query.get(producto_id)
    if producto:
        producto.estatus = 'Inactivo'
        db.session.commit()
        flash(f'El producto "{producto.nombre}" ha sido dado de baja.', 'success')
    else:
        flash('Producto no encontrado.', 'danger')
    return redirect(url_for('inventario.listar_productos'))

# Ruta para reactivar un producto (solo administradores)
@bp.route('/productos/reactivar/<int:producto_id>', methods=['POST'])
@login_required
@admin_required
def reactivar_producto(producto_id):
    producto = Producto.query.get(producto_id)
    if producto:
        producto.estatus = 'Activo'
        db.session.commit()
        flash(f'El producto "{producto.nombre}" ha sido reactivado.', 'success')
    else:
        flash('Producto no encontrado.', 'danger')
    return redirect(url_for('inventario.listar_productos'))

# Ruta para eliminar un producto (solo administradores)
@bp.route('/productos/eliminar/<int:producto_id>', methods=['POST'])
@login_required
@admin_required
def eliminar_producto(producto_id):
    producto = Producto.query.get(producto_id)
    if producto:
        db.session.delete(producto)
        db.session.commit()
        flash(f'El producto "{producto.nombre}" ha sido eliminado.', 'success')
    else:
        flash('Producto no encontrado.', 'danger')
    return redirect(url_for('inventario.listar_productos'))

# Ruta para cambiar el estatus de un producto (activo/inactivo)
@bp.route('/productos/cambiar_estatus/<int:producto_id>', methods=['POST'])
@login_required
@admin_required
def cambiar_estatus(producto_id):
    producto = Producto.query.get(producto_id)
    if producto:
        producto.estatus = 'Inactivo' if producto.estatus == 'Activo' else 'Activo'
        db.session.commit()
        flash(f'El estatus del producto "{producto.nombre}" ha sido cambiado a {producto.estatus}.', 'success')
    else:
        flash('Producto no encontrado.', 'danger')
    return redirect(url_for('inventario.listar_productos'))

# Ruta para registrar una salida (almacenistas y administradores)
@bp.route('/movimientos', methods=['GET', 'POST'])
@login_required
@almacenista_required
def registrar_movimiento():
    if request.method == 'POST':
        producto_id = int(request.form['producto_id'])
        tipo = request.form['tipo']  # Solo "Salida" permitida para almacenistas
        cantidad = int(request.form['cantidad'])

        if current_user.rol == 'almacenista' and tipo != 'Salida':
            flash('Acceso denegado: Los almacenistas solo pueden registrar salidas.', 'danger')
            return redirect(url_for('inventario.listar_productos'))

        producto = Producto.query.get(producto_id)
        if not producto:
            flash('Producto no encontrado', 'danger')
            return redirect(url_for('inventario.listar_productos'))

        if tipo == 'Salida' and producto.cantidad < cantidad:
            flash('No hay suficiente stock para realizar la salida', 'danger')
            return redirect(url_for('inventario.listar_productos'))

        # Actualizar cantidad del producto
        if tipo == 'Salida':
            producto.cantidad -= cantidad

        # Registrar movimiento
        movimiento = Movimiento(
            producto_id=producto_id,
            tipo=tipo,
            cantidad=cantidad,
            fecha=datetime.now()
        )
        db.session.add(movimiento)
        db.session.commit()

        flash(f'Movimiento de {tipo} registrado correctamente', 'success')
        return redirect(url_for('inventario.listar_productos'))

    productos = Producto.query.all()
    return render_template('inventario/movimientos.html', productos=productos)

# Ruta para registrar un movimiento (entrada o salida)
@bp.route('/movimiento/<tipo>/<int:producto_id>', methods=['POST'])
@login_required
@almacenista_required
def movimiento(tipo, producto_id):
    cantidad = int(request.form['cantidad'])
    producto = Producto.query.get(producto_id)

    if not producto:
        flash('Producto no encontrado.', 'danger')
        return redirect(url_for('inventario.listar_productos'))

    if tipo == 'entrada':
        producto.cantidad += cantidad
    elif tipo == 'salida':
        if cantidad > producto.cantidad:
            flash('No puedes sacar más productos de los que hay en inventario.', 'danger')
            return redirect(url_for('inventario.listar_productos'))
        producto.cantidad -= cantidad

    # Registrar movimiento
    movimiento = Movimiento(
        producto_id=producto_id,
        tipo=tipo,
        cantidad=cantidad,
        fecha=datetime.now()
    )
    db.session.add(movimiento)
    db.session.commit()

    flash(f'Movimiento de {tipo} registrado correctamente.', 'success')
    return redirect(url_for('inventario.listar_productos'))

# Ruta para ver el historial de movimientos (solo administradores)
@bp.route('/movimientos')
@login_required
@admin_required
def ver_movimientos():
    filtro = request.args.get('filtro')  # Puede ser 'entrada', 'salida' o None

    # Filtrar movimientos según el tipo (entrada, salida o todos)
    query = db.session.query(
        Movimiento.id,
        Producto.nombre,
        Movimiento.tipo,
        Movimiento.cantidad,
        Movimiento.fecha,
        Movimiento.usuario_id  # Incluye el ID del usuario
    ).join(Producto, Movimiento.producto_id == Producto.id)

    if filtro == 'entrada':
        movimientos = query.filter(Movimiento.tipo == 'entrada', Producto.estatus == 'Activo').order_by(Movimiento.fecha.desc()).all()
    elif filtro == 'salida':
        movimientos = query.filter(Movimiento.tipo == 'salida', Producto.estatus == 'Inactivo').order_by(Movimiento.fecha.desc()).all()
    else:
        movimientos = query.order_by(Movimiento.fecha.desc()).all()

    # Obtener los nombres de los usuarios
    usuarios = {usuario.id: usuario.username for usuario in db.session.query(Usuario).all()}
    movimientos = [
        (m.id, m.nombre, m.tipo, m.cantidad, m.fecha, usuarios.get(m.usuario_id, "Desconocido"))
        for m in movimientos
    ]

    return render_template('inventario/movimientos.html', movimientos=movimientos, filtro=filtro)
