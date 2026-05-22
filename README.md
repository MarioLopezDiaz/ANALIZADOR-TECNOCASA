# 🏡 Tecnocasa AI Valuator

![Python](https://img.shields.io/badge/Python-3.9%2B-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B) ![GBR](https://img.shields.io/badge/Model-GBR-orange) ![Gemini](https://img.shields.io/badge/AI-Gemini_Pro-8E75B2)

**Trabajo de Fin de Grado (TFG)** centrado en la valoración inmobiliaria inteligente. Este proyecto implementa un sistema *end-to-end* que combina **Machine Learning** (predicción de precios) e **Inteligencia Artificial Generativa** (análisis de imágenes y texto) para asistir en la toma de decisiones de inversión inmobiliaria.

## 🎯 Propósito del Proyecto

El objetivo es reducir la incertidumbre en el mercado inmobiliario mediante una herramienta analítica que permite:

1.  **Predecir el valor de mercado** de inmuebles utilizando modelos de regresión avanzados.

2.  **Analizar cualitativamente** las viviendas mediante visión artificial (Google Gemini) para puntuar nivel de lujo, estado y luminosidad.
3.  **Simular escenarios de inversión**, calculando rentabilidad, Cash Flow y ROI tras posibles reformas.
3.  **Detectar patrones ocultos** que influyen en el precio de los inmuebles.
4.  **Generar informes técnicos** automatizados en formato PDF.

## 🗂️ Estructura del Repositorio

El proyecto sigue el ciclo de vida del dato, organizado en módulos secuenciales:

```text
ANALIZADOR-TECNOCASA/
├── 1. ADQUISICION/
│   ├── REDPISO/
│   │   ├── 1_indice_rapido.py
│   │   └── 2_extraer_detalles.py
│   ├── 1.1_adquisicion.py     
│   └── 1.2_descarga_drive.py  
├── 2. PREPROCESADO Y LIMPIEZA/
│   ├── division100imagenes_tecnocasa/
│   ├── image_features/
│   ├── 2.1_limpieza.py
│   ├── 2.2_division_datoslimpios_100filas.ipynb       
│   ├── 2.3_imagenes_procesado.ipynb
│   ├── 2.4_enriquecimiento_redpiso.ipynb
│   ├── 2.4_enriquecimiento_TecnocasaRentaSeccion.ipynb
│   └── 2.4_enriquecimiento.ipynb
├── 3. ANALISIS EXPLORATORIO/
│   └── 3.1_analisis_exploratorio.ipynb
├── 4. MODELADO/
│   ├── 4.1_preparacion-Redpiso.ipynb
│   ├── 4.1_preparacion-Tecnocasa.ipynb
│   ├── 4.2_entrenamiento-RedPiso_Tecnocasa.ipynb
│   ├── 4.2_entrenamiento-Redpiso.ipynb
│   ├── 4.2_entrenamiento-Tecnocasa.ipynb 
│   ├── 4.3_entrenamientoDataAugmentation.ipynb
│   ├── 4.4_experimentos_entrenamiento.ipynb
│   ├── 4.5_entrenamiento_TecnocasaRentaSeccion.ipynb
│   ├── 4.5_preparacion_TecnocasaRentaSeccion.ipynb
│   ├── 4.6_enriquecimiento_colas.ipynb
│   └── 4.6_entrenamiento_colas.ipynb
├── 5. DESPLIEGUE/
│   ├── app.py 
│   └── utils/
│       ├── gemini.py
│       ├── features.py
│       ├── plots.py
│       ├── market.py 
│       └── pdf_gen.py 
└── DATOS/
```

## ⚙️ Instalación y Dependencias

### 1. Clonar el proyecto
```bash
git clone <URL_DEL_REPOSITORIO>
cd ANALIZADOR-TECNOCASA
```

### 2. Configurar entorno
Se recomienda usar Python 3.9+ y crear un entorno virtual:
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### 3. Instalar librerías
El proyecto requiere las dependencias listadas en requirements.txt:
```bash
pip install -r requirements.txt
```

## 🚀 Ejecución
Para iniciar el Dashboard Interactivo, navega a la carpeta de despliegue y ejecuta Streamlit:
```bash
cd "5. DESPLIEGUE"
streamlit run app.py
```
**Nota:** Al iniciar la aplicación, necesitarás introducir tu API Key de Google (Gemini) en la barra lateral para habilitar las funciones de visión artificial y el chat inteligente.

---
**Autor**: MARIO LÓPEZ DÍAZ  - Grado en Ingeniería de Datos e IA