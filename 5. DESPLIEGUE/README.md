# 🚀 TRABAJO FIN DE GRADO: "Análisis inteligente del mercado inmobiliario mediante técnicas de web scraping y aprendizaje automático"

Este módulo materializa todo el trabajo de análisis y modelado en una herramienta funcional e interactiva: el **Tecnocasa AI Dashboard**. 

Se trata de una aplicación web construida con **Streamlit** que permite a usuarios finales (inversores, agentes inmobiliarios o particulares) interactuar con los modelos predictivos en tiempo real, realizar análisis de visión artificial y generar informes profesionales.

> 📦 **Repositorio completo del TFG** (notebooks, datos, modelos y aplicación):
> [https://github.com/MarioLopezDiaz/ANALIZADOR-TECNOCASA](https://github.com/MarioLopezDiaz/ANALIZADOR-TECNOCASA.git)

## 📂 Arquitectura del Módulo

El despliegue sigue una arquitectura modular donde `app.py` actúa como orquestador (Frontend) y la carpeta `utils/` contiene la lógica de negocio (Backend).

```
tecnocasa-ai-valuator/
├── app.py                        # Punto de entrada (UI principal)
├── requirements.txt              # Dependencias del proyecto
├── pipeline_final_gbr.pkl        # Modelo GBR serializado
├── features_columns.pkl          # Columnas esperadas por el pipeline
├── tecnocasa_modelo.parquet      # Dataset histórico de referencia
├── gemini_api_key.txt            # API Key lista para el tribunal
├── imagenes/                     # Carpeta con imágenes de inmueble (IA)
└── utils/
    ├── config.py                 # Configuración global y estilos
    ├── loader.py                 # Carga cacheada de modelos y datos
    ├── features.py               # Ingeniería de características en inferencia
    ├── gemini.py                 # Integración con Google Gemini (visión + chat)
    ├── market.py                 # Testigos comparables y copywriting IA
    ├── plots.py                  # Gráficos interactivos (Plotly)
    ├── pdf_gen.py                # Generación de informes PDF
    └── assistant.py              # Lógica del asistente conversacional
```

### 1. `app.py` (Punto de Entrada)
**Propósito:** Script principal que renderiza la interfaz de usuario y gestiona el flujo de la aplicación.
**Funcionalidades:**
* **Gestión de Sesión:** Manejo de variables de estado (`st.session_state`) para persistir datos entre recargas (ej: datos de la vivienda, API Key).
* **Navegación:** Estructura de pestañas para separar funcionalidades:
    1.  **Tasadora:** Formulario de entrada de datos y predicción de precio (GBR).
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

- **Python** 3.10 o superior
- **pip** actualizado
- Archivos del modelo entrenado en el directorio raíz:
  - `pipeline_final_gbr.pkl` (o `pipeline_final_xgb.pkl` / `pipeline_final_rf.pkl`)
  - `features_columns.pkl`
  - `tecnocasa_modelo.parquet`

- **API Key de Google Gemini** (gratuita en [aistudio.google.com](https://aistudio.google.com))


* **Frontend:** `streamlit`.
* **Visualización:** `plotly`, `matplotlib`, `seaborn`.
* **Reportes:** `fpdf`.

* **IA:** `google-generativeai`.
* **Procesamiento:** `pandas`, `numpy`, `scikit-learn`, `gbr`.


## 🚀 Instalación y Ejecución

### 1. Acceder al repositorio

```bash
cd tecnocasa-ai-valuator
```

### 2. Crear el entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Lanzar la aplicación

```bash
streamlit run app.py
```

La aplicación arrancará y se abrirá automáticamente en el navegador en:

```
http://localhost:8501
```

## 🔑 Configuración de la API Key de Gemini

Para obtener una clave gratuita:
1. Ve a [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Crea una clave de API y cópiala en el campo correspondiente del sidebar.
 
> **Estos recursos están listos para usar directamente. No requieren ninguna configuración adicional.**
 
### API Key de Google Gemini (lista para usar)
 
La clave necesaria para activar el análisis visual con IA y el asistente conversacional está disponible en el archivo `gemini_api_key.txt` de la raíz del repositorio.
 
```
AIzaSyCtp7Io1iBQokvqMlGI21RseIfW5TUJ1BQ
```
 
**Cómo introducirla:**
1. Arranca la aplicación (`streamlit run app.py`)
2. En el **panel lateral izquierdo**, localiza el campo `🔑 Gemini API Key`
3. Pega la clave y pulsa Enter — queda activa para toda la sesión
> Cuota gratuita: **15 peticiones/min · 1.000.000 tokens/min** (Gemini 2.5 Flash). Más que suficiente para la evaluación.


## 🛠️ Solución de Problemas Comunes

| Error | Causa probable | Solución |
|---|---|---|
| `ModuleNotFoundError: fastparquet` | Motor de parquet no instalado | `pip install fastparquet` |
| `FileNotFoundError: pipeline_final_gbr.pkl` | Falta el modelo entrenado | Asegúrate de que los archivos `.pkl` están en el directorio raíz |
| `Error de conexión con Gemini` | API Key inválida o cuota agotada | Verifica la clave en [aistudio.google.com](https://aistudio.google.com) |
| `streamlit: command not found` | Entorno virtual no activado | Ejecuta `source venv/bin/activate` (Linux/Mac) o `venv\Scripts\activate` (Windows) |


## ✍️ Autor

**Mario López Díaz** - Grado en Ingeniería de Datos e Inteligencia Artificial
