from flask import Blueprint, render_template, request
from models.models import Producto
from models import db

bp = Blueprint('movimientos', __name__, url_prefix='/movimientos')

@bp.route('/')
def index():
    filtro = request.args.get('filtro')  # Puede ser 'activo', 'inactivo' o None

    # Filtrar productos según el estatus
    if filtro == 'activo':
        productos = Producto.query.filter_by(estatus='Activo').all()
    elif filtro == 'inactivo':
        productos = Producto.query.filter_by(estatus='Inactivo').all()
    else:
        productos = Producto.query.all()

    return render_template('movimientos/index.html', productos=productos, filtro=filtro)

@bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        # Lógica para agregar movimiento
        pass
    return render_template('movimientos/add.html')
