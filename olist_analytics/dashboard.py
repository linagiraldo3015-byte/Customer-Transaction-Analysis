import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Customer Analytics - Olist",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def cargar_datos():
    return pd.read_csv("olist_analytics/rfm_data.csv")

colores = {
    'Campeon': '#2ecc71', 'Cliente leal': '#3498db',
    'Potencial': '#f39c12', 'Regular': '#95a5a6',
    'En riesgo': '#e67e22', 'Perdido': '#e74c3c'
}

with st.spinner("Cargando datos..."):
    df = cargar_datos()

st.title("📊 Customer Analytics — Olist E-Commerce")
st.markdown("Análisis RFM · 93,350 clientes · 2016–2018")
st.markdown("---")

# Métricas
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

# Pregunta 1
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
    campeones_n = len(df[df['segmento'] == 'Campeon'])
    st.info(f"El **{en_riesgo/total*100:.1f}%** de los clientes está en riesgo o perdido.")
    st.success(f"Solo **{campeones_n/total*100:.1f}%** son Campeones.")

st.markdown("---")

# Pregunta 2
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
    st.warning("El problema principal es la frecuencia de compra, no el valor por transacción.")

st.markdown("---")

# Pregunta 3
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
    st.info(f"Los Campeones representan solo el **{pct_rev:.1f}%** del revenue total.")
    rev_en_riesgo = df[df['segmento'] == 'En riesgo']['monetario'].sum()
    st.error(f"Los clientes En riesgo generan **${rev_en_riesgo:,.0f}** — perderlos tendría un impacto significativo.")

st.markdown("---")

# Tabla
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