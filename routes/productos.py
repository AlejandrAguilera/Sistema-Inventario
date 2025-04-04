from flask import Blueprint, render_template, request
from models.models import Producto
from models import db

bp = Blueprint('productos', __name__, url_prefix='/productos')

@bp.route('/')
def index():
    productos = Producto.query.all()
    return render_template('productos/index.html', productos=productos)

@bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        pass
    return render_template('productos/add.html')
