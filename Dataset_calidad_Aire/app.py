import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de página en modo ancho (Wide)
st.set_page_config(page_title="Panel de Calidad del Aire - Colombia", layout="wide")

# Carga de datos con la ruta de tu carpeta
@st.cache_data
def load_data():
    return pd.read_csv('Dataset_calidad_Aire/airquality_clean.csv')

df = load_data()

# ---------------------------------------------------------
# BARRA LATERAL / FILTROS PRINCIPALES
# ---------------------------------------------------------
st.markdown("### 📊 Panel de Calidad del Aire")
st.markdown("Colombia • Datos históricos (2011–2025)")

st.sidebar.header("⚙️ FILTROS")

ciudades_disponibles = sorted(df['Nombre del Departamento'].unique())
ciudad_sel = st.sidebar.selectbox("Ciudad / Departamento", ["Todas las ciudades"] + ciudades_disponibles)

anos_disponibles = sorted(df['Año'].unique())
val_min, val_max = int(min(anos_disponibles)), int(max(anos_disponibles))
rango_anos = st.sidebar.slider("Período", val_min, val_max, (val_min, val_max))

variables_disponibles = sorted(df['Variable'].unique())
contaminante_sel = st.sidebar.selectbox("Contaminante / Variable", variables_disponibles)

# Filtrado dinámico
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
excedencias_calc = len(df_filtered[df_filtered['Promedio'] > 15]) # Umbral OMS

col1.metric(label=f"PROMEDIO {contaminante_sel}", value=f"{promedio_general:.2f}")
col2.metric(label="VALOR MÁXIMO", value=f"{max_registrado:.2f}")
col3.metric(label="REGISTROS TOTALES", value=f"{total_registros}")
col4.metric(label="EVENTOS CRÍTICOS (>15)", value=f"{excedencias_calc} registros")

st.markdown("---")

# ---------------------------------------------------------
# MAPA MAPBOX Y TENDENCIA ANUAL
# ---------------------------------------------------------
col_mapa, col_grafico = st.columns([1, 1.5])

with col_mapa:
    st.subheader("🌍 Distribución Geográfica")
    if not df_filtered.empty and 'Latitud' in df_filtered.columns and 'Longitud' in df_filtered.columns:
        df_map_data = df_filtered.drop_duplicates(subset=['Nombre del Municipio', 'Latitud', 'Longitud'])
        
        # Estilo integrado directamente en scatter_mapbox para evitar errores de atributo
        fig_map = px.scatter_mapbox(
            df_map_data,
            lat='Latitud',
            lon='Longitud',
            hover_name='Nombre del Municipio',
            size='Promedio',
            color='Promedio',
            color_continuous_scale='Viridis',
            zoom=4.5,
            center=dict(lat=4.5708, lon=-74.2973),
            height=420,
            mapbox_style="open-street-map"
        )
        fig_map.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("No hay datos geográficos disponibles para los filtros seleccionados.")

with col_grafico:
    st.subheader(f"📈 Tendencia Anual - {contaminante_sel}")
    if not df_filtered.empty:
        df_tendencia = df_filtered.groupby('Año')['Promedio'].mean().reset_index()
        fig_line = px.line(
            df_tendencia, 
            x='Año', 
            y='Promedio', 
            markers=True,
            line_shape='spline'
        )
        fig_line.add_hline(y=15, line_dash="dash", line_color="red", annotation_text="Límite OMS (15 µg/m³)")
        fig_line.update_layout(margin={"r":0,"t":30,"l":0,"b":0}, height=420)
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.warning("No hay datos para mostrar en la tendencia.")

# ---------------------------------------------------------
# RANKING INFERIOR (Top Municipios)
# ---------------------------------------------------------
st.markdown("---")
st.subheader(f"🏆 Top Municipios más Afectados — {contaminante_sel}")
if not df_filtered.empty:
    df_ranking = df_filtered.groupby('Nombre del Municipio')['Promedio'].mean().reset_index()
    df_ranking = df_ranking.sort_values(by='Promedio', ascending=False).head(8)
    
    fig_bar = px.bar(
        df_ranking,
        x='Promedio',
        y='Nombre del Municipio',
        orientation='h',
        text_auto='.2f',
        color='Promedio',
        color_continuous_scale='Oranges'
    )
    fig_bar.add_vline(x=15, line_dash="dash", line_color="red", annotation_text="Límite OMS")
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, margin={"r":0,"t":10,"l":0,"b":0}, height=380)
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("No hay suficientes datos para el ranking.")
