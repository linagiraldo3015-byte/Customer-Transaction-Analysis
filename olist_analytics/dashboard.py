import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import psycopg2

st.set_page_config(
    page_title="Customer Analytics - Olist",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def cargar_datos():
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="olist_project",
        user="postgres",
        password="lizara1937."
    )
    query = """
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
            recency_dias,
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
        CASE
            WHEN r_score = 5 AND f_score >= 4 THEN 'Campeon'
            WHEN r_score >= 4 AND f_score >= 3 THEN 'Cliente leal'
            WHEN r_score >= 3 AND f_score <= 2 THEN 'Potencial'
            WHEN r_score <= 2 AND f_score >= 3 THEN 'En riesgo'
            WHEN r_score <= 2 AND f_score <= 2 THEN 'Perdido'
            ELSE 'Regular'
        END AS segmento
    FROM rfm_scores
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

colores = {
    'Campeon': '#2ecc71', 'Cliente leal': '#3498db',
    'Potencial': '#f39c12', 'Regular': '#95a5a6',
    'En riesgo': '#e67e22', 'Perdido': '#e74c3c'
}

# Cargar datos
with st.spinner("Cargando datos..."):
    df = cargar_datos()

# Título
st.title("📊 Customer Analytics — Olist E-Commerce")
st.markdown("Análisis RFM · 93,350 clientes · 2016–2018")
st.markdown("---")

# ── MÉTRICAS PRINCIPALES ──────────────────────────────
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total clientes", f"{len(df):,}")
with col2:
    st.metric("Revenue total", f"${df['monetario'].sum():,.0f}")
with col3:
    st.metric("Ticket promedio", f"${df['monetario'].mean():,.2f}")
with col4:
    campeones = df[df['segmento'] == 'Campeon']
    pct_rev = campeones['monetario'].sum() / df['monetario'].sum() * 100
    st.metric("Revenue de Campeones", f"{pct_rev:.1f}%")

st.markdown("---")

# ── PREGUNTA 1: Distribución de clientes ─────────────
st.subheader("¿Cómo están distribuidos mis clientes?")

col1, col2 = st.columns([2, 1])

with col1:
    seg_count = df['segmento'].value_counts()
    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.barh(
        seg_count.index, seg_count.values,
        color=[colores.get(s, '#95a5a6') for s in seg_count.index]
    )
    for bar, val in zip(bars, seg_count.values):
        ax.text(bar.get_width() + 100, bar.get_y() + bar.get_height()/2,
                f'{val:,}', va='center', fontsize=9)
    ax.set_xlabel("Total clientes")
    ax.set_xlim(0, seg_count.max() * 1.15)
    st.pyplot(fig)
    plt.close()

with col2:
    st.markdown("**Insight**")
    total = len(df)
    en_riesgo = len(df[df['segmento'].isin(['En riesgo', 'Perdido'])])
    st.info(f"El **{en_riesgo/total*100:.1f}%** de los clientes está en riesgo o perdido — una oportunidad de retención.")
    campeones_n = len(df[df['segmento'] == 'Campeon'])
    st.success(f"Solo **{campeones_n/total*100:.1f}%** son Campeones — el segmento más valioso.")

st.markdown("---")

# ── PREGUNTA 2: Ticket promedio por segmento ─────────
st.subheader("¿Cuánto gasta cada tipo de cliente?")

col1, col2 = st.columns([2, 1])

with col1:
    ticket = df.groupby('segmento')['monetario'].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(
        ticket.index, ticket.values,
        color=[colores.get(s, '#95a5a6') for s in ticket.index]
    )
    for bar, val in zip(bars, ticket.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'${val:,.0f}', ha='center', fontsize=9)
    ax.set_ylabel("Ticket promedio (USD)")
    plt.xticks(rotation=45)
    st.pyplot(fig)
    plt.close()

with col2:
    st.markdown("**Insight**")
    ticket_campeon = df[df['segmento'] == 'Campeon']['monetario'].mean()
    ticket_perdido = df[df['segmento'] == 'Perdido']['monetario'].mean()
    diferencia = ticket_campeon / ticket_perdido
    st.info(f"Un Campeón gasta **{diferencia:.1f}x más** que un cliente Perdido.")
    st.warning("La diferencia de ticket no es tan grande como se esperaría — el problema principal es la frecuencia de compra, no el valor por transacción.")

st.markdown("---")

# ── PREGUNTA 3: Revenue Campeones vs resto ────────────
st.subheader("¿Quién genera el revenue real?")

col1, col2 = st.columns([2, 1])

with col1:
    rev_seg = df.groupby('segmento')['monetario'].sum()
    rev_campeon = rev_seg.get('Campeon', 0)
    rev_resto = rev_seg.sum() - rev_campeon

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        [rev_campeon, rev_resto],
        labels=['Campeones', 'Resto'],
        colors=['#2ecc71', '#bdc3c7'],
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 12}
    )
    ax.set_title("Distribución del revenue total")
    st.pyplot(fig)
    plt.close()

with col2:
    st.markdown("**Insight**")
    st.info(f"Los Campeones representan solo el **{pct_rev:.1f}%** del revenue total a pesar de ser el **{campeones_n/total*100:.1f}%** de los clientes.")
    
    rev_en_riesgo = df[df['segmento'] == 'En riesgo']['monetario'].sum()
    st.error(f"Los clientes En riesgo generan **${rev_en_riesgo:,.0f}** — si se pierden, el impacto en revenue sería significativo.")

st.markdown("---")

# ── TABLA DETALLE ────────────────────────────────────
st.subheader("Explorar clientes por segmento")
segmento_sel = st.selectbox(
    "Selecciona un segmento",
    ['Todos'] + sorted(df['segmento'].unique().tolist())
)

df_filtrado = df if segmento_sel == 'Todos' else df[df['segmento'] == segmento_sel]

st.dataframe(
    df_filtrado[['customer_id', 'recency_dias', 'frecuencia', 'monetario', 'segmento']]
    .sort_values('monetario', ascending=False)
    .head(100),
    use_container_width=True
)