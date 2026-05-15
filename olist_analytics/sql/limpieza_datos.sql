---Revision para limpieza y roganizacion de los datos:

--  Conteo general de filas por tabla
select
	'raw_customers'  as tabla, 
	count(*) as filas 
FROM staging.raw_customers

union all

select 
	'raw_orders',
	count(*)
from staging.raw_orders

union all

select 
	'raw_order_items',
	count(*)
from staging.raw_order_items

union all

select 
	'raw_payments',
	count(*)
from staging.raw_payments 

union all

select 
	'raw_products',
	count(*)
from staging.raw_products 
;

-- Nulos en raw_orders (tabla más crítica y es clave que no tenga nulos)

SELECT
    COUNT(*)                                                          AS total_filas,
    COUNT(*) FILTER (WHERE order_id IS NULL)                          AS nulos_order_id,
    COUNT(*) FILTER (WHERE customer_id IS NULL)                       AS nulos_customer_id,
    COUNT(*) FILTER (WHERE order_status IS NULL)                      AS nulos_status,
    COUNT(*) FILTER (WHERE order_purchase_timestamp IS NULL)          AS nulos_fecha_compra,
    COUNT(*) FILTER (WHERE order_approved_at IS NULL)                 AS nulos_fecha_aprobacion,
    COUNT(*) FILTER (WHERE order_delivered_carrier_date IS NULL)      AS nulos_fecha_despacho,
    COUNT(*) FILTER (WHERE order_delivered_customer_date IS NULL)     AS nulos_fecha_entrega,
    COUNT(*) FILTER (WHERE order_estimated_delivery_date IS NULL)     AS nulos_fecha_estimada
FROM staging.raw_orders;

--Hallazgo: no hay nulos en el dataset

--verifico valores vacios

SELECT
    COUNT(*) FILTER (WHERE order_id = '')                          AS vacios_order_id,
    COUNT(*) FILTER (WHERE customer_id = '')                       AS vacios_customer_id,
    COUNT(*) FILTER (WHERE order_status = '')                      AS vacios_status,
    COUNT(*) FILTER (WHERE order_purchase_timestamp = '')          AS vacios_fecha_compra,
    COUNT(*) FILTER (WHERE order_approved_at = '')                 AS vacios_fecha_aprobacion,
    COUNT(*) FILTER (WHERE order_delivered_carrier_date = '')      AS vacios_fecha_despacho,
    COUNT(*) FILTER (WHERE order_delivered_customer_date = '')     AS vacios_fecha_entrega,
    COUNT(*) FILTER (WHERE order_estimated_delivery_date = '')     AS vacios_fecha_estimada
FROM staging.raw_orders;

--Hallazgos: valores vacios en 'order_approved_at', 'order_delivered_carrier_date' y 'order_delivered_customer_date'

--- verifico a donde pertenecen:  ordenes con fecha de entrega vacía, agrupadas por status para verificar cual es la razon de que esten vacias esas columnas
SELECT
    order_status,
    COUNT(*) AS total
FROM staging.raw_orders
WHERE order_delivered_customer_date = ''
GROUP BY order_status
ORDER BY total DESC;

--Hallazgos: de 2,965 ordenes sin fecha de entrega, hay 8 que están en status delivered pero no tienen fecha. De resto están en transito o canceladas etc.

---Auditoria raw_customers:
--vacios

SELECT
    COUNT(*)                                                    AS total_filas,
    COUNT(*) FILTER (WHERE customer_id = '')                    AS vacios_customer_id,
    COUNT(*) FILTER (WHERE customer_unique_id = '')             AS vacios_unique_id,
    COUNT(*) FILTER (WHERE customer_zip_code_prefix = '')       AS vacios_zip,
    COUNT(*) FILTER (WHERE customer_city = '')                  AS vacios_city,
    COUNT(*) FILTER (WHERE customer_state = '')                 AS vacios_state
FROM staging.raw_customers;

--Hallazgo: no hay vacios

--duplicados

SELECT
    COUNT(*)                        AS total_filas,
    COUNT(DISTINCT customer_id)     AS ids_unicos,
    COUNT(DISTINCT customer_unique_id) AS unique_ids_unicos
FROM staging.raw_customers;

--Hallazgos: customer_id es la identificacion de la transaccion, hay 99,441 transacciones distintas
------------ y customer_unique_id es el id real del cliente sin importar cuantas transacciones tenga
	---------conclusion: customer_unique_id es el identificador real del cliente



---- auditoria raw_order_items
-- 
SELECT
    COUNT(*)                                            AS total_filas,
    COUNT(*) FILTER (WHERE order_id = '')               AS vacios_order_id,
    COUNT(*) FILTER (WHERE product_id = '')             AS vacios_product_id,
    COUNT(*) FILTER (WHERE price = '')                  AS vacios_price,
    COUNT(*) FILTER (WHERE freight_value = '')          AS vacios_freight
FROM staging.raw_order_items;

--Hallazgos: no hay vacios 

--- Precios sospechosos
SELECT
    COUNT(*) FILTER (WHERE price::NUMERIC = 0)          AS precios_en_cero,
    COUNT(*) FILTER (WHERE price::NUMERIC < 0)          AS precios_negativos,
    ROUND(AVG(price::NUMERIC), 2)                       AS precio_promedio,
    ROUND(MIN(price::NUMERIC), 2)                       AS precio_minimo,
    ROUND(MAX(price::NUMERIC), 2)                       AS precio_maximo
FROM staging.raw_order_items;
--Hallzgos: no hay valores extraños como negativos, o ceros. Esta tabla no requiere limpieza especial

-----Auditoria raw_payments:

SELECT
    payment_type,
    COUNT(*)                        AS total,
    ROUND(AVG(payment_value::NUMERIC), 2) AS valor_promedio
FROM staging.raw_payments
GROUP BY payment_type
ORDER BY total DESC;


SELECT
    COUNT(*)                                                AS total_filas,
    COUNT(*) FILTER (WHERE order_id = '')                   AS vacios_order_id,
    COUNT(*) FILTER (WHERE payment_type = '')               AS vacios_tipo_pago,
    COUNT(*) FILTER (WHERE payment_value = '')              AS vacios_valor
FROM staging.raw_payments;

--Hallazgos: no hay filas vacias ni datos aparentemente erroneos


-----auditoria raw_products

SELECT
    COUNT(*)                                                    AS total_filas,
    COUNT(*) FILTER (WHERE product_id = '')                     AS vacios_product_id,
    COUNT(*) FILTER (WHERE product_category_name = '')          AS vacios_categoria,
    COUNT(*) FILTER (WHERE product_weight_g = '')               AS vacios_peso,
    COUNT(*) FILTER (WHERE product_length_cm = '')              AS vacios_largo,
    COUNT(*) FILTER (WHERE product_height_cm = '')              AS vacios_alto,
    COUNT(*) FILTER (WHERE product_width_cm = '')               AS vacios_ancho
FROM staging.raw_products;

--Hallazgo: para la columna 'product category name' presenta 610 espacios vacios. y 2 espacios vacios para 'product_weight_g',
-- 'product_length_cm' , 'product_height_cm'y  'product_width_cm'.

-- Decisión: en analytics reemplazar categoría vacía con 'sin_categoria'
-- y mantener los productos con dimensiones vacías ya que no afectan el análisis al tratarse de atributos fisicos y clasificatorios, en cambio si afectaria eliminar los registros.






