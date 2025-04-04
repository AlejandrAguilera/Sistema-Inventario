from app import app
from models import db, Producto

with app.app_context():
    # Verifica si la columna "estatus" existe en la tabla "produtos"
    inspector = db.inspect(db.engine)
    columns = [column['name'] for column in inspector.get_columns('produtos')]

    if 'estatus' not in columns:
        with db.engine.connect() as connection:
            connection.execute('ALTER TABLE produtos ADD COLUMN estatus TEXT DEFAULT "Activo"')
            print('Columna "estatus" agregada a la tabla "produtos".')

    db.create_all()
