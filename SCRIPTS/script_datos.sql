INSERT INTO productos (id, nombre, precio) VALUES
(1, 'LAPTOP', 3000.00),
(2, 'PC', 4000.00),
(3, 'MOUSE', 100.00),
(4, 'TECLADO', 150.00),
(5, 'MONITOR', 2000.00),
(6, 'MICROFONO', 350.00),
(7, 'AUDIFONOS', 450.00);

INSERT INTO ventas (id, producto_id, cantidad) VALUES
(1, 5, 8),
(2, 1, 15),
(3, 6, 13),
(4, 3, 7),
(5, 4, 5),
(6, 7, 8),
(7, 4, 5),
(8, 3, 5),
(9, 6, 2),
(10, 1, 8);

INSERT INTO usuarios (nombre, password, rol) VALUES
('admin', ('admin123'), 'admin'),
('almacenista', ('almacen123'), 'almacenista');

SELECT id, nombre, password FROM usuarios;
DELETE FROM usuarios WHERE id = 18;

SELECT id, producto_id, cantidad FROM productos;

ALTER TABLE ventas ADD COLUMN total DECIMAL(10,2);

DESC usuarios;
SELECT * FROM usuarios;

ALTER TABLE movimientos 
ADD CONSTRAINT fk_movimientos_usuarios 
FOREIGN KEY (usuario_id) REFERENCES usuarios(id);

SELECT id FROM usuarios WHERE id IN (101, 102, 103, 104, 105);
