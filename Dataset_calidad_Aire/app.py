"""
Panel Ejecutivo de Calidad del Aire - Colombia
=============================================
Aplicación analítica desarrollada en Streamlit para la exploración, evaluación de
riesgo ambiental y exportación de datos de calidad del aire (fuente IDEAM).

Arquitectura y criterios de diseño:
- Fuente de datos: `Dataset_calidad_Aire/airquality_clean_II.csv` (previamente
  depurado y estandarizado).
- Enfoque en contaminantes atmosféricos: Se excluyen variables meteorológicas
  y se conservan únicamente contaminantes del aire (`CO`, `NO`, `NO2`, `O3`,
  `PM10`, `PM2.5`, `PST`, `SO2`).
- Umbrales dinámicos por contaminante: Cada contaminante con guía de referencia
  se evalúa contra su propio umbral y unidad configurados en `LIMITES_OMS`.
- Compatibilidad geoespacial: La función `crear_mapa_estaciones` detecta si la
  versión de Plotly instalada expone `px.scatter_map` o `px.scatter_mapbox` para
  evitar fallos de compatibilidad en entornos de despliegue.
"""

import unicodedata
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# Configura el lienzo en modo ancho para aprovechar pantallas de escritorio y
# dar espacio suficiente a las grillas de KPIs, gráficos y tablas laterales.
st.set_page_config(
    page_title="Panel Ejecutivo de Calidad del Aire - Colombia",
    layout="wide",
)

# Contaminantes atmosféricos del dataset (se excluyen variables meteorológicas).
CONTAMINANTES_ATMOSFERICOS = [
    "CO",
    "NO",
    "NO2",
    "O3",
    "PM10",
    "PM2.5",
    "PST",
    "SO2",
]

# Límites de referencia dinámicos por contaminante (en µg/m³).
# Las variables sin límite oficial definido en este diccionario (`NO`, `PST`)
# se muestran en modo informativo sin activar comparación de umbral OMS.
LIMITES_OMS = {
    "PM2.5": {
        "umbral": 5.0,
        "criterio": "Guía anual OMS",
        "unidad": "µg/m³",
    },
    "PM10": {
        "umbral": 15.0,
        "criterio": "Guía anual OMS",
        "unidad": "µg/m³",
    },
    "NO2": {
        "umbral": 10.0,
        "criterio": "Guía anual OMS",
        "unidad": "µg/m³",
    },
    "O3": {
        "umbral": 100.0,
        "criterio": "Guía 8h OMS",
        "unidad": "µg/m³",
    },
    "SO2": {
        "umbral": 40.0,
        "criterio": "Guía 24h OMS",
        "unidad": "µg/m³",
    },
    "CO": {
        "umbral": 4000.0,
        "criterio": "Guía 24h OMS (4 mg/m³)",
        "unidad": "µg/m³",
    },
}

# Catálogo de definiciones técnicas para los contaminantes del sistema.
GLOSARIO_CONTAMINANTES = {
    "CO": (
        "**Monóxido de Carbono (CO):** Gas incoloro e inodoro generado "
        "principalmente por la combustión incompleta en fuentes móviles "
        "(vehículos y transporte) e industriales. Referencia de control en este "
        "tablero: 4.000 µg/m³ (equivalente a 4 mg/m³ en guía de 24h)."
    ),
    "PM10": (
        "**Material Particulado PM10:** Pequeñas partículas sólidas o líquidas de "
        "polvo, cenizas, hollín o humo con diámetro menor a 10 micras que "
        "ingresan al sistema respiratorio alto. Referencia anual OMS: 15,0 µg/m³."
    ),
    "PM2.5": (
        "**Material Particulado PM2.5:** Partículas finas respirables con diámetro "
        "inferior a 2.5 micras; debido a su tamaño, penetran profundamente en los "
        "pulmones y el torrente sanguíneo. Referencia anual OMS: 5,0 µg/m³."
    ),
    "NO2": (
        "**Dióxido de Nitrógeno (NO2):** Gas altamente irritante proveniente de "
        "procesos de combustión a alta temperatura (tráfico vehicular e "
        "industrias de energía). Referencia anual OMS: 10,0 µg/m³."
    ),
    "SO2": (
        "**Dióxido de Azufre (SO2):** Gas incoloro pero con olor penetrante, "
        "originado principalmente por la quema de combustibles fósiles que "
        "contienen azufre (carbón y petróleo). Referencia 24h OMS: 40,0 µg/m³."
    ),
    "O3": (
        "**Ozono Troposférico (O3):** Gas secundario formado cuando los "
        "contaminantes reaccionan con la luz solar; componente clave del smog "
        "fotoquímico en zonas urbanas. Referencia 8h OMS: 100,0 µg/m³."
    ),
    "NO": (
        "**Monóxido de Nitrógeno (NO):** Gas precursor de la contaminación "
        "fotoquímica emitido por vehículos y procesos de combustión. Variable "
        "de monitoreo sin umbral guía único asignado en este panel."
    ),
    "PST": (
        "**Partículas Suspendidas Totales (PST):** Fracción total de partículas "
        "sólidas o líquidas suspendidas en el aire. Variable de monitoreo sin "
        "umbral guía único asignado en este panel."
    ),
}

# Diccionario indexado por nombre de departamento normalizado (sin tildes, en
# formato título) para contextualizar la gobernanza ambiental territorial.
AUTORIDADES_AMBIENTALES = {
    "Amazonas": "Corpoamazonia",
    "Antioquia": "Corantioquia / Cornare / Área Metropolitana del Valle de Aburrá",
    "Arauca": "Corporinoquia",
    "Atlantico": "CRA (Corporación Autónoma Regional del Atlántico)",
    "Bogota, D.C.": "Secretaría Distrital de Ambiente (SDA)",
    "Bolivar": "Cardique / EPA Cartagena / CSB",
    "Boyaca": "Corpoboyacá",
    "Caldas": "Corpocaldas",
    "Caqueta": "Corpoamazonia",
    "Casanare": "Corporinoquia",
    "Cauca": "CRC (Corporación Autónoma Regional del Cauca)",
    "Cesar": "Corpocesar",
    "Choco": "Codechocó",
    "Cordoba": "CVS (Corporación Autónoma Regional de los Valles del Sinú y del San Jorge)",
    "Cundinamarca": "CAR (Corporación Autónoma Regional de Cundinamarca)",
    "Guainia": "CDA",
    "Guaviare": "CDA",
    "Huila": "CAM (Corporación Autónoma Regional del Alto Magdalena)",
    "La Guajira": "Corpoguajira",
    "Magdalena": "Corpamag / DADSA",
    "Meta": "Cormacarena",
    "Narino": "Corponariño",
    "Norte De Santander": "Corponor",
    "Putumayo": "Corpoamazonia",
    "Quindio": "CRQ (Corporación Autónoma Regional del Quindío)",
    "Risaralda": "Carder",
    "San Andres, Providencia Y Santa Catalina": "Coralina",
    "Santander": "CDMB / CAS",
    "Sucre": "Carsucre",
    "Tolima": "Cortolima",
    "Valle Del Cauca": "CVC (Corporación Autónoma Regional del Valle del Cauca)",
    "Vaupes": "CDA",
    "Vichada": "Corporinoquia",
}


def normalizar_texto(texto):
    """Estandariza cadenas eliminando acentos diacríticos y aplicando formato título."""
    if pd.isna(texto):
        return texto
    texto_str = str(texto).strip()
    nfkd_form = unicodedata.normalize("NFKD", texto_str)
    texto_sin_tildes = "".join(
        c for c in nfkd_form if not unicodedata.combining(c)
    )
    return texto_sin_tildes.title()


def obtener_config_oms(variable):
    """Retorna (umbral, unidad, criterio) si el contaminante tiene límite OMS."""
    clave = str(variable).strip().upper() if pd.notna(variable) else ""
    config = LIMITES_OMS.get(clave)
    if config is None:
        return None, "µg/m³", None
    return (
        float(config["umbral"]),
        str(config["unidad"]),
        str(config["criterio"]),
    )


def obtener_autoridad_ambiental(depto):
    """Retorna la autoridad ambiental asociada a un departamento normalizado."""
    if pd.isna(depto):
        return "Autoridad Ambiental Regional / IDEAM"
    return AUTORIDADES_AMBIENTALES.get(
        str(depto).strip(),
        "Corporación Autónoma Regional / IDEAM",
    )


@st.cache_data
def load_data():
    """Carga, filtra a contaminantes atmosféricos y normaliza el dataset."""
    df = pd.read_csv("Dataset_calidad_Aire/airquality_clean_II.csv")

    if "Nombre del Departamento" in df.columns:
        df["Nombre del Departamento"] = df["Nombre del Departamento"].apply(
            normalizar_texto
        )
        df["Autoridad Ambiental"] = df["Nombre del Departamento"].apply(
            obtener_autoridad_ambiental
        )

    if "Nombre del Municipio" in df.columns:
        df["Nombre del Municipio"] = df["Nombre del Municipio"].apply(
            normalizar_texto
        )

    if "Variable" in df.columns:
        df["Variable"] = df["Variable"].apply(lambda x: str(x).strip().upper())
        df = df[df["Variable"].isin(CONTAMINANTES_ATMOSFERICOS)].copy()

    return df


def calcular_zoom_y_centro(lat_series, lon_series, es_nacional=False):
    """Calcula coordenadas centrales y nivel de zoom adaptativo para el mapa."""
    lat_clean = pd.to_numeric(lat_series, errors="coerce").dropna()
    lon_clean = pd.to_numeric(lon_series, errors="coerce").dropna()

    if lat_clean.empty or lon_clean.empty:
        return {"lat": 4.5709, "lon": -74.2973}, 5.0

    centro = {"lat": float(lat_clean.mean()), "lon": float(lon_clean.mean())}
    if es_nacional:
        return {"lat": 4.5709, "lon": -74.2973}, 5.0

    span = max(
        float(lat_clean.max() - lat_clean.min()),
        float(lon_clean.max() - lon_clean.min()),
    )
    if span < 0.15:
        zoom = 10.5
    elif span < 0.5:
        zoom = 9.0
    elif span < 1.5:
        zoom = 7.8
    elif span < 3.5:
        zoom = 6.5
    else:
        zoom = 5.5

    return centro, zoom


def crear_mapa_estaciones(df_estaciones, contaminante, unidad, centro, zoom):
    """Construye el mapa de burbujas georreferenciadas de estaciones/municipios."""
    usa_scatter_map = hasattr(px, "scatter_map")
    scatter_fn = px.scatter_map if usa_scatter_map else px.scatter_mapbox

    fig = scatter_fn(
        df_estaciones,
        lat="Latitud",
        lon="Longitud",
        color="Promedio_Estacion",
        size="Tamano_Burbuja",
        hover_name="Nombre del Municipio",
        hover_data={
            "Nombre del Departamento": True,
            "Autoridad Ambiental": True,
            "Promedio_Estacion": ":.2f",
            "Muestras": True,
            "Latitud": ":.4f",
            "Longitud": ":.4f",
            "Tamano_Burbuja": False,
        },
        labels={
            "Promedio_Estacion": f"Media {contaminante} ({unidad})",
            "Nombre del Departamento": "Departamento",
            "Muestras": "Registros",
        },
        color_continuous_scale="Turbo",
    )

    layout_geo_key = "map" if usa_scatter_map else "mapbox"
    fig.update_layout(
        **{
            layout_geo_key: {
                "style": "carto-positron",
                "center": centro,
                "zoom": zoom,
            }
        },
        margin={"r": 0, "t": 10, "l": 0, "b": 0},
        height=440,
    )

    return fig


# Carga inicial del dataset filtrado a contaminantes atmosféricos.
df = load_data()

# ---------------------------------------------------------
# BARRA LATERAL / FILTROS CORPORATIVOS
# ---------------------------------------------------------
st.sidebar.markdown("### Panel de Control")
st.sidebar.markdown("Parámetros gerenciales de segmentación")

departamentos_disponibles = sorted(df["Nombre del Departamento"].dropna().unique())
depto_sel = st.sidebar.selectbox(
    "Departamento / Región",
    ["Todos los departamentos"] + departamentos_disponibles,
)

anos_disponibles = sorted(df["Año"].dropna().unique())

st.sidebar.markdown("---")
st.sidebar.markdown("Rango Temporal de Análisis")
col_y1, col_y2 = st.sidebar.columns(2)
with col_y1:
    ano_inicio = st.selectbox("Año Inicio", anos_disponibles, index=0)
with col_y2:
    ano_fin = st.selectbox(
        "Año Fin",
        anos_disponibles,
        index=len(anos_disponibles) - 1,
    )

if ano_inicio > ano_fin:
    ano_inicio, ano_fin = ano_fin, ano_inicio

st.sidebar.markdown("---")
variables_disponibles = sorted(df["Variable"].dropna().unique())
contaminante_sel = st.sidebar.selectbox(
    "Contaminante Atmosférico Evaluado",
    variables_disponibles,
)

umbral_activo, unidad_activa, criterio_activo = obtener_config_oms(contaminante_sel)

df_filtered = df.copy()
if depto_sel != "Todos los departamentos":
    df_filtered = df_filtered[df_filtered["Nombre del Departamento"] == depto_sel]

df_filtered = df_filtered[
    (df_filtered["Año"] >= ano_inicio) & (df_filtered["Año"] <= ano_fin)
]
df_filtered = df_filtered[df_filtered["Variable"] == contaminante_sel]

# ---------------------------------------------------------
# ENCABEZADO Y BLOQUE DE KPIs EMPRESARIALES (DOBLE FILA)
# ---------------------------------------------------------
st.markdown("### Panel Ejecutivo de Calidad del Aire")
st.markdown("Sistema de Monitoreo Analítico y Evaluación de Riesgo Ambiental • IDEAM")

promedio_general = float(df_filtered["Promedio"].mean()) if not df_filtered.empty else 0.0
total_registros = len(df_filtered)
volatilidad = float(df_filtered["Promedio"].std()) if not df_filtered.empty else 0.0

if umbral_activo is not None and umbral_activo > 0:
    brecha_oms = ((promedio_general - umbral_activo) / umbral_activo) * 100
else:
    brecha_oms = None

if not df_filtered.empty:
    medias_mun = df_filtered.groupby("Nombre del Municipio")["Promedio"].mean()
    mun_critico = medias_mun.idxmax()
    val_critico = float(medias_mun.max())
    max_absoluto = float(
        df_filtered["Máximo"].max()
        if "Máximo" in df_filtered.columns
        else df_filtered["Promedio"].max()
    )
    registros_criticos = (
        int((df_filtered["Promedio"] > umbral_activo).sum())
        if umbral_activo is not None
        else None
    )
    municipios_cobertura = int(df_filtered["Nombre del Municipio"].nunique())

    df_anos_prom = df_filtered.groupby("Año")["Promedio"].mean().reset_index()
    if len(df_anos_prom) >= 2:
        val_inicial = float(df_anos_prom.iloc[0]["Promedio"])
        val_final = float(df_anos_prom.iloc[-1]["Promedio"])
        variacion_interanual = (
            ((val_final - val_inicial) / val_inicial) * 100
            if val_inicial > 0
            else 0.0
        )
    else:
        variacion_interanual = 0.0
else:
    mun_critico = "N/A"
    val_critico = 0.0
    max_absoluto = 0.0
    registros_criticos = 0 if umbral_activo is not None else None
    municipios_cobertura = 0
    variacion_interanual = 0.0

delta_media = (
    f"{brecha_oms:+.1f}% vs Límite OMS ({umbral_activo:g} {unidad_activa})"
    if brecha_oms is not None
    else "Sin umbral OMS asignado"
)
delta_eventos = (
    f"Superan {umbral_activo:g} {unidad_activa}"
    if registros_criticos is not None
    else "Sin umbral OMS asignado"
)
valor_eventos = (
    f"{registros_criticos:,}".replace(",", ".")
    if registros_criticos is not None
    else "N/A"
)

col1, col2, col3, col4 = st.columns(4)
col1.metric(
    label=f"CONCENTRACIÓN MEDIA ({contaminante_sel})",
    value=f"{promedio_general:.2f} {unidad_activa}",
    delta=delta_media,
    delta_color="inverse" if brecha_oms is not None else "off",
)
col2.metric(
    label="ESTABILIDAD (DESV. EST)",
    value=f"{volatilidad:.2f} {unidad_activa}",
    delta="Variabilidad de registros",
)
col3.metric(
    label="MUNICIPIO CON MAYOR PRESIÓN",
    value=f"{mun_critico}",
    delta=f"Media: {val_critico:.1f} {unidad_activa}",
)
col4.metric(
    label="TOTAL DE MUESTRAS",
    value=f"{total_registros:,}".replace(",", "."),
)

col5, col6, col7, col8 = st.columns(4)
col5.metric(
    label="PICO HISTÓRICO MÁXIMO",
    value=f"{max_absoluto:.2f} {unidad_activa}",
    delta="Valor extremo registrado",
)
col6.metric(
    label="EVENTOS SOBRE EL LÍMITE",
    value=valor_eventos,
    delta=delta_eventos,
    delta_color="inverse" if registros_criticos is not None else "off",
)
col7.metric(
    label="TENDENCIA DEL PERÍODO",
    value=f"{variacion_interanual:+.1f}%",
    delta="Variación inicio vs fin",
    delta_color="inverse",
)
col8.metric(
    label="MUNICIPIOS MONITOREADOS",
    value=f"{municipios_cobertura}",
    delta="Cobertura territorial",
)

st.markdown("---")

# ---------------------------------------------------------
# GLOSARIO TÉCNICO DINÁMICO E INTEGRAL
# ---------------------------------------------------------
with st.expander("Guía de Lectura y Glosario Técnico Detallado (Haga clic para expandir)"):
    st.markdown(
        """
- **Límites de Referencia por Contaminante:** Cada contaminante con guía configurada se evalúa frente a su propio umbral en µg/m³ (PM2.5: 5,0; PM10: 15,0; NO2: 10,0; SO2: 40,0; O3: 100,0; CO: 4.000,0). Las variables sin límite configurado (`NO`, `PST`) se presentan únicamente como monitoreo descriptivo.
- **Catálogo de Contaminantes Atmosféricos:**
        """
    )

    for var in variables_disponibles:
        descrip = GLOSARIO_CONTAMINANTES.get(
            var,
            f"**{var}:** Contaminante atmosférico registrado en el sistema de monitoreo del IDEAM.",
        )
        st.markdown(f"- {descrip}")

    st.markdown(
        """
- **Concentración Media:** Promedio aritmético de los niveles medidos en el período y región seleccionados.
- **Estabilidad (Desviación Estándar):** Mide la dispersión de los datos. Un valor elevado indica fluctuaciones amplias en las concentraciones registradas.
        """
    )

st.markdown("---")

# ---------------------------------------------------------
# NARRATIVA Y DIAGNÓSTICO EJECUTIVO AUTOMÁTICO
# ---------------------------------------------------------
ubicacion_texto = (
    f"en el departamento de **{depto_sel}**"
    if depto_sel != "Todos los departamentos"
    else "a nivel nacional (todos los departamentos)"
)

if not df_filtered.empty:
    tendencia_texto = "al alza" if variacion_interanual > 0 else "a la baja"
    if umbral_activo is not None:
        estado_alerta = "CRÍTICO" if promedio_general > umbral_activo else "ESTABLE"
        cierre_umbral = (
            f"clasificado como **{estado_alerta}** frente al umbral de "
            f"referencia (**{umbral_activo:g} {unidad_activa}** — {criterio_activo})"
        )
    else:
        cierre_umbral = (
            "sin umbral de referencia OMS asignado en este panel (monitoreo descriptivo)"
        )

    st.info(
        f"**Diagnóstico Gerencial:** Durante el período **{ano_inicio}–{ano_fin}**, "
        f"la concentración media de **{contaminante_sel}** {ubicacion_texto} se "
        f"sitúa en **{promedio_general:.2f} {unidad_activa}**, {cierre_umbral}. "
        f"Se registra una tendencia **{tendencia_texto}** del "
        f"**{variacion_interanual:+.1f}%**, con cobertura en "
        f"**{municipios_cobertura}** municipios analizados."
    )

st.markdown("---")

# ---------------------------------------------------------
# SECCIÓN DE PESTAÑAS (TABS) CORPORATIVAS
# ---------------------------------------------------------
tab_general, tab_comparativa, tab_exportar = st.tabs(
    ["Analítica General y Mapas", "Comparativa Territorial", "Repositorio y Exportación"]
)

with tab_general:
    col_grafico, col_ranking = st.columns([1.2, 1])

    with col_grafico:
        st.markdown(f"#### Evolución Histórica Anual — {contaminante_sel}")
        if not df_filtered.empty:
            df_tendencia = (
                df_filtered.groupby("Año")["Promedio"].mean().reset_index()
            )
            fig_line = px.line(
                df_tendencia,
                x="Año",
                y="Promedio",
                markers=True,
                line_shape="spline",
                title=f"Comportamiento Histórico Promedio de {contaminante_sel} ({unidad_activa})",
            )
            if umbral_activo is not None:
                fig_line.add_hline(
                    y=umbral_activo,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Límite Referencia ({umbral_activo:g} {unidad_activa})",
                )
            fig_line.update_layout(
                margin={"r": 0, "t": 30, "l": 0, "b": 0},
                height=380,
                xaxis_title="Año de Monitoreo",
                yaxis_title=f"Concentración Media ({contaminante_sel}, {unidad_activa})",
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.warning("No hay datos para mostrar en la tendencia.")

    with col_ranking:
        st.markdown(f"#### Top Zonas con Mayor Presión — {contaminante_sel}")
        if not df_filtered.empty:
            df_ranking = (
                df_filtered.groupby("Nombre del Municipio")["Promedio"]
                .mean()
                .reset_index()
            )
            df_ranking = df_ranking.sort_values(
                by="Promedio", ascending=False
            ).head(10)

            fig_bar = px.bar(
                df_ranking,
                x="Promedio",
                y="Nombre del Municipio",
                orientation="h",
                text_auto=".2f",
                color="Promedio",
                color_continuous_scale="Oranges",
                title=f"Ranking de Municipios ({contaminante_sel}, {unidad_activa})",
            )
            if umbral_activo is not None:
                max_eje_x = max(
                    float(df_ranking["Promedio"].max()),
                    umbral_activo,
                )
                if umbral_activo <= max_eje_x * 1.15:
                    fig_bar.add_vline(
                        x=umbral_activo,
                        line_dash="dash",
                        line_color="red",
                        annotation_text=f"Límite ({umbral_activo:g} {unidad_activa})",
                    )
            fig_bar.update_layout(
                yaxis={"categoryorder": "total ascending"},
                margin={"r": 0, "t": 30, "l": 0, "b": 0},
                height=380,
                xaxis_title=f"Concentración Promedio ({contaminante_sel}, {unidad_activa})",
                yaxis_title="Municipio",
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No hay suficientes datos para el ranking.")

    st.markdown("---")

    titulo_mapa = (
        f"Ubicación de Estaciones y Gestión Ambiental en {depto_sel}"
        if depto_sel != "Todos los departamentos"
        else f"Ubicación Nacional de Estaciones y Municipios — {contaminante_sel}"
    )
    st.markdown(f"#### {titulo_mapa}")

    if (
        not df_filtered.empty
        and "Latitud" in df_filtered.columns
        and "Longitud" in df_filtered.columns
    ):
        df_geo_valid = df_filtered.dropna(subset=["Latitud", "Longitud"]).copy()

        if not df_geo_valid.empty:
            df_estaciones = df_geo_valid.groupby(
                ["Nombre del Departamento", "Nombre del Municipio", "Autoridad Ambiental"],
                as_index=False,
            ).agg(
                Latitud=("Latitud", "mean"),
                Longitud=("Longitud", "mean"),
                Promedio_Estacion=("Promedio", "mean"),
                Muestras=("Promedio", "count"),
            )
            df_estaciones["Tamano_Burbuja"] = df_estaciones[
                "Promedio_Estacion"
            ].clip(lower=1.0)

            centro_mapa, zoom_mapa = calcular_zoom_y_centro(
                df_estaciones["Latitud"],
                df_estaciones["Longitud"],
                es_nacional=(depto_sel == "Todos los departamentos"),
            )

            col_map_view, col_map_info = st.columns([2.1, 1])

            with col_map_view:
                fig_map = crear_mapa_estaciones(
                    df_estaciones,
                    contaminante_sel,
                    unidad_activa,
                    centro_mapa,
                    zoom_mapa,
                )
                st.plotly_chart(fig_map, use_container_width=True)

            with col_map_info:
                st.markdown("##### Gobernanza y Estaciones Activas")
                if depto_sel != "Todos los departamentos":
                    autoridad_actual = obtener_autoridad_ambiental(depto_sel)
                    st.markdown(
                        f"**Autoridad Ambiental Competente:**  \n{autoridad_actual}"
                    )
                else:
                    st.markdown(
                        "**Autoridad Ambiental Competente:**  \n"
                        "Corporaciones Autónomas Regionales (CAR) / "
                        "Autoridades Urbanas / IDEAM"
                    )

                st.markdown(
                    f"**Municipios / Puntos Georreferenciados:** {len(df_estaciones)}"
                )

                col_media_est = f"Media ({contaminante_sel}, {unidad_activa})"
                df_tabla_est = (
                    df_estaciones[
                        [
                            "Nombre del Municipio",
                            "Nombre del Departamento",
                            "Promedio_Estacion",
                            "Muestras",
                        ]
                    ]
                    .sort_values(by="Promedio_Estacion", ascending=False)
                    .rename(
                        columns={
                            "Nombre del Municipio": "Municipio",
                            "Nombre del Departamento": "Departamento",
                            "Promedio_Estacion": col_media_est,
                        }
                    )
                )
                df_tabla_est[col_media_est] = df_tabla_est[col_media_est].round(2)
                st.dataframe(df_tabla_est, use_container_width=True, height=280)

            st.caption(
                "Pase el cursor sobre cada punto para consultar el municipio, "
                "la autoridad ambiental asociada, la concentración media y el "
                "volumen de registros en el período seleccionado."
            )
        else:
            st.warning(
                "Los registros filtrados no contienen coordenadas válidas de latitud y longitud."
            )
    else:
        st.warning("No hay datos geográficos disponibles para los filtros seleccionados.")

with tab_comparativa:
    st.markdown("#### Análisis de Comparativa Cruzada por Departamento")
    st.markdown(
        "Seleccione dos regiones o departamentos diferentes para contrastar "
        "su comportamiento histórico."
    )

    col_comp1, col_comp2 = st.columns(2)
    with col_comp1:
        dep1 = st.selectbox("Seleccionar Región A", departamentos_disponibles, index=0)
    with col_comp2:
        dep2 = st.selectbox(
            "Seleccionar Región B",
            departamentos_disponibles,
            index=min(1, len(departamentos_disponibles) - 1),
        )

    df_comp = df[
        (df["Variable"] == contaminante_sel)
        & (df["Año"] >= ano_inicio)
        & (df["Año"] <= ano_fin)
    ]
    df_comp_filtered = df_comp[
        df_comp["Nombre del Departamento"].isin([dep1, dep2])
    ]

    if not df_comp_filtered.empty:
        df_comp_trend = (
            df_comp_filtered.groupby(["Año", "Nombre del Departamento"])["Promedio"]
            .mean()
            .reset_index()
        )

        fig_comp = px.line(
            df_comp_trend,
            x="Año",
            y="Promedio",
            color="Nombre del Departamento",
            markers=True,
            line_shape="spline",
            title=f"Comparativa Cruzada de {contaminante_sel} ({unidad_activa}): {dep1} vs {dep2}",
        )
        if umbral_activo is not None:
            fig_comp.add_hline(
                y=umbral_activo,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Límite Referencia ({umbral_activo:g} {unidad_activa})",
            )
        fig_comp.update_layout(
            margin={"r": 0, "t": 30, "l": 0, "b": 0},
            height=420,
            xaxis_title="Año de Evaluación",
            yaxis_title=f"Concentración Promedio ({contaminante_sel}, {unidad_activa})",
        )
        st.plotly_chart(fig_comp, use_container_width=True)

        st.markdown("#### Resumen Estadístico Comparativo")
        col_max_comp = (
            "Máximo" if "Máximo" in df_comp_filtered.columns else "Promedio"
        )
        df_resumen_comp = (
            df_comp_filtered.groupby("Nombre del Departamento")
            .agg(
                Concentracion_Promedio=("Promedio", "mean"),
                Pico_Maximo=(col_max_comp, "max"),
                Muestras_Totales=("Promedio", "count"),
            )
            .reset_index()
        )
        st.dataframe(df_resumen_comp, use_container_width=True)
    else:
        st.warning(
            "No hay suficientes datos cruzados para generar la comparativa "
            "con las regiones seleccionadas."
        )

with tab_exportar:
    st.markdown("#### Exportación de Datos Procesados")
    st.markdown(
        "Descargue el conjunto de datos filtrados actualmente para "
        "integraciones o reportes externos en formato estructurado."
    )

    if not df_filtered.empty:
        csv_data = df_filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Descargar Dataset Filtrado (.csv)",
            data=csv_data,
            file_name=f"reporte_calidad_aire_{contaminante_sel}.csv",
            mime="text/csv",
        )
        st.dataframe(df_filtered.head(100), use_container_width=True)
        st.caption(
            "Vista previa de los primeros 100 registros correspondientes a la selección actual."
        )
    else:
        st.warning("No hay registros disponibles para exportar con los filtros actuales.")
