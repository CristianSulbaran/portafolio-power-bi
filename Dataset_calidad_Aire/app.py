import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de página en modo ancho (Wide)
st.set_page_config(page_title="Panel Ejecutivo de Calidad del Aire - Colombia", layout="wide")

# Carga de datos optimizada con la ruta exacta de tu carpeta
@st.cache_data
def load_data():
    return pd.read_csv('Dataset_calidad_Aire/airquality_clean.csv')

df = load_data()

# ---------------------------------------------------------
# BARRA LATERAL / FILTROS CORPORATIVOS
# ---------------------------------------------------------
st.sidebar.markdown("### Panel de Control")
st.sidebar.markdown("Filtros y parámetros de segmentación")

ciudades_disponibles = sorted(df['Nombre del Departamento'].unique())
ciudad_sel = st.sidebar.selectbox("Ciudad / Departamento Base", ["Todas las ciudades"] + ciudades_disponibles)

anos_disponibles = sorted(df['Año'].unique())
val_min, val_max = int(min(anos_disponibles)), int(max(anos_disponibles))
rango_anos = st.sidebar.slider("Período de Análisis", val_min, val_max, (val_min, val_max))

variables_disponibles = sorted(df['Variable'].unique())
contaminante_sel = st.sidebar.selectbox("Contaminante / Variable", variables_disponibles)

# Filtrado dinámico principal
df_filtered = df.copy()
if ciudad_sel != "Todas las ciudades":
    df_filtered = df_filtered[df_filtered['Nombre del Departamento'] == ciudad_sel]

df_filtered = df_filtered[(df_filtered['Año'] >= rango_anos[0]) & (df_filtered['Año'] <= rango_anos[1])]
df_filtered = df_filtered[df_filtered['Variable'] == contaminante_sel]

# ---------------------------------------------------------
# ENCABEZADO Y BLOQUE DE KPIs EMPRESARIALES (DOBLE FILA)
# ---------------------------------------------------------
st.markdown("### Panel Ejecutivo de Calidad del Aire")
st.markdown("Sistema de Monitoreo Analítico y Evaluación de Riesgo Ambiental • IDEAM")

promedio_general = df_filtered['Promedio'].mean() if not df_filtered.empty else 0
total_registros = len(df_filtered)
limite_oms = 15.0
brecha_oms = ((promedio_general - limite_oms) / limite_oms) * 100 if limite_oms > 0 else 0
volatilidad = df_filtered['Promedio'].std() if not df_filtered.empty else 0

if not df_filtered.empty:
    mun_critico = df_filtered.groupby('Nombre del Municipio')['Promedio'].mean().idxmax()
    val_critico = df_filtered.groupby('Nombre del Municipio')['Promedio'].mean().max()
    max_absoluto = df_filtered['Máximo'].max() if 'Máximo' in df_filtered.columns else df_filtered['Promedio'].max()
    registros_criticos = len(df_filtered[df_filtered['Promedio'] > limite_oms])
    municipios_cobertura = df_filtered['Nombre del Municipio'].nunique()
    
    df_Anos_prom = df_filtered.groupby('Año')['Promedio'].mean().reset_index()
    if len(df_Anos_prom) >= 2:
        val_inicial = df_Anos_prom.iloc[0]['Promedio']
        val_final = df_Anos_prom.iloc[-1]['Promedio']
        variacion_interanual = ((val_final - val_inicial) / val_inicial) * 100 if val_inicial > 0 else 0
    else:
        variacion_interanual = 0.0
else:
    mun_critico = "N/A"
    val_critico = 0
    max_absoluto = 0
    registros_criticos = 0
    municipios_cobertura = 0
    variacion_interanual = 0.0

# Fila 1 de KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric(label=f"PROMEDIO {contaminante_sel}", value=f"{promedio_general:.2f}", delta=f"{brecha_oms:+.1f}% vs Límite OMS", delta_color="inverse")
col2.metric(label="VOLATILIDAD (EST. DEV)", value=f"{volatilidad:.2f}", delta="Estabilidad estadística")
col3.metric(label="MUNICIPIO CRÍTICO", value=f"{mun_critico}", delta=f"Pico: {val_critico:.1f}")
col4.metric(label="MUESTRAS ANALIZADAS", value=f"{total_registros:,}".replace(",", "."))

# Fila 2 de KPIs
col5, col6, col7, col8 = st.columns(4)
col5.metric(label="MÁXIMO ABSOLUTO", value=f"{max_absoluto:.2f}", delta="Pico histórico registrado")
col6.metric(label="REGISTROS CRÍTICOS", value=f"{registros_criticos:,}".replace(",", "."), delta=f"Superan {limite_oms} µg/m³", delta_color="inverse")
col7.metric(label="TENDENCIA PERÍODO", value=f"{variacion_interanual:+.1f}%", delta="Variación inicio vs fin", delta_color="inverse")
col8.metric(label="MUNICIPIOS ACTIVOS", value=f"{municipios_cobertura}", delta="Cobertura territorial")

st.markdown("---")

# ---------------------------------------------------------
# NARRATIVA Y DIAGNÓSTICO EJECUTIVO AUTOMÁTICO
# ---------------------------------------------------------
if not df_filtered.empty:
    estado_alerta = "CRÍTICO" if promedio_general > limite_oms else "ESTABLE"
    tendencia_texto = "a la alza" if variacion_interanual > 0 else "a la baja"
    st.info(
        f"**Diagnóstico Gerencial:** Durante el período **{rango_anos[0]}–{rango_anos[1]}**, la concentración de **{contaminante_sel}** "
        f"en **{ciudad_sel}** muestra un promedio general de **{promedio_general:.2f}**, situándose en un estado **{estado_alerta}**. "
        f"Se observa una variación interanual **{tendencia_texto}** de **{variacion_interanual:+.1f}%**, con **{municipios_cobertura}** municipios "
        f"monitoreados y un total de **{registros_criticos}** eventos excediendo el estándar de la OMS."
    )

st.markdown("---")

# ---------------------------------------------------------
# SECCIÓN DE PESTAÑAS (TABS) CORPORATIVAS AMPLIADAS
# ---------------------------------------------------------
tab_general, tab_comparativa, tab_exportar = st.tabs(["Analítica General y Mapas", "Comparativa Territorial", "Repositorio y Exportación"])

with tab_general:
    col_mapa, col_grafico = st.columns([1, 1.5])

    with col_mapa:
        st.markdown("#### Distribución Geográfica de Estaciones")
        if not df_filtered.empty and 'Latitud' in df_filtered.columns and 'Longitud' in df_filtered.columns:
            df_map_data = df_filtered.drop_duplicates(subset=['Nombre del Municipio', 'Latitud', 'Longitud'])
            
            fig_map = px.scatter(
                df_map_data,
                x='Longitud',
                y='Latitud',
                color='Promedio',
                size='Promedio',
                hover_name='Nombre del Municipio',
                color_continuous_scale='Viridis',
            )
            fig_map.update_layout(margin={"r":0,"t":10,"l":0,"b":0}, height=390, xaxis_title="Longitud", yaxis_title="Latitud")
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning("No hay datos geográficos disponibles para los filtros seleccionados.")

    with col_grafico:
        st.markdown(f"#### Tendencia Histórica Anual — {contaminante_sel}")
        if not df_filtered.empty:
            df_tendencia = df_filtered.groupby('Año')['Promedio'].mean().reset_index()
            fig_line = px.line(
                df_tendencia, 
                x='Año', 
                y='Promedio', 
                markers=True,
                line_shape='spline'
            )
            fig_line.add_hline(y=limite_oms, line_dash="dash", line_color="red", annotation_text="Límite OMS (15 µg/m³)")
            fig_line.update_layout(margin={"r":0,"t":10,"l":0,"b":0}, height=390)
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.warning("No hay datos para mostrar en la tendencia.")

    st.markdown("---")
    st.markdown(f"#### Ranking de Municipios con Mayor Concentración — {contaminante_sel}")
    if not df_filtered.empty:
        df_ranking = df_filtered.groupby('Nombre del Municipio')['Promedio'].mean().reset_index()
        df_ranking = df_ranking.sort_values(by='Promedio', ascending=False).head(10)
        
        fig_bar = px.bar(
            df_ranking,
            x='Promedio',
            y='Nombre del Municipio',
            orientation='h',
            text_auto='.2f',
            color='Promedio',
            color_continuous_scale='Oranges'
        )
        fig_bar.add_vline(x=limite_oms, line_dash="dash", line_color="red", annotation_text="Límite OMS")
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, margin={"r":0,"t":10,"l":0,"b":0}, height=380)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No hay suficientes datos para el ranking.")

with tab_comparativa:
    st.markdown("#### Análisis de Comparativa Cruzada por Departamento")
    st.markdown("Seleccione dos departamentos diferentes para contrastar su comportamiento histórico bajo el contaminante seleccionado.")
    
    col_comp1, col_comp2 = st.columns(2)
    with col_comp1:
        dep1 = st.selectbox("Seleccionar Región A", ciudades_disponibles, index=0)
    with col_comp2:
        dep2 = st.selectbox("Seleccionar Región B", ciudades_disponibles, index=min(1, len(ciudades_disponibles)-1))
    
    # Filtrado cruzado para la comparativa
    df_comp = df[(df['Variable'] == contaminante_sel) & (df['Año'] >= rango_anos[0]) & (df['Año'] <= rango_anos[1])]
    df_comp_filtered = df_comp[df_comp['Nombre del Departamento'].isin([dep1, dep2])]
    
    if not df_comp_filtered.empty:
        df_comp_trend = df_comp_filtered.groupby(['Año', 'Nombre del Departamento'])['Promedio'].mean().reset_index()
        
        fig_comp = px.line(
            df_comp_trend,
            x='Año',
            y='Promedio',
            color='Nombre del Departamento',
            markers=True,
            line_shape='spline',
            title=f"Comparativa Histórica de {contaminante_sel}: {dep1} vs {dep2}"
        )
        fig_comp.add_hline(y=limite_oms, line_dash="dash", line_color="red", annotation_text="Límite OMS")
        fig_comp.update_layout(margin={"r":0,"t":30,"l":0,"b":0}, height=420)
        st.plotly_chart(fig_comp, use_container_width=True)
        
        # Tabla resumen comparativa
        st.markdown("#### Resumen Estadístico Comparativo")
        df_resumen_comp = df_comp_filtered.groupby('Nombre del Departamento').agg(
            Promedio_General=('Promedio', 'mean'),
            Maximo_Registrado=('Máximo' if 'Máximo' in df_comp_filtered.columns else 'Promedio', 'max'),
            Total_Muestras=('Promedio', 'count')
        ).reset_index()
        st.dataframe(df_resumen_comp, use_container_width=True)
    else:
        st.warning("No hay suficientes datos cruzados para generar la comparativa con las regiones seleccionadas.")

with tab_exportar:
    st.markdown("#### Exportación de Datos Procesados")
    st.markdown("Descargue el conjunto de datos filtrados actualmente para integraciones o reportes externos en formato estructurado.")
    
    if not df_filtered.empty:
        csv_data = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar Dataset Filtrado (.csv)",
            data=csv_data,
            file_name=f"reporte_calidad_aire_{contaminante_sel}.csv",
            mime="text/css" if False else "text/csv",
        )
        st.dataframe(df_filtered.head(100), use_container_width=True)
        st.caption("Vista previa de los primeros 100 registros correspondientes a la selección actual.")
    else:
        st.warning("No hay registros disponibles para exportar con los filtros actuales.")
