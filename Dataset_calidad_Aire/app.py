import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Calidad del Aire Colombia", layout="wide")

st.title("🇨🇴 Histórico de Calidad del Aire en Colombia (2011-2025)")
st.markdown("Tablero interactivo basado en datos abiertos del IDEAM.")

@st.cache_data
def load_data():
    return pd.read_csv('calidad_aire/airquality_clean.csv')

df = load_data()

# Filtros en Sidebar
st.sidebar.header("Filtros")
depto = st.sidebar.selectbox("Seleccione Departamento", sorted(df['Nombre del Departamento'].unique()))
df_filtered = df[df['Nombre del Departamento'] == depto]

# Nuevo: Filtro de Municipio dependiente del departamento
municipios = sorted(df_filtered['Nombre del Municipio'].unique())
municipio = st.sidebar.selectbox("Seleccione Municipio", ["Todos"] + municipios)
if municipio != "Todos":
    df_filtered = df_filtered[df_filtered['Nombre del Municipio'] == municipio]

variable = st.sidebar.selectbox("Seleccione Contaminante/Variable", sorted(df_filtered['Variable'].unique()))
df_filtered = df_filtered[df_filtered['Variable'] == variable]

# KPIs principales
st.subheader(f"Métricas para {variable} en {depto} {f'({municipio})' if municipio != 'Todos' else ''}")
col1, col2, col3 = st.columns(3)
col1.metric("Promedio General", f"{df_filtered['Promedio'].mean():.2f}" if not df_filtered.empty else "0")
col2.metric("Valor Máximo", f"{df_filtered['Máximo'].max():.2f}" if not df_filtered.empty else "0")
col3.metric("Total Registros", len(df_filtered))

# Gráfico y Mapa
st.subheader("Evolución Temporal Anual")
if not df_filtered.empty:
    fig_line = px.line(df_filtered.groupby('Año')['Promedio'].mean().reset_index(), 
                       x='Año', y='Promedio', markers=True, title=f"Tendencia anual de {variable}")
    st.plotly_chart(fig_line, use_container_width=True)

st.subheader("Ubicación de Estaciones")
if not df_filtered.empty and 'Latitud' in df_filtered.columns:
    df_map = df_filtered[['Latitud', 'Longitud']].rename(columns={'Latitud': 'lat', 'Longitud': 'lon'}).drop_duplicates()
    st.map(df_map)
