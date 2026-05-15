  ----Tabla customers limpia
CREATE TABLE analytics.customers as

SELECT DISTINCT
    customer_unique_id                  AS customer_id,
    INITCAP(customer_city)             AS city,
    customer_state                      AS state
FROM staging.raw_customers
WHERE customer_unique_id IS NOT NULL
  AND customer_unique_id != '';


-- Tabla orders limpia
-- 2. Tabla orders limpia
CREATE TABLE analytics.orders AS
SELECT
    o.order_id,
    c.customer_unique_id                        AS customer_id,
    o.order_status,
    o.order_purchase_timestamp::TIMESTAMP       AS order_date,
    o.order_delivered_customer_date::TIMESTAMP  AS delivered_date,
    o.order_estimated_delivery_date::TIMESTAMP  AS estimated_date,
    CASE
        WHEN o.order_delivered_customer_date::TIMESTAMP
           > o.order_estimated_delivery_date::TIMESTAMP
        THEN TRUE
        ELSE FALSE
    END                                         AS delivered_late
FROM staging.raw_orders o
JOIN staging.raw_customers c USING (customer_id)
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date != '';

-- Tabla order_items limpia
CREATE TABLE analytics.order_items AS
SELECT
    order_id,
    product_id,
    order_item_id::INT                                      AS item_sequence,
    ROUND(price::NUMERIC, 2)                                AS price,
    ROUND(freight_value::NUMERIC, 2)                        AS freight_value,
    ROUND(price::NUMERIC + freight_value::NUMERIC, 2)       AS total_value
FROM staging.raw_order_items
WHERE price::NUMERIC > 0;


--- Tabla de productos limpia

CREATE TABLE analytics.products AS
SELECT
    product_id,
    COALESCE(
        NULLIF(product_category_name, ''), 'sin_categoria'
    )                                               AS category,
    NULLIF(product_photos_qty, '')::INT             AS photos_qty,
    NULLIF(product_weight_g, '')::NUMERIC           AS weight_g
FROM staging.raw_products;


--- Tabla maestra para RFM (transactions)

CREATE TABLE analytics.customer_transactions AS
SELECT
    o.customer_id,
    o.order_id,
    o.order_date,
    o.delivered_late,
    SUM(i.total_value)      AS order_value,
    COUNT(i.item_sequence)  AS items_count
FROM analytics.orders o
JOIN analytics.order_items i USING (order_id)
GROUP BY 1, 2, 3, 4;




