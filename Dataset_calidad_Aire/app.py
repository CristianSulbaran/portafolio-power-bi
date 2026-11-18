import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de página en modo ancho (Wide) para aprovechar toda la pantalla
st.set_page_config(page_title="Panel de Calidad del Aire - Colombia", layout="wide")

# Carga de datos optimizada
@st.cache_data
def load_data():
    return pd.read_csv('Dataset_calidad_Aire/airquality_clean.csv')

df = load_data()

# ---------------------------------------------------------
# BARRA SUPERIOR / FILTROS PRINCIPALES
# ---------------------------------------------------------
st.markdown("### 📊 Panel de Calidad del Aire")
st.markdown("Colombia • Datos históricos (2011–2025)")

st.sidebar.header("⚙️ FILTROS")

# Filtro de Departamento / Ciudad
ciudades_disponibles = sorted(df['Nombre del Departamento'].unique())
ciudad_sel = st.sidebar.selectbox("Ciudad / Departamento", ["Todas las ciudades"] + ciudades_disponibles)

# Filtro de Años
anos_disponibles = sorted(df['Año'].unique())
val_min, val_max = int(min(anos_disponibles)), int(max(anos_disponibles))
rango_anos = st.sidebar.slider("Período", val_min, val_max, (val_min, val_max))

# Filtro de Contaminante (Variable)
variables_disponibles = sorted(df['Variable'].unique())
contaminante_sel = st.sidebar.selectbox("Contaminante / Variable", variables_disponibles)

# Filtrado dinámico del DataFrame
df_filtered = df.copy()
if ciudad_sel != "Todas las ciudades":
    df_filtered = df_filtered[df_filtered['Nombre del Departamento'] == ciudad_sel]

df_filtered = df_filtered[(df_filtered['Año'] >= rango_anos[0]) & (df_filtered['Año'] <= rango_anos[1])]
df_filtered = df_filtered[df_filtered['Variable'] == contaminante_sel]

# ---------------------------------------------------------
# 4 TARJETAS DE KPIs SUPERIORES (Estilo Ejecutivo)
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

promedio_general = df_filtered['Promedio'].mean() if not df_filtered.empty else 0
max_registrado = df_filtered['Máximo'].max() if not df_filtered.empty else 0
total_registros = len(df_filtered)
excedencias_calc = len(df_filtered[df_filtered['Promedio'] > 50]) # Umbral referencial

col1.metric(label=f"PROMEDIO {contaminante_sel}", value=f"{promedio_general:.2f}")
col2.metric(label="VALOR MÁXIMO", value=f"{max_registrado:.2f}")
col3.metric(label="REGISTROS TOTALES", value=f"{total_registros}")
col4.metric(label="EVENTOS CRÍTICOS", value=f"{excedencias_calc} registros")

st.markdown("---")
st.info("💡 **Fase 1 lista:** Estructura superior y tarjetas ejecutivas configuradas. Haz los cambios en GitHub y avísame para agregar el mapa interactivo y los gráficos en la Fase 2.")
