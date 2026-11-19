# Tablero de Calidad del Aire en Colombia (IDEAM)

Este proyecto presenta un tablero interactivo para consultar y analizar datos históricos de calidad del aire en Colombia (2011–2025), construido a partir del archivo limpio `airquality_clean_II.csv`. La idea es que cualquier persona pueda revisar cómo se comportan distintos contaminantes, qué municipios concentran mayores niveles, qué autoridad ambiental está detrás de cada departamento y descargar los datos que está viendo.

Accede al dashboard interactivo desplegado en Streamlit: 
<p align="center">
  <a href="https://portafolio-power-bi-rnz4epzuwpjqgrnzd6rxsm.streamlit.app/">
    <img src="https://img.shields.io/badge/Ver_Dashboard-Streamlit-red?style=for-the-badge&logo=streamlit" alt="Ver Dashboard">
  </a>
</p>

## Para que sirve este tablero

Muchas veces los datos ambientales vienen en tablas extensas que cuestan leer a simple vista. Este tablero transforma esa información en indicadores rápidos, gráficos comparativos, un mapa y un glosario para entender qué mide cada variable. Además, contrasta los promedios registrados frente a la referencia de 15,0 µg/m³ el límite diario de la OMS para partículas finas (PM₂,₅) o anual para partículas respirables (PM₁₀), lo que permite identificar de inmediato si la calidad del aire representa un riesgo para la salud o se mantiene dentro de un rango seguro.

## Herramientas y apps usadas

- **Python:** Lenguaje principal de la aplicación y de la limpieza o normalización de textos.
  
- **Pandas y NumPy:** Manejo de tablas, filtros, promedios, desviaciones, conteos y agrupación de datos.
  
- **Streamlit:** Creación de la interfaz web, barra lateral, pestañas, métricas y botón de descarga.
  
- **Plotly Express:** Gráficos de líneas, barras horizontales y mapa de puntos sobre cartografía.
  
- **GitHub y Streamlit Community Cloud:** Almacenamiento del código y los datos, y publicación del tablero en la web.
  

## Estructura del proyecto


```
Dataset_calidad_Aire/
├── app.py
├── airquality_clean_II.csv
├── requierements/
└── README.md
```

## Como funciona el tablero por partes

### Vista general de la pantalla

<img width="1884" height="925" alt="Captura de pantalla 2026-11-19 154531" src="https://github.com/user-attachments/assets/d6dff7f4-794f-4370-9362-00fc0d5123d5" />

Aqui se ve el tablero completo en pantalla ancha. A la izquierda queda el panel de filtros y en el cuerpo principal se distribuyen las métricas, el resumen de estado, las pestañas de navegación, los gráficos y el mapa.

### Panel de control (filtros)

<img width="261" height="491" alt="Captura de pantalla 2026-11-19 154452" src="https://github.com/user-attachments/assets/fa9e53f8-fb73-450d-9504-c120d39e4edb" />

Sirve para demarcar lo que se analiza en todo el tablero:

- **Departamento / Región:** Permite ver todos los departamentos juntos o centrarse en uno solo.
  
- **Rango Temporal de Análisis:** Elige el año de inicio y el año de fin entre 2011 y 2025. Si el año inicial queda mayor que el final, el código los acomoda para no dejar el tablero vacío.
  
- **Contaminante / Variable Evaluada:** Selecciona la variable a revisar, como `CO` o las demás disponibles en el dataset.
  

### Indicadores clave, glosario y diagnostico

<img width="1814" height="585" alt="Captura de pantalla 2026-11-19 154116" src="https://github.com/user-attachments/assets/8205f74b-f7ea-4ffa-a73d-0dbf00c9cb0c" />

Las tarjetas superiores resumen de forma rápida el comportamiento del contaminante filtrado:

* **Concentración media y brecha frente a la OMS:** Muestra el promedio registrado y cuánto se desvía respecto a **15,0 µg/m³** (el límite guía diario de la OMS para partículas finas PM₂,₅ y anual para PM₁₀, usado aquí como umbral base de alerta sanitaria).
* **Estabilidad (desviación estándar):** Indica qué tanto varían las mediciones respecto al promedio.
* **Municipio con mayor presión y pico histórico:** Identifica la zona con el promedio más alto y el valor máximo puntual alcanzado.
* **Eventos sobre el límite:** Contabiliza cuántas mediciones superaron el umbral de referencia de **15,0**, permitiendo dimensionar la frecuencia del riesgo.
* **Tendencia y cobertura:** Refleja la variación porcentual entre el inicio y el fin del período evaluado, junto con el total de muestras y municipios monitoreados.

Debajo de las tarjetas se encuentra el **glosario técnico** desplegable clave para interpretar las unidades y límites específicos de cada contaminante (como CO, PM₂,₅ o PM₁₀) y el **diagnóstico gerencial**, que sintetiza en una sola lectura si la situación es estable o crítica, su tendencia y el alcance territorial.

### Tendencia anual y ranking de municipios

<img width="1779" height="462" alt="Captura de pantalla 2026-11-19 154305" src="https://github.com/user-attachments/assets/6961ff9a-4f07-4509-b813-a075f66324a4" />


Dentro de la pestaña **Analítica General y Mapas**, estos dos gráficos se leen en conjunto para evaluar el comportamiento territorial y temporal:

* **Evolución Histórica Anual:** Muestra la variación del promedio año a año dentro del período seleccionado (2011–2025). La línea roja punteada en **15,0** funciona como un umbral visual de referencia basado en las guías de la OMS para material particulado (**15 µg/m³** anual para PM₁₀ y diario para PM₂,₅), permitiendo identificar de un vistazo qué tan lejos o cerca se ubica la serie histórica respecto a ese estándar internacional.
* **Top Zonas con Mayor Presión:** Ordena los 10 municipios con mayor concentración promedio según el filtro activo (encabezados en esta vista por Facatativá y Cartagena de Indias) y los contrasta contra la línea vertical de referencia para ubicar rápidamente dónde se concentran los registros más elevados.


### Mapa de estaciones y autoridad ambiental

<img width="1804" height="531" alt="Captura de pantalla 2026-11-19 154422" src="https://github.com/user-attachments/assets/d3645c6a-b11d-4fe3-8584-8c7f2bbfc2ff" />


Más abajo en la misma pestaña aparece el mapa con los municipios o puntos georreferenciados, donde el color y el tamaño de cada punto reflejan la concentración media. El zoom se ajusta según lo que estés viendo (todo el país o un departamento).

A la derecha se indica qué autoridad ambiental corresponde al departamento elegido (o el panorama general de autoridades ambientales e IDEAM si ves todo el país), junto con una tabla ordenada con el promedio y el número de muestras por municipio.

### Comparativa entre dos departamentos

<img width="1791" height="784" alt="Captura de pantalla 2026-11-19 154336" src="https://github.com/user-attachments/assets/07d45d01-8e04-4352-92eb-ce7dc6caabab" />


En la pestaña *Comparativa Territorial* puedes elegir dos departamentos (Región A y Región B) para comparar sus curvas anuales en un mismo gráfico usando el contaminante y el rango de años que tengas activos en la barra lateral. Debajo se muestra una tabla resumida con el promedio, el pico máximo y el total de muestras de cada uno.

### Descarga y vista previa de datos

<img width="1822" height="612" alt="Captura de pantalla 2026-11-19 154400" src="https://github.com/user-attachments/assets/fdaaf30c-f95d-4cee-bc10-6f28f2156b06" />


En la pestaña *Repositorio y Exportación* puedes revisar los registros filtrados que alimentan el tablero y descargarlos en un archivo `.csv` con el botón correspondiente.
