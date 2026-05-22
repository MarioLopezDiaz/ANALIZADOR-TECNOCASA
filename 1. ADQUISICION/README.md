# 🕸️ Módulo de Adquisición de Datos

Este módulo es el punto de entrada del proyecto **Tecnocasa AI Valuator**. Su función principal es la ingesta de datos, encargándose tanto de la extracción automatizada de información inmobiliaria desde la web (Web Scraping) como de la gestión y descarga de recursos externos alojados en la nube. En iteraciones avanzadas del proyecto, se ha ampliado para capturar datos de un segundo portal (Redpiso) con fines de validación cruzada y enriquecimiento.

## 📂 Archivos del Módulo

### 1. Carpeta `REDPISO/` (Nuevo Origen de Datos)
**Propósito:** Scripts dedicados a la extracción de un dataset alternativo para validar la necesidad de la Inteligencia Artificial y enriquecer las colas del modelo.
* **`1_indice_rapido.py`**: Araña web encargada de barrer la paginación del portal Redpiso para recopilar las URLs y metadatos básicos de todos los inmuebles disponibles.
* **`2_extraer_detalles.py`**: Scraper profundo que visita cada URL obtenida para extraer las características estructurales, eficiencia energética y descripciones detalladas.

### 2. `1.1_adquisicion.py` (Web Scraper)
**Propósito:** Automatizar la extracción masiva de anuncios de venta de inmuebles en la Comunidad de Madrid desde el portal de Tecnocasa.

**Funcionalidades Clave:**
* **Scraping Dinámico:** Utiliza `Selenium` para navegar por la paginación y acceder al detalle de cada URL.

* **Extracción de Atributos:** Captura datos estructurados (precio, m², habitaciones) y semi-estructurados (servicios cercanos, etiqueta energética).
* **Procesamiento de Texto (NLP Básico):** Implementa expresiones regulares (`Regex`) para analizar la descripción del anuncio y detectar características binarias (ej: "Terraza", "A reformar", "Portero").
* **Descarga de Imágenes:** Gestiona la descarga automática de las fotografías de cada inmueble, organizándolas en carpetas locales.
* **Persistencia:** Guarda los datos en formato eficiente Parquet (`tecnocasa_datos_sin_limpiar.parquet`).

**Uso:**
```bash
python 1.1_adquisicion.py
```
### 2. `1.2_descarga_drive.py` (Gestor de Recursos)
Propósito: Automatizar la descarga y descompresión de datasets o lotes de imágenes alojados en Google Drive, facilitando la replicabilidad del entorno de datos.

**Funcionalidades Clave:**

* **Lectura de Manifiesto:** Lee un archivo de configuración (`archivos_raw.txt`) que especifica ID, nombre y ruta de destino.

* **Descarga Directa:** Gestiona la conexión con Google Drive mediante `requests`.

* **Descompresión Inteligente:** Detecta automáticamente archivos `.zip` o `.tar` y los extrae en el directorio correspondiente tras la descarga.

**Uso:** Requiere el archivo `archivos_raw.txt` en el directorio base.
```bash
python 1.2_descarga_drive.py
```

## 📦 Dependencias Específicas
Este módulo depende de las siguientes librerías (incluidas en el `requirements.txt` global):

* **Selenium:** Automatización del navegador web.

* **Requests:** Peticiones HTTP para descarga de archivos e imágenes.

* **Pandas:** Estructuración de los datos extraídos.

* **Pathlib / OS / Zipfile / Tarfile:** Gestión del sistema de archivos.
---
**Autor**: Mario López Díaz