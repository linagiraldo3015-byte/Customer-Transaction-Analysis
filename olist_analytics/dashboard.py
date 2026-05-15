import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="Customer Analytics - Olist",
    page_icon="📊",
    layout="wide"
)

COLORES = {
    "Campeon": "#0B6E4F",
    "Cliente leal": "#3A86FF",
    "Potencial": "#FB8500",
    "Regular": "#8D99AE",
    "En riesgo": "#E63946",
    "Perdido": "#6C757D",
}
ORDEN_SEGMENTOS = ["Campeon", "Cliente leal", "Potencial", "Regular", "En riesgo", "Perdido"]

PLOTLY_LAYOUT = dict(
    font=dict(family="Inter, system-ui, sans-serif", size=13, color="#2B2D42"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=40, r=20, t=40, b=40),
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', system-ui, sans-serif; }
    h1, h2, h3 { font-weight: 700; color: #2B2D42; }
    [data-testid="stMetricValue"] { font-size: 1.6rem; font-weight: 700; }
    [data-testid="stMetricLabel"] { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def cargar_rfm():
    return pd.read_csv("rfm_data.csv")


@st.cache_data
def cargar_transacciones():
    df = pd.read_csv("analytics_data.csv", parse_dates=["order_date"])
    return df


rfm = cargar_rfm()
txn = cargar_transacciones()

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.header("Filtros")
fecha_min = txn["order_date"].min().date()
fecha_max = txn["order_date"].max().date()
rango = st.sidebar.date_input(
    "Rango de fechas",
    value=(fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max,
)

if isinstance(rango, tuple) and len(rango) == 2:
    inicio, fin = pd.Timestamp(rango[0]), pd.Timestamp(rango[1])
else:
    inicio, fin = pd.Timestamp(fecha_min), pd.Timestamp(fecha_max)

txn_f = txn[(txn["order_date"] >= inicio) & (txn["order_date"] <= fin)]
clientes_en_rango = set(txn_f["customer_id"])
rfm_f = rfm[rfm["customer_id"].isin(clientes_en_rango)]

# ── Header ───────────────────────────────────────────────────────────────────
st.title("📊 Customer Analytics — Olist E-Commerce")
st.caption(
    f"Análisis RFM · {len(rfm_f):,} clientes · "
    f"{inicio.strftime('%b %Y')} – {fin.strftime('%b %Y')}"
)
st.divider()

# ── KPIs ─────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
revenue_total = rfm_f["monetario"].sum()
with c1:
    st.metric("Total clientes", f"{len(rfm_f):,}")
with c2:
    st.metric("Revenue total", f"R$ {revenue_total:,.0f}")
with c3:
    st.metric("Ticket promedio", f"R$ {rfm_f['monetario'].mean():,.2f}")
with c4:
    rev_camp = rfm_f.loc[rfm_f["segmento"] == "Campeon", "monetario"].sum()
    pct_camp = rev_camp / revenue_total * 100 if revenue_total else 0
    st.metric("Revenue Campeones", f"{pct_camp:.1f}%")

st.divider()

# ── 1. Distribución de clientes ──────────────────────────────────────────────
st.subheader("¿Cómo están distribuidos los clientes?")
col1, col2 = st.columns([2, 1])

with col1:
    seg_count = (
        rfm_f["segmento"]
        .value_counts()
        .reindex(ORDEN_SEGMENTOS)
        .dropna()
        .astype(int)
    )
    fig = go.Figure(
        go.Bar(
            y=seg_count.index,
            x=seg_count.values,
            orientation="h",
            marker_color=[COLORES[s] for s in seg_count.index],
            text=[f"{v:,}" for v in seg_count.values],
            textposition="outside",
        )
    )
    fig.update_layout(**PLOTLY_LAYOUT, yaxis=dict(autorange="reversed"), xaxis_title="Total clientes")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    total = len(rfm_f)
    en_riesgo_n = len(rfm_f[rfm_f["segmento"].isin(["En riesgo", "Perdido"])])
    campeones_n = len(rfm_f[rfm_f["segmento"] == "Campeon"])
    st.markdown("**Insight**")
    st.info(f"El **{en_riesgo_n / total * 100:.1f}%** de los clientes está en riesgo o perdido.")
    st.success(f"Solo el **{campeones_n / total * 100:.1f}%** son Campeones.")

st.divider()

# ── 2. Ticket promedio por segmento ──────────────────────────────────────────
st.subheader("¿Cuánto gasta cada tipo de cliente?")
col1, col2 = st.columns([2, 1])

with col1:
    ticket = (
        rfm_f.groupby("segmento")["monetario"]
        .mean()
        .reindex(ORDEN_SEGMENTOS)
        .dropna()
    )
    fig = go.Figure(
        go.Bar(
            x=ticket.index,
            y=ticket.values,
            marker_color=[COLORES[s] for s in ticket.index],
            text=[f"R$ {v:,.0f}" for v in ticket.values],
            textposition="outside",
        )
    )
    fig.update_layout(**PLOTLY_LAYOUT, yaxis_title="Ticket promedio (R$)")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    t_camp = rfm_f.loc[rfm_f["segmento"] == "Campeon", "monetario"].mean()
    t_perd = rfm_f.loc[rfm_f["segmento"] == "Perdido", "monetario"].mean()
    ratio = t_camp / t_perd if t_perd else 0
    st.markdown("**Insight**")
    st.info(f"Un Campeón gasta **{ratio:.1f}x más** que un cliente Perdido.")
    st.warning("El problema principal es la frecuencia de compra, no el valor por transacción.")

st.divider()

# ── 3. Distribución del revenue ──────────────────────────────────────────────
st.subheader("¿Quién genera el revenue real?")
col1, col2 = st.columns([2, 1])

with col1:
    rev_seg = (
        rfm_f.groupby("segmento")["monetario"]
        .sum()
        .reindex(ORDEN_SEGMENTOS)
        .dropna()
    )
    fig = go.Figure(
        go.Pie(
            labels=rev_seg.index,
            values=rev_seg.values,
            marker=dict(colors=[COLORES[s] for s in rev_seg.index]),
            hole=0.45,
            textinfo="label+percent",
            textfont_size=13,
        )
    )
    fig.update_layout(**PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("**Insight**")
    st.info(f"Los Campeones representan solo el **{pct_camp:.1f}%** del revenue total.")
    rev_en_riesgo = rfm_f.loc[rfm_f["segmento"] == "En riesgo", "monetario"].sum()
    st.error(
        f"Los clientes En riesgo generan **R$ {rev_en_riesgo:,.0f}** — "
        "perderlos tendría un impacto significativo."
    )

st.divider()

# ── 4. Evolución del revenue mes a mes ───────────────────────────────────────
st.subheader("Evolución del revenue mensual")

rev_mensual = (
    txn_f.assign(mes=txn_f["order_date"].dt.to_period("M").dt.to_timestamp())
    .groupby("mes")["order_value"]
    .sum()
    .reset_index()
)
fig = px.area(
    rev_mensual,
    x="mes",
    y="order_value",
    labels={"mes": "Mes", "order_value": "Revenue (R$)"},
    color_discrete_sequence=["#3A86FF"],
)
fig.update_layout(**PLOTLY_LAYOUT)
fig.update_traces(
    hovertemplate="<b>%{x|%b %Y}</b><br>Revenue: R$ %{y:,.0f}<extra></extra>",
    line=dict(width=2.5),
    fillcolor="rgba(58,134,255,0.12)",
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── 5. Mapa coroplético de revenue por estado ────────────────────────────────
st.subheader("Revenue por estado")

rev_estado = txn_f.groupby("state")["order_value"].sum().reset_index()
rev_estado.columns = ["state", "revenue"]

fig = px.choropleth(
    rev_estado,
    locations="state",
    color="revenue",
    hover_name="state",
    hover_data={"revenue": ":,.0f", "state": False},
    geojson="https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson",
    featureidkey="properties.sigla",
    color_continuous_scale=["#EDF2FB", "#3A86FF", "#0B3D91"],
    labels={"revenue": "Revenue (R$)"},
)
fig.update_geos(
    fitbounds="locations",
    visible=False,
    bgcolor="rgba(0,0,0,0)",
)
fig.update_layout(
    **PLOTLY_LAYOUT,
    geo=dict(projection_type="natural earth"),
    height=550,
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── 6. Explorar clientes por segmento ────────────────────────────────────────
st.subheader("Explorar clientes por segmento")
segmento_sel = st.selectbox(
    "Selecciona un segmento",
    ["Todos"] + ORDEN_SEGMENTOS,
)
df_tabla = rfm_f if segmento_sel == "Todos" else rfm_f[rfm_f["segmento"] == segmento_sel]
st.dataframe(
    df_tabla[["customer_id", "recency_dias", "frecuencia", "monetario", "segmento"]]
    .sort_values("monetario", ascending=False)
    .head(100),
    use_container_width=True,
)

st.divider()

# ── 7. Revenue recuperable & recomendaciones ─────────────────────────────────
st.subheader("Revenue recuperable: clientes En Riesgo")

riesgo = rfm_f[rfm_f["segmento"] == "En riesgo"]
n_riesgo = len(riesgo)
ticket_medio_riesgo = riesgo["monetario"].mean()
revenue_recuperable = n_riesgo * ticket_medio_riesgo

m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Clientes En Riesgo", f"{n_riesgo:,}")
with m2:
    st.metric("Ticket promedio histórico", f"R$ {ticket_medio_riesgo:,.2f}")
with m3:
    st.metric("Revenue recuperable potencial", f"R$ {revenue_recuperable:,.0f}")

st.caption(
    "Estimación: si cada cliente En Riesgo realizara una compra adicional "
    "equivalente a su valor monetario histórico promedio."
)

st.divider()

st.subheader("Recomendaciones de negocio")

st.markdown(
    f"""
| Prioridad | Acción | Impacto esperado |
|-----------|--------|------------------|
| 🔴 Alta | **Programa de reactivación para clientes En Riesgo** — cupones personalizados o descuento en próxima compra dirigido a los {n_riesgo:,} clientes de este segmento. | Recuperar hasta **R$ {revenue_recuperable:,.0f}** en revenue. |
| 🔴 Alta | **Incentivos de segunda compra** — la frecuencia promedio es ~1 en todos los segmentos; un programa de referidos o descuento por recompra atacaría el problema estructural de retención. | Aumentar LTV un 50-100% por cliente convertido. |
| 🟡 Media | **Programa de fidelización para Campeones** — beneficios exclusivos (envío gratis, acceso anticipado) para los {campeones_n:,} clientes que ya generan el {pct_camp:.1f}% del revenue. | Retener el segmento de mayor valor y generar referidos. |
| 🟡 Media | **Conversión de Potenciales a Leales** — {len(rfm_f[rfm_f['segmento'] == 'Potencial']):,} clientes con recencia reciente pero baja frecuencia; campañas de cross-sell basadas en categoría de última compra. | Mover clientes al segmento de mayor frecuencia. |
| 🟢 Baja | **Análisis geográfico de concentración** — el mapa muestra que SP concentra la mayoría del revenue; explorar campañas regionales en estados con menor penetración. | Diversificar la base de ingresos geográficamente. |
"""
)
