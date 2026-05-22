# 🤖 Módulo de Modelado y Aprendizaje Automático

Este módulo contiene el núcleo predictivo del proyecto **Tecnocasa AI Valuator**. Aquí se lleva a cabo la definición, entrenamiento, optimización y selección de los modelos de Machine Learning encargados de estimar el precio de mercado de los inmuebles.

El flujo de trabajo incluye la preparación rigurosa de los datos, una comparativa exhaustiva entre diferentes familias de algoritmos (Lineales, Árboles, Redes Neuronales) y experimentos avanzados con generación de datos sintéticos.

## 📂 Archivos del Módulo

### Fase 1: Baseline y Validación Cruzada de Portales

### 1. `4.1_preparacion-Tecnocasa.ipynb`/ `4.1_preparacion-Redpiso.ipynb` (Split y Preprocesamiento)
**Propósito:** Establecer las bases para un entrenamiento robusto y reproducible, garantizando que no haya fuga de datos (*Data Leakage*).

**Funcionalidades Clave:**
* **Filtrado de Outliers:** Eliminación de valores extremos (cuantiles 2% y 98%) en el precio para evitar sesgos en el entrenamiento.

* **Transformación del Target:** Conversión del precio a `Log(Precio/m²)` para estabilizar la varianza y mejorar la convergencia de los modelos.
* **División Estratificada:** Split Train/Test (80/20) estratificado por rangos de precio, asegurando que ambos conjuntos tengan la misma distribución económica.
* **Pipeline de Preprocesamiento:** Definición de `ColumnTransformer` para:
    * Imputación de nulos restantes.
    * Codificación de variables categóricas (`OneHotEncoder`).
    * Escalado de variables numéricas (`StandardScaler`) para modelos sensibles (Lineales y NN).

---

### 2. `4.2_entrenamiento-Tecnocasa.ipynb` (Selección de Modelos y Optuna)
**Propósito:** Entrenar, optimizar y comparar múltiples arquitecturas para encontrar el "Modelo Champion".

**Modelos Evaluados:**
1.  **Modelos Lineales:** Regresión Lineal, Lasso, Ridge, ElasticNet (Base de referencia).

2.  **Ensembles de Árboles:** Random Forest, Gradient Boosting, **XGBoost**.
3.  **Deep Learning:** Red Neuronal (MLP) con Keras/TensorFlow.

**Metodología:**
* **Optimización Bayesiana:** Uso de `Optuna` para la búsqueda eficiente de hiperparámetros (learning rate, depth, n_estimators, dropout, etc.).
* **Validación Cruzada:** 5-Fold Cross-Validation para estimar el error de generalización.

* **Métrica de Decisión:** MAE (Mean Absolute Error) en Euros reales (tras invertir la transformación logarítmica).
* **Resultado:** Selección de **XGBoost** como el modelo ganador por su capacidad para capturar no-linealidades y su robustez frente al ruido.

* **`4.2_entrenamiento- (Redpiso, Fusión)`:** Optimización Bayesiana (Optuna) de 8 arquitecturas (Lineales, XGBoost, RF, Redes Neuronales Keras). Demostración del "techo de cristal": Redpiso, incluso con GIS avanzado, obtiene un error >7.000 € superior a Tecnocasa por carecer de la Visión Artificial de Gemini.

---

### Fase 2: Manipulación del Volumen de Datos

### 3. `4.3_entrenamientoDataAugmentation.ipynb` (Experimentación)
**Propósito:** Investigar si el aumento de datos mediante generación sintética mejora el rendimiento de los modelos, especialmente las Redes Neuronales.

**Experimento:**
* **Generación Sintética:** Creación de "gemelos digitales" de los inmuebles variando ligeramente su superficie y características, manteniendo la coherencia del precio/m².

* **Protocolo Riguroso:** Aplicación del aumento **SOLO en el conjunto de Train** después del split, manteniendo el Test "virgen" para una evaluación honesta.
* **Conclusiones del TFG:** Se demostró que, para este dataset tabular específico, la calidad del dato real supera a la cantidad sintética. Los modelos de árboles (XGBoost) con datos originales superaron a los modelos entrenados con datos aumentados, los cuales introdujeron ruido en los extremos de la distribución.

### Fase 3: Estudio de Ablación y Corrección Espacial
* **`4.4_experimentos_entrenamiento.ipynb`:** 
    1. **Estudio de Ablación:** Comparativa de arquitecturas SMALL (tradicional), MEDIUM y LARGE (IA Completa), probando matemáticamente que la inyección de Visión Artificial reduce drásticamente el MAE.
  2. **Modelo Híbrido:** Desarrollo de la clase customizada `HybridValuator` que entrena un XGBoost base y corrige el sesgo local en las colas mediante la evaluación de residuales con *K-Nearest Neighbors (KNN)*.

### Fase 4: Granularidad Espacial Extrema
* **`4.5_preparacion/entrenamiento_TecnocasaRentaSeccion.ipynb`:** Experimento probando la Renta Neta Media por Sección Censal. Demuestra el efecto de la "maldición de la dimensionalidad" y el exceso de varianza frente a la robustez macroeconómica de la Renta por Distrito.

### Fase 5: Enriquecimiento de Colas (El Experimento Definitivo)
* **`4.6_enriquecimiento_colas.ipynb` / `4.6_entrenamiento_colas.ipynb`:** *Stratified Data Augmentation* inyectando pisos de Redpiso en los deciles de precio extremos. Para solventar la falta de IA en Redpiso, se utiliza un `KNNImputer` que "hereda" las variables visuales de los gemelos matemáticos de Tecnocasa (evitando *Data Leakage* al ocultar el target).

## 📊 Resumen de Resultados

| Familia de Modelos | Algoritmo | MAE Test (Aprox) | Comportamiento |
| :--- | :--- | :--- | :--- |
| **Árboles (Boosting)** | **GBR** | **~37.000 €** | **Óptimo. Mejor balance Sesgo-Varianza.** |
| Árboles (Bagging) | Random Forest | ~42.000 € | Bueno, pero tiende a sobreajustar. |
| Lineales | Ridge / Lasso | ~39.000 € | Underfitting (No captan la complejidad). |
| Deep Learning | Red Neuronal | >70.000 € | Overfitting severo por falta de datos masivos. |

## 📦 Dependencias Específicas

Este módulo requiere un entorno de ML completo:

* **Frameworks:** `scikit-learn`, `GBR`, `tensorflow` (Keras).
* **Optimización:** `optuna`.

* **Métricas:** `sklearn.metrics` (mean_absolute_error).
* **Utilidades:** `joblib` (para guardar los modelos `.pkl`), `pandas`, `numpy`.

---
**Autor:** Mario López Díaz