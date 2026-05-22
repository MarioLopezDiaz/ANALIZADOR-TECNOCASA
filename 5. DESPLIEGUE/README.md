# 🚀 Módulo de Despliegue y Aplicación de Usuario

Este módulo materializa todo el trabajo de análisis y modelado en una herramienta funcional e interactiva: el **Tecnocasa AI Dashboard**. 

Se trata de una aplicación web construida con **Streamlit** que permite a usuarios finales (inversores, agentes inmobiliarios o particulares) interactuar con los modelos predictivos en tiempo real, realizar análisis de visión artificial y generar informes profesionales.

## 📂 Arquitectura del Módulo

El despliegue sigue una arquitectura modular donde `app.py` actúa como orquestador (Frontend) y la carpeta `utils/` contiene la lógica de negocio (Backend).

### 1. `app.py` (Punto de Entrada)
**Propósito:** Script principal que renderiza la interfaz de usuario y gestiona el flujo de la aplicación.
**Funcionalidades:**
* **Gestión de Sesión:** Manejo de variables de estado (`st.session_state`) para persistir datos entre recargas (ej: datos de la vivienda, API Key).
* **Navegación:** Estructura de pestañas para separar funcionalidades:
    1.  **Tasadora:** Formulario de entrada de datos y predicción de precio (XGBoost).
    2.  **Análisis Visual (Gemini):** Subida de imágenes para análisis cualitativo con IA.
    3.  **Simulador de Inversión:** Calculadora financiera (ROI, Cash Flow, Reformas).
    4.  **Generador de Informes:** Exportación de resultados a PDF.

---

### 2. Submódulo `utils/` (Lógica de Negocio)

Este paquete contiene funciones especializadas que son invocadas por la aplicación principal:

* **`loader.py` (Gestión de Recursos):**
    * Carga eficiente del modelo entrenado (`.pkl`) y el dataset (`.parquet`).
    * Implementa decoradores de caché (`@st.cache_resource`) para que la carga de datos pesados ocurra solo una vez, optimizando la velocidad de la app.

* **`features.py` (Ingeniería de Características en Inferencia):**
    * **Pipeline de Transformación:** Convierte los inputs del usuario (texto, números) en el formato exacto de matriz que espera el modelo GBR (One-Hot Encoding, escalado, etc.).
    * **Lógica de Negocio (Post-procesado):** Aplica correcciones manuales detectadas en la fase de análisis (ej: suavizado de precios para niveles de lujo extremos).

* **`gemini.py` (Integración IA Generativa):**
    * Wrapper para la API de **Google Generative AI**.
    * Envía prompts multimodales (Texto + Imagen) para evaluar el estado de conservación, luminosidad y estilo de la vivienda.
    * Gestiona el Chatbot asistente inmobiliario.

* **`market.py` (Análisis de Mercado):**
    * Algoritmo para encontrar **Testigos Comparables**: Filtra el dataset histórico para encontrar las viviendas más similares a la tasada (por zona, tamaño y precio) utilizando distancia euclídea o filtros directos.

* **`plots.py` (Visualización de Datos):**
    * Generación de gráficos interactivos con **Plotly**:
        * Medidores (Gauge Charts) para el precio estimado.
        * Mapas de dispersión geoespaciales (Mapbox) para ubicar la vivienda y sus testigos.
        * Gráficos de distribución de precios por zona.

* **`pdf_gen.py` (Reporting):**
    * Motor de generación de documentos con `FPDF`.
    * Maqueta dinámicamente un dossier que incluye: datos de la vivienda, precio estimado, análisis de la IA, gráficos financieros y listado de testigos.

* **`assistant.py`:**
    * Lógica específica para el asistente conversacional, gestionando el historial de chat y el contexto de la vivienda analizada.

* **`config.py`:**
    * Archivo de configuración global (rutas de archivos, diccionarios de mapeo de distritos, constantes de la aplicación).

## 📦 Dependencias Específicas

Para ejecutar este módulo, el entorno debe tener instaladas las librerías de interfaz y visualización:

* **Frontend:** `streamlit`.
* **Visualización:** `plotly`, `matplotlib`, `seaborn`.
* **Reportes:** `fpdf`.

* **IA:** `google-generativeai`.
* **Procesamiento:** `pandas`, `numpy`, `scikit-learn`, `gbr`.

## 🚀 Ejecución

Para lanzar la aplicación en un servidor local:

```bash
streamlit run app.py
```
La aplicación estará disponible en http://localhost:8501

**Autor:** Mario López Díaz