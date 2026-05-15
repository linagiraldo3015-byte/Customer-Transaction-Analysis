------  Calcular métricas RFM por cliente
WITH rfm_base AS (
    SELECT
        customer_id,
        MAX(order_date)                     AS ultima_compra,
        COUNT(DISTINCT order_id)            AS frecuencia,
        ROUND(SUM(order_value)::NUMERIC, 2) AS monetario
    FROM analytics.customer_transactions
    GROUP BY customer_id
),
fecha_ref AS (
    SELECT MAX(ultima_compra) AS fecha_referencia
    FROM rfm_base
)
SELECT
    r.customer_id,
    r.ultima_compra,
    r.frecuencia,
    r.monetario,
    DATE_PART('day', f.fecha_referencia - r.ultima_compra) AS recency_dias
FROM rfm_base r
CROSS JOIN fecha_ref f
ORDER BY recency_dias
LIMIT 20;

--hallazgos: 
-----frecuencia: la mayoria tiene 2
----- monetario: valores entre $14 y $712
----- recency_dias: todos en 0 porque son los mas recientes del dataset


--- Calcular scores RFM
WITH rfm_base AS (
    SELECT
        customer_id,
        MAX(order_date)                     AS ultima_compra,
        COUNT(DISTINCT order_id)            AS frecuencia,
        ROUND(SUM(order_value)::NUMERIC, 2) AS monetario
    FROM analytics.customer_transactions
    GROUP BY customer_id
),
fecha_ref AS (
    SELECT MAX(ultima_compra) AS fecha_referencia
    FROM rfm_base
),
rfm_calc AS (
    SELECT
        r.customer_id,
        r.frecuencia,
        r.monetario,
        DATE_PART('day', f.fecha_referencia - r.ultima_compra) AS recency_dias
    FROM rfm_base r
    CROSS JOIN fecha_ref f
)
SELECT
    customer_id,
    recency_dias,
    frecuencia,
    monetario,
    NTILE(5) OVER (ORDER BY recency_dias ASC)  AS r_score,
    NTILE(5) OVER (ORDER BY frecuencia DESC)   AS f_score,
    NTILE(5) OVER (ORDER BY monetario DESC)    AS m_score
FROM rfm_calc
LIMIT 20;

---Hallazgos:

--  Segmentación final RFM
WITH rfm_base AS (
    SELECT
        customer_id,
        MAX(order_date)                     AS ultima_compra,
        COUNT(DISTINCT order_id)            AS frecuencia,
        ROUND(SUM(order_value)::NUMERIC, 2) AS monetario
    FROM analytics.customer_transactions
    GROUP BY customer_id
),
fecha_ref AS (
    SELECT MAX(ultima_compra) AS fecha_referencia
    FROM rfm_base
),
rfm_calc AS (
    SELECT
        r.customer_id,
        r.frecuencia,
        r.monetario,
        DATE_PART('day', f.fecha_referencia - r.ultima_compra) AS recency_dias
    FROM rfm_base r
    CROSS JOIN fecha_ref f
),
rfm_scores AS (
    SELECT
        customer_id,
        recency_dias,
        frecuencia,
        monetario,
        NTILE(5) OVER (ORDER BY recency_dias ASC)  AS r_score,
        NTILE(5) OVER (ORDER BY frecuencia DESC)   AS f_score,
        NTILE(5) OVER (ORDER BY monetario DESC)    AS m_score
    FROM rfm_calc
)
SELECT
    customer_id,
    recency_dias,
    frecuencia,
    monetario,
    r_score,
    f_score,
    m_score,
    CASE
        WHEN r_score = 5 AND f_score >= 4 THEN 'Campeon'
        WHEN r_score >= 4 AND f_score >= 3 THEN 'Cliente leal'
        WHEN r_score >= 3 AND f_score <= 2 THEN 'Potencial'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'En riesgo'
        WHEN r_score <= 2 AND f_score <= 2 THEN 'Perdido'
        ELSE 'Regular'
    END                                            AS segmento
FROM rfm_scores
ORDER BY r_score DESC, f_score DESC
LIMIT 20;

--- Distribución de segmentos
WITH rfm_base AS (
    SELECT
        customer_id,
        MAX(order_date)                     AS ultima_compra,
        COUNT(DISTINCT order_id)            AS frecuencia,
        ROUND(SUM(order_value)::NUMERIC, 2) AS monetario
    FROM analytics.customer_transactions
    GROUP BY customer_id
),
fecha_ref AS (
    SELECT MAX(ultima_compra) AS fecha_referencia
    FROM rfm_base
),
rfm_calc AS (
    SELECT
        r.customer_id,
        r.frecuencia,
        r.monetario,
        DATE_PART('day', f.fecha_referencia - r.ultima_compra) AS recency_dias
    FROM rfm_base r
    CROSS JOIN fecha_ref f
),
rfm_scores AS (
    SELECT
        customer_id,
        NTILE(5) OVER (ORDER BY recency_dias ASC)  AS r_score,
        NTILE(5) OVER (ORDER BY frecuencia DESC)   AS f_score,
        NTILE(5) OVER (ORDER BY monetario DESC)    AS m_score
    FROM rfm_calc
),
rfm_segmentos AS (
    SELECT
        CASE
            WHEN r_score = 5 AND f_score >= 4 THEN 'Campeon'
            WHEN r_score >= 4 AND f_score >= 3 THEN 'Cliente leal'
            WHEN r_score >= 3 AND f_score <= 2 THEN 'Potencial'
            WHEN r_score <= 2 AND f_score >= 3 THEN 'En riesgo'
            WHEN r_score <= 2 AND f_score <= 2 THEN 'Perdido'
            ELSE 'Regular'
        END AS segmento
    FROM rfm_scores
)
SELECT
    segmento,
    COUNT(*)                                                    AS total_clientes,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2)         AS porcentaje
FROM rfm_segmentos
GROUP BY segmento
ORDER BY total_clientes DESC;


-- 5. Revenue promedio por segmento
WITH rfm_base AS (
    SELECT
        customer_id,
        MAX(order_date)                     AS ultima_compra,
        COUNT(DISTINCT order_id)            AS frecuencia,
        ROUND(SUM(order_value)::NUMERIC, 2) AS monetario
    FROM analytics.customer_transactions
    GROUP BY customer_id
),
fecha_ref AS (
    SELECT MAX(ultima_compra) AS fecha_referencia
    FROM rfm_base
),
rfm_calc AS (
    SELECT
        r.customer_id,
        r.frecuencia,
        r.monetario,
        DATE_PART('day', f.fecha_referencia - r.ultima_compra) AS recency_dias
    FROM rfm_base r
    CROSS JOIN fecha_ref f
),
rfm_scores AS (
    SELECT
        customer_id,
        monetario,
        frecuencia,
        NTILE(5) OVER (ORDER BY recency_dias ASC)  AS r_score,
        NTILE(5) OVER (ORDER BY frecuencia DESC)   AS f_score,
        NTILE(5) OVER (ORDER BY monetario DESC)    AS m_score
    FROM rfm_calc
),
rfm_segmentos AS (
    SELECT
        customer_id,
        monetario,
        frecuencia,
        CASE
            WHEN r_score = 5 AND f_score >= 4 THEN 'Campeon'
            WHEN r_score >= 4 AND f_score >= 3 THEN 'Cliente leal'
            WHEN r_score >= 3 AND f_score <= 2 THEN 'Potencial'
            WHEN r_score <= 2 AND f_score >= 3 THEN 'En riesgo'
            WHEN r_score <= 2 AND f_score <= 2 THEN 'Perdido'
            ELSE 'Regular'
        END AS segmento
    FROM rfm_scores
)
SELECT
    segmento,
    COUNT(*)                                AS total_clientes,
    ROUND(AVG(monetario), 2)               AS ticket_promedio,
    ROUND(SUM(monetario), 2)               AS revenue_total,
    ROUND(AVG(frecuencia), 2)              AS frecuencia_promedio
FROM rfm_segmentos
GROUP BY segmento
ORDER BY revenue_total DESC;

-- HALLAZGOS DE NEGOCIO:
-- Potencial y En riesgo generan el mayor revenue total ($3.7M cada uno)
-- porque son los segmentos más grandes (22,311 clientes cada uno)
-- Los Campeones son solo 7,528 clientes pero con ticket promedio de $161
-- La frecuencia promedio es ~1 en todos los segmentos
-- Hallazgo clave: la mayoría de clientes de Olist compra solo una vez
-- Oportunidad: convertir clientes Potenciales en Leales

