# Tablero de Calidad del Aire en Colombia (IDEAM)

Este proyecto presenta un tablero interactivo para consultar y analizar datos históricos de calidad del aire en Colombia (2011–2025), construido a partir del archivo limpio `airquality_clean_II.csv`. La idea es que cualquier persona pueda revisar cómo se comportan distintos contaminantes, qué municipios concentran mayores niveles, qué autoridad ambiental está detrás de cada departamento y descargar los datos que está viendo.

## Para que sirve este tablero

Muchas veces los datos ambientales vienen en tablas extensas que cuesta leer a simple vista. Este tablero organiza esa información en indicadores rápidos, gráficos comparativos, un mapa y un glosario para entender qué mide cada variable. Además, compara los promedios frente a una referencia de 15.0 para dar contexto sobre si el nivel observado está por encima o por debajo de ese umbral.

## Herramientas y apps usadas

- **Python:** Lenguaje principal de la aplicación y de la limpieza o normalización de textos.
  
- **Pandas y NumPy:** Manejo de tablas, filtros, promedios, desviaciones, conteos y agrupación de datos.
  
- **Streamlit:** Creación de la interfaz web, barra lateral, pestañas, métricas y botón de descarga.
  
- **Plotly Express:** Gráficos de líneas, barras horizontales y mapa de puntos sobre cartografía.
  
- **GitHub y Streamlit Community Cloud:** Almacenamiento del código y los datos, y publicación del tablero en la web.
  

## Estructura del proyecto

Plaintext

```
Dataset_calidad_Aire/
├── app.py
├── airquality_clean_II.csv
├── assets/
└── README.md
```

## Como funciona el tablero por partes

### Vista general de la pantalla



Aqui se ve el tablero completo en pantalla ancha. A la izquierda queda el panel de filtros y en el cuerpo principal se distribuyen las métricas, el resumen de estado, las pestañas de navegación, los gráficos y el mapa.

### Panel de control (filtros)

> **\[COLOCAR AQUI: Imagen 6 — Panel de control lateral\]**

Sirve para acotar lo que se analiza en todo el tablero:

- **Departamento / Región:** Permite ver todos los departamentos juntos o centrarse en uno solo.
  
- **Rango Temporal de Análisis:** Elige el año de inicio y el año de fin entre 2011 y 2025. Si el año inicial queda mayor que el final, el código los acomoda para no dejar el tablero vacío.
  
- **Contaminante / Variable Evaluada:** Selecciona la variable a revisar, como `CO` o las demás disponibles en el dataset.
  

### Indicadores clave, glosario y diagnostico

> **\[COLOCAR AQUI: Imagen 1 — Bloque de KPIs y diagnostico gerencial\]**

Las tarjetas de arriba muestran de forma rápida el resumen del filtro elegido: concentración media y su diferencia frente a 15.0, desviación estándar, municipio con mayor promedio, total de muestras, pico máximo, cantidad de registros por encima de 15.0, cambio porcentual entre el primer y último año con datos y cantidad de municipios cubiertos.

Debajo de las tarjetas está el desplegable del glosario para explicar qué significa cada contaminante y cada métrica, y más abajo aparece el cuadro de diagnóstico que resume en una frase el nivel (estable o crítico), la tendencia y el número de municipios involucrados.

### Tendencia anual y ranking de municipios

> **\[COLOCAR AQUI: Imagen 2 — Graficos de evolucion historica y top de municipios\]**

Dentro de la pestaña *Analítica General y Mapas*, estos dos gráficos se leen en conjunto:

- **Evolución Histórica Anual:** Muestra cómo cambia el promedio año a año dentro del rango elegido, con una línea roja punteada en 15.0 para ver si se mantiene por encima de esa referencia.
  
- **Top Zonas con Mayor Presión:** Ordena los 10 municipios con mayor promedio en el filtro actual para ubicar rápido dónde se concentran los valores más altos.
  

### Mapa de estaciones y autoridad ambiental

> **\[COLOCAR AQUI: Imagen 5 — Mapa y tabla de gobernanza y estaciones\]**

Más abajo en la misma pestaña aparece el mapa con los municipios o puntos georreferenciados, donde el color y el tamaño de cada punto reflejan la concentración media. El zoom se ajusta según lo que estés viendo (todo el país o un departamento).

A la derecha se indica qué autoridad ambiental corresponde al departamento elegido (o el panorama general de autoridades ambientales e IDEAM si ves todo el país), junto con una tabla ordenada con el promedio y el número de muestras por municipio.

### Comparativa entre dos departamentos

> **\[COLOCAR AQUI: Imagen 3 — Pestana de comparativa cruzada\]**

En la pestaña *Comparativa Territorial* puedes elegir dos departamentos (Región A y Región B) para comparar sus curvas anuales en un mismo gráfico usando el contaminante y el rango de años que tengas activos en la barra lateral. Debajo se muestra una tabla resumida con el promedio, el pico máximo y el total de muestras de cada uno.

### Descarga y vista previa de datos

> **\[COLOCAR AQUI: Imagen 4 — Pestana de repositorio y exportacion\]**

En la pestaña *Repositorio y Exportación* puedes revisar los registros filtrados que alimentan el tablero y descargarlos en un archivo `.csv` con el botón correspondiente.