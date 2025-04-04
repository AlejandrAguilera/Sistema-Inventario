SELECT DISTINCT p.id, p.nombre 
FROM productos p 
JOIN ventas v ON p.id = v.producto_id;

SELECT p.id, p.nombre, SUM(v.cantidad) AS total_vendido
FROM productos p
JOIN ventas v ON p.id = v.producto_id
GROUP BY p.id, p.nombre;

SELECT p.id, p.nombre, 
       IFNULL(SUM(v.cantidad * p.precio), 0) AS total_vendido 
FROM productos p 
LEFT JOIN ventas v ON p.id = v.producto_id 
GROUP BY p.id, p.nombre 
LIMIT 1000;

