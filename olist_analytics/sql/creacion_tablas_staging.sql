create TABLE staging.raw_customers (
	customer_id                   text,
	customer_unique_id            text,
	customer_zip_code_prefix      text,
	customer_city                 text,
	customer_state                text
	
);

create table staging.raw_orders (
	order_id                      text,
	customer_id                   text,
	order_status                  text,
	order_purchase_timestamp      text,
	order_approved_at             text,
	order_delivered_carrier_date  text,
	order_delivered_customer_date text,
	order_estimated_delivery_date text
	
	);
	
create table staging.raw_order_items (
    order_id                     TEXT,
    order_item_id                TEXT,
    product_id                   TEXT,
    seller_id                    TEXT,
    shipping_limit_date          TEXT,
    price                        TEXT,
    freight_value                TEXT
    
   );
   
  CREATE TABLE staging.raw_payments (
    order_id                     TEXT,
    payment_sequential           TEXT,
    payment_type                 TEXT,
    payment_installments         TEXT,
    payment_value                TEXT
);

CREATE TABLE staging.raw_products (
    product_id                   TEXT,
    product_category_name        TEXT,
    product_name_lenght          TEXT,
    product_description_lenght   TEXT,
    product_photos_qty           TEXT,
    product_weight_g             TEXT,
    product_length_cm            TEXT,
    product_height_cm            TEXT,
    product_width_cm             TEXT
);

