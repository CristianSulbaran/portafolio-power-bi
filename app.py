import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Calidad del Aire Colombia", layout="wide")

st.title("🇨🇴 Histórico de Calidad del Aire en Colombia (2011-2025)")
st.markdown("Tablero interactivo basado en datos abiertos del IDEAM.")

# Cargar datos limpios
@st.cache_data
def load_data():
    return pd.read_csv('airquality_clean.csv')

df = load_data()

# Sidebar: Filtros
st.sidebar.header("Filtros")
depto = st.sidebar.selectbox("Seleccione Departamento", sorted(df['Nombre del Departamento'].unique()))
df_filtered = df[df['Nombre del Departamento'] == depto]

variable = st.sidebar.selectbox("Seleccione Contaminante/Variable", sorted(df_filtered['Variable'].unique()))
df_filtered = df_filtered[df_filtered['Variable'] == variable]

# KPIs principales
st.subheader(f"Métricas para {variable} en {depto}")
col1, col2, col3 = st.columns(3)
col1.metric("Promedio General", f"{df_filtered['Promedio'].mean():.2f}")
col2.metric("Valor Máximo Registrado", f"{df_filtered['Máximo'].max():.2f}")
col3.metric("Total de Registros", len(df_filtered))

# Gráfico de evolución temporal
st.subheader("Evolución Temporal Anual")
if not df_filtered.empty:
    fig_line = px.line(df_filtered.groupby('Año')['Promedio'].mean().reset_index(), 
                       x='Año', y='Promedio', markers=True, title=f"Tendencia anual de {variable}")
    st.plotly_chart(fig_line, use_container_width=True)

# Mapa de estaciones
st.subheader("Ubicación de Estaciones")
if not df_filtered.empty and 'Latitud' in df_filtered.columns:
    st.map(df_filtered[['Latitud', 'Longitud']].drop_duplicates())
