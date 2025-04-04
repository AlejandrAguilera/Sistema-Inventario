from flask import Blueprint, render_template, request, redirect, url_for
from models.models import Usuario
from models import db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Lógica de autenticación
        pass
    return render_template('login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Lógica de registro
        pass
    return render_template('register.html')
