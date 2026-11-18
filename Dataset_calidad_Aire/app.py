import streamlit as st
import pandas as pd
import plotly.express as px
import unicodedata

# Configuración de página en modo ancho (Wide)
st.set_page_config(page_title="Panel Ejecutivo de Calidad del Aire - Colombia", layout="wide")

# Función robusta para normalizar texto por seguridad
def normalizar_texto(texto):
    if pd.isna(texto):
        return texto
    texto_str = str(texto).strip()
    nfkd_form = unicodedata.normalize('NFKD', texto_str)
    texto_sin_tildes = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    return texto_sin_tildes.title()

# Carga de datos apuntando al archivo limpio unificado
@st.cache_data
def load_data():
    df = pd.read_csv('Dataset_calidad_Aire/airquality_clean_II.csv')
    
    if 'Nombre del Departamento' in df.columns:
        df['Nombre del Departamento'] = df['Nombre del Departamento'].apply(normalizar_texto)
    if 'Nombre del Municipio' in df.columns:
        df['Nombre del Municipio'] = df['Nombre del Municipio'].apply(normalizar_texto)
    if 'Variable' in df.columns:
        df['Variable'] = df['Variable'].apply(lambda x: str(x).strip().upper())
        
    return df

df = load_data()

# ---------------------------------------------------------
# BARRA LATERAL / FILTROS CORPORATIVOS LIMPIOS Y JERÁRQUICOS
# ---------------------------------------------------------
st.sidebar.markdown("### Panel de Control")
st.sidebar.markdown("Parámetros gerenciales de segmentación")

departamentos_disponibles = sorted(df['Nombre del Departamento'].dropna().unique())
depto_sel = st.sidebar.selectbox("Departamento / Región", ["Todos los departamentos"] + departamentos_disponibles)

anos_disponibles = sorted(df['Año'].dropna().unique())
val_min, val_max = int(min(anos_disponibles)), int(max(anos_disponibles))

st.sidebar.markdown("---")
st.sidebar.markdown("Rango Temporal de Análisis")
col_y1, col_y2 = st.sidebar.columns(2)
with col_y1:
    ano_inicio = st.selectbox("Año Inicio", anos_disponibles, index=0)
with col_y2:
    ano_fin = st.selectbox("Año Fin", anos_disponibles, index=len(anos_disponibles)-1)

if ano_inicio > ano_fin:
    ano_inicio, ano_fin = ano_fin, ano_inicio

st.sidebar.markdown("---")
variables_disponibles = sorted(df['Variable'].dropna().unique())
contaminante_sel = st.sidebar.selectbox("Contaminante / Variable Evaluada", variables_disponibles)

# Filtrado dinámico principal
df_filtered = df.copy()
if depto_sel != "Todos los departamentos":
    df_filtered = df_filtered[df_filtered['Nombre del Departamento'] == depto_sel]

df_filtered = df_filtered[(df_filtered['Año'] >= ano_inicio) & (df_filtered['Año'] <= ano_fin)]
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
col1.metric(label=f"CONCENTRACIÓN MEDIA ({contaminante_sel})", value=f"{promedio_general:.2f}", delta=f"{brecha_oms:+.1f}% vs Límite OMS", delta_color="inverse")
col2.metric(label="ESTABILIDAD (DESV. EST)", value=f"{volatilidad:.2f}", delta="Variabilidad de registros")
col3.metric(label="MUNICIPIO CON MAYOR PRESIÓN", value=f"{mun_critico}", delta=f"Pico: {val_critico:.1f}")
col4.metric(label="TOTAL DE MUESTRAS", value=f"{total_registros:,}".replace(",", "."))

# Fila 2 de KPIs
col5, col6, col7, col8 = st.columns(4)
col5.metric(label="PICO HISTÓRICO MÁXIMO", value=f"{max_absoluto:.2f}", delta="Valor extremo registrado")
col6.metric(label="EVENTOS SOBRE EL LÍMITE", value=f"{registros_criticos:,}".replace(",", "."), delta=f"Superan {limite_oms} de referencia", delta_color="inverse")
col7.metric(label="TENDENCIA DEL PERÍODO", value=f"{variacion_interanual:+.1f}%", delta="Variación inicio vs fin", delta_color="inverse")
col8.metric(label="MUNICIPIOS MONITOREADOS", value=f"{municipios_cobertura}", delta="Cobertura territorial")

st.markdown("---")

# ---------------------------------------------------------
# GLOSARIO TÉCNICO DINÁMICO E INTEGRAL
# ---------------------------------------------------------
with st.expander("Guía de Lectura y Glosario Técnico Detallado (Haga clic para expandir)"):
    st.markdown(
        """
        * **¿Qué es el Límite de Referencia OMS?** Es el valor internacional recomendado por la **Organización Mundial de la Salud** (fijado en 15.0 unidades para control general) para proteger la salud respiratoria a largo plazo. Superar este umbral representa una alerta ambiental.
        * **Catálogo de Contaminantes y Variables del Sistema:**
        """
    )
    
    glosario_dict = {
        "CO": "**Monóxido de Carbono (CO):** Gas incoloro e inodoro generado principalmente por la combustión incompleta en fuentes móviles (vehículos y transporte) e industriales.",
        "PM10": "**Material Particulado PM10:** Pequeñas partículas sólidas o líquidas de polvo, cenizas, hollín o humo con diámetro menor a 10 micras que ingresan al sistema respiratorio alto.",
        "PM2.5": "**Material Particulado PM2.5:** Partículas finas respirables con diámetro inferior a 2.5 micras; debido a su tamaño, penetran profundamente en los pulmones y el torrente sanguíneo.",
        "NO2": "**Dióxido de Nitrógeno (NO2):** Gas altamente irritante proveniente de procesos de combustión a alta temperatura (tráfico vehicular e industrias de energía).",
        "SO2": "**Dióxido de Azufre (SO2):** Gas incoloro pero con olor penetrante, originado principalmente por la quema de combustibles fósiles que contienen azufre (carbón y petróleo).",
        "O3": "**Ozono Troposférico (O3):** Gas secundario formado cuando los contaminantes reaccionan con la luz solar; componente clave del smog fotoquímico en zonas urbanas.",
        "NO": "**Monóxido de Nitrógeno (NO):** Gas precursor de la contaminación fotoquímica emitido por vehículos y procesos de combustión.",
        "NOX": "**Óxidos de Nitrógeno (NOx):** Grupo de gases compuestos por nitrógeno y oxígeno, altamente reactivos y generados en procesos de combustión urbana e industrial."
    }
    
    for var in variables_disponibles:
        descrip = glosario_dict.get(var, f"**{var}:** Variable ambiental registrada en el sistema de monitoreo de calidad del aire del IDEAM.")
        st.markdown(f"- {descrip}")
        
    st.markdown(
        """
        * **Concentración Media:** Promedio aritmético de los niveles medidos en el período y región seleccionados.
        * **Estabilidad (Desviación Estándar):** Mide la dispersión de los datos. Un valor elevado indica fluctuaciones extremas y repentinas en la contaminación.
        """
    )

st.markdown("---")

# ---------------------------------------------------------
# NARRATIVA Y DIAGNÓSTICO EJECUTIVO AUTOMÁTICO
# ---------------------------------------------------------
ubicacion_texto = f"en el departamento de **{depto_sel}**" if depto_sel != "Todos los departamentos" else "a nivel nacional (todos los departamentos)"

if not df_filtered.empty:
    estado_alerta = "CRÍTICO" if promedio_general > limite_oms else "ESTABLE"
    tendencia_texto = "a la alza" if variacion_interanual > 0 else "a la baja"
    st.info(
        f"**Diagnóstico Gerencial:** Durante el período **{ano_inicio}–{ano_fin}**, la concentración media de **{contaminante_sel}** "
        f"{ubicacion_texto} se sitúa en **{promedio_general:.2f}**, un nivel clasificado como **{estado_alerta}** "
        f"frente al umbral internacional de referencia (15.0). Se registra una tendencia **{tendencia_texto}** del **{variacion_interanual:+.1f}%**, "
        f"evidenciando presión ambiental en **{municipios_cobertura}** municipios analizados."
    )

st.markdown("---")

# ---------------------------------------------------------
# SECCIÓN DE PESTAÑAS (TABS) CORPORATIVAS
# ---------------------------------------------------------
tab_general, tab_comparativa, tab_exportar = st.tabs(["Analítica General y Mapas", "Comparativa Territorial", "Repositorio y Exportación"])

with tab_general:
    # FILA 1: Evolución Histórica y Ranking de Municipios (Lado a lado)
    col_grafico, col_ranking = st.columns([1.2, 1])

    with col_grafico:
        st.markdown(f"#### Evolución Histórica Anual — {contaminante_sel}")
        if not df_filtered.empty:
            df_tendencia = df_filtered.groupby('Año')['Promedio'].mean().reset_index()
            fig_line = px.line(
                df_tendencia, 
                x='Año', 
                y='Promedio', 
                markers=True,
                line_shape='spline',
                title=f"Comportamiento Histórico Promedio"
            )
            fig_line.add_hline(y=limite_oms, line_dash="dash", line_color="red", annotation_text="Límite Seguro (15.0)")
            fig_line.update_layout(
                margin={"r":0,"t":30,"l":0,"b":0}, 
                height=380,
                xaxis_title="Año de Monitoreo",
                yaxis_title=f"Concentración Media ({contaminante_sel})"
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.warning("No hay datos para mostrar en la tendencia.")

    with col_ranking:
        st.markdown(f"#### Top Zonas con Mayor Presión — {contaminante_sel}")
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
                color_continuous_scale='Oranges',
                title=f"Ranking de Municipios Críticos"
            )
            fig_bar.add_vline(x=limite_oms, line_dash="dash", line_color="red", annotation_text="Límite OMS")
            fig_bar.update_layout(
                yaxis={'categoryorder':'total ascending'}, 
                margin={"r":0,"t":30,"l":0,"b":0}, 
                height=380,
                xaxis_title=f"Concentración Promedio ({contaminante_sel})",
                yaxis_title="Municipio"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No hay suficientes datos para el ranking.")

    st.markdown("---")

    # FILA 2 (ABAJO): MAPA GEOGRÁFICO REAL DE COLOMBIA / SUDAMÉRICA CON FRONTERAS
    titulo_mapa = f"Mapa Geográfico de Estaciones y Ciudades en {depto_sel}" if depto_sel != "Todos los departamentos" else f"Mapa Geográfico Nacional de Colombia — {contaminante_sel}"
    st.markdown(f"#### {titulo_mapa}")

    if not df_filtered.empty and 'Latitud' in df_filtered.columns and 'Longitud' in df_filtered.columns:
        df_map_data = df_filtered.drop_duplicates(subset=['Nombre del Municipio', 'Latitud', 'Longitud'])
        
        # MAPA GEOGRÁFICO NATIVO CON FRONTERAS DE PAÍSES (SUDAMÉRICA / COLOMBIA)
        fig_map = px.scatter_geo(
            df_map_data,
            lat='Latitud',
            lon='Longitud',
            color='Promedio',
            size='Promedio',
            hover_name='Nombre del Municipio',
            hover_data=['Nombre del Departamento', 'Promedio'],
            color_continuous_scale='Viridis',
            scope='south america',
            title=f"Dispersión Territorial sobre Mapa Geográfico ({contaminante_sel})"
        )
        
        # Configuración de proyección enfocada en Colombia con fronteras visibles
        fig_map.update_geos(
            center=dict(lat=4.5709, lon=-74.2973),
            projection_scale=4.5,
            showcountries=True, countrycolor="gray",
            showland=True, landcolor="rgb(240, 240, 240)",
            showocean=True, oceancolor="rgb(230, 242, 255)"
        )
        
        fig_map.update_layout(
            margin={"r":0,"t":30,"l":0,"b":0}, 
            height=450
        )
        st.plotly_chart(fig_map, use_container_width=True)
        st.caption("Nota: Este mapa geográfico muestra los países de la región y ubica las ciudades y estaciones de forma interactiva según el departamento seleccionado.")
    else:
        st.warning("No hay datos geográficos disponibles para los filtros seleccionados.")

with tab_comparativa:
    st.markdown("#### Análisis de Comparativa Cruzada por Departamento")
    st.markdown("Seleccione dos regiones o departamentos diferentes para contrastar su comportamiento histórico frente al estándar.")
    
    col_comp1, col_comp2 = st.columns(2)
    with col_comp1:
        dep1 = st.selectbox("Seleccionar Región A", departamentos_disponibles, index=0)
    with col_comp2:
        dep2 = st.selectbox("Seleccionar Región B", departamentos_disponibles, index=min(1, len(departamentos_disponibles)-1))
    
    df_comp = df[(df['Variable'] == contaminante_sel) & (df['Año'] >= ano_inicio) & (df['Año'] <= ano_fin)]
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
            title=f"Comparativa Cruzada de {contaminante_sel}: {dep1} vs {dep2}"
        )
        fig_comp.add_hline(y=limite_oms, line_dash="dash", line_color="red", annotation_text="Límite Seguro Referencia")
        fig_comp.update_layout(
            margin={"r":0,"t":30,"l":0,"b":0}, 
            height=420,
            xaxis_title="Año de Evaluación",
            yaxis_title=f"Concentración Promedio ({contaminante_sel})"
        )
        st.plotly_chart(fig_comp, use_container_width=True)
        
        st.markdown("#### Resumen Estadístico Comparativo")
        df_resumen_comp = df_comp_filtered.groupby('Nombre del Departamento').agg(
            Concentracion_Promedio=('Promedio', 'mean'),
            Pico_Maximo=('Máximo' if 'Máximo' in df_comp_filtered.columns else 'Promedio', 'max'),
            Muestras_Totales=('Promedio', 'count')
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
            mime="text/csv",
        )
        st.dataframe(df_filtered.head(100), use_container_width=True)
        st.caption("Vista previa de los primeros 100 registros correspondientes a la selección actual.")
    else:
        st.warning("No hay registros disponibles para exportar con los filtros actuales.")
