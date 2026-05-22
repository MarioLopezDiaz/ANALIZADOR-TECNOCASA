# 📊 Módulo de Análisis Exploratorio de Datos (EDA)

Este módulo representa la fase de diagnóstico y comprensión del dato dentro del proyecto **Tecnocasa AI Valuator**. Antes de alimentar los modelos predictivos, se realiza un análisis estadístico y visual exhaustivo para entender las distribuciones, detectar anomalías, validar hipótesis de negocio y seleccionar las variables más relevantes.

El análisis combina estadística descriptiva clásica con visualizaciones interactivas y análisis geoespacial.

## 📂 Archivos del Módulo

### 1. `3.1_analisis_exploratorio.ipynb` (Cuaderno Principal de EDA)
**Propósito:** Realizar una radiografía completa del dataset `tecnocasa_modelo.parquet` para asegurar la calidad del dato y descubrir patrones de mercado.

**Análisis Realizados:**

* **1. Análisis de la Variable Objetivo (`Precio`):**
    * Estudio de la distribución del precio y precio/m².
    * Comprobación de normalidad (Histogramas y Q-Q Plots).
    * Justificación de la transformación logarítmica (`Log1p`) para corregir el sesgo positivo (skewness) típico del mercado inmobiliario.

* **2. Análisis Univariante y Bivariante:**
    * **Variables Numéricas:** Relación entre Superficie y Precio (Scatter plots). Detección de no-linealidades.
    * **Variables Categóricas:** Impacto de características como "Ascensor", "Terraza" o "Estado de conservación" en el precio final (Boxplots y Violin Plots).
    * **Análisis de Nulos:** Visualización de la matriz de valores faltantes con `missingno` para validar la estrategia de imputación realizada en la fase anterior.

* **3. Análisis de Correlaciones:**
    * Generación de mapas de calor (**Heatmaps**) para identificar multicolinealidad entre variables.
    * Identificación de las "Golden Features" (variables con mayor correlación de Pearson/Spearman con el target).

* **4. Validación de Features de IA (Gemini):**
    * Evaluación estadística de las variables generadas por Visión Artificial (puntuaciones de Lujo, Luminosidad, Modernidad).
    * ¿Influye realmente la puntuación estética de Gemini en el precio de mercado? Visualización de esta relación.

* **5. Análisis Geoespacial:**
    * Visualización de precios medios por Distrito y Barrio.
    * Detección de zonas "calientes" (precios altos) y oportunidades de inversión mediante mapas coropléticos interactivos.

## 📦 Dependencias Específicas

Este cuaderno utiliza librerías avanzadas de visualización y estadística:

* **Visualización Estática:** `matplotlib`, `seaborn` (estilos y paletas de colores).
* **Visualización Interactiva:** `plotly` (gráficos dinámicos y mapas).
* **Análisis de Nulos:** `missingno`.

* **Estadística:** `scipy` (tests de normalidad y correlaciones).
* **Manipulación:** `pandas`, `numpy`.

---
**Autor:** Mario López Díaz