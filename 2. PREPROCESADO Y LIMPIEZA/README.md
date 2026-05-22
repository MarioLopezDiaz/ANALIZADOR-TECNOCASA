# 🧹 Módulo de Preprocesamiento, Limpieza y Enriquecimiento

Este módulo constituye el núcleo de la ingeniería de datos del proyecto **Tecnocasa AI Valuator**. Su objetivo es transformar los datos brutos y desestructurados (obtenidos en la fase de adquisición) en un dataset de alta calidad, enriquecido y listo para el entrenamiento de modelos de Machine Learning.

El flujo de trabajo abarca desde la limpieza de tipos de datos y la imputación de valores nulos mediante ML, hasta el análisis de imágenes con IA Generativa y el enriquecimiento geoespacial.

## 📂 Archivos del Módulo

### 1. `2.1_limpieza.py` (Limpieza y Estandarización)
**Propósito:** Procesar el dataset crudo (`raw`) para corregir formatos, manejar valores faltantes y eliminar ruido estadístico.

**Funcionalidades Clave:**
* **Normalización de Strings:** Uso de `Regex` y `Unidecode` para limpiar campos de texto (habitaciones, baños, planta, fecha de construcción).
* **Conversión de Tipos:** Transformación de columnas a formatos numéricos (`int`, `float`) y categóricos optimizados.
* **Imputación Avanzada:** Implementación de `IterativeImputer` (basado en `RandomForestRegressor`) para rellenar valores nulos basándose en las correlaciones con otras variables, superando a la imputación por media/mediana.
* **Detección de Outliers:** Eliminación de registros anómalos (ej: precios o superficies irreales) utilizando el método del Rango Intercuartílico (IQR).

* **Salida:** Genera `tecnocasa_datos_limpios.parquet`.

---

### 2. `2.2_division_datoslimpios_100filas.ipynb` (Optimización de Flujo)
**Propósito:** Crear un subconjunto representativo del dataset limpio para optimizar costes y tiempos en el procesamiento de imágenes.

**Funcionalidades Clave:**
* **Submuestreo:** Selecciona las primeras 100 filas del dataset limpio.

* **Justificación:** El análisis de imágenes con LLMs (Gemini) tiene un coste computacional y de API elevado. Este script permite generar un lote de prueba/validación (`tecnocasa_datos_limpios_100filas.parquet`) para calibrar el análisis visual antes de escalar (o para limitar el alcance en entornos de desarrollo).

---

### 3. `2.3_imagenes_procesado.ipynb` (Visión Artificial con GenAI)
**Propósito:** Extraer características cualitativas ("intangibles") de las viviendas analizando sus fotografías mediante Inteligencia Artificial Generativa.

**Funcionalidades Clave:**
* **Integración con Google Gemini:** Conexión a la API de `Gemini Pro Vision`.
* **Ingeniería de Prompts:** Envío de imágenes con instrucciones específicas para que la IA puntúe del 1 al 5:
    * Nivel de Lujo.
    * Estado de conservación.
    * Modernidad.
    * Calidad de la fotografía.
    * Luminosidad.
* **Parsing Estructurado:** Conversión de las respuestas de la IA en datos tabulares.

* **Salida:** Genera `imagenes_procesadas.parquet`, añadiendo valor semántico visual que los metadatos tradicionales no capturan.

---

### 4. `2.4_enriquecimiento.ipynb` (Feature Engineering y Fusión)
**Propósito:** Enriquecer el dataset con datos externos, análisis de texto y geolocalización, generando el "Master Table" final para el modelado.

**Funcionalidades Clave:**
* **Geocoding Inverso:** Uso de `Geopy (Nominatim)` para convertir direcciones textuales en coordenadas (Latitud/Longitud).
* **Spatial Join:** Mapeo de coordenadas a distritos y barrios oficiales de Madrid utilizando archivos Shapefile (`.shp`) y `Geopandas`.
* **Datos Socioeconómicos:** Cruce con fuentes externas (`rentaMedia.csv`) para añadir la renta media por barrio, una variable predictora crítica.
* **NLP (Procesamiento de Lenguaje Natural):**
    * Análisis de sentimiento (`TextBlob`) de las descripciones.
    * Extracción de keywords (`CountVectorizer`) para detectar términos de valor (ej: "luminoso", "reformado").
* **Fusión Final:** Une los datos tabulares limpios con las *features* de imágenes (del script 2.3) y los datos geoespaciales.

* **Salida Final:** Genera `tecnocasa_modelo.parquet`, el dataset definitivo para la fase de entrenamiento.

* **`2.4_enriquecimiento_TecnocasaRentaSeccion.ipynb`:** Variante de alta granularidad. En lugar del distrito, cruza las coordenadas con los polígonos de las **Secciones Censales** para obtener una métrica de riqueza a nivel micro (calle/bloque).
* **`2.4_enriquecimiento_redpiso.ipynb`:** Adaptación del flujo para el dataset de Redpiso. Añade variables oficiales de GIS medioambiental (distancia a focos de ruido, aeropuertos, ferrocarriles) preparándolo para ser el grupo de control en la fase de modelado.

## 📦 Dependencias Específicas

Este módulo hace uso intensivo de librerías de Ciencia de Datos y Geoespaciales:

* **Manipulación de Datos:** `pandas`, `numpy`.
* **Machine Learning (Imputación):** `scikit-learn`.
* **IA Generativa:** `google-generativeai` (Gemini).
* **Geoespacial:** `geopy`, `geopandas`, `shapely`.
* **NLP:** `textblob`, `unidecode`.

* **Visualización:** `seaborn`, `matplotlib`.

---
**Autor:** Mario López Díaz