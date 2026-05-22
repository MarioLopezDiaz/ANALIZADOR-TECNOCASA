"""
GESTOR DE CARGA DE MODELOS Y DATOS (CACHING)
--------------------------------------------
Optimiza el rendimiento de la aplicación mediante el uso de `st.cache_data` y 
`st.cache_resource`. Se encarga de la deserialización segura (vía joblib) del 
modelo XGBoost y los pipelines de preprocesamiento, evitando cargas redundantes.
"""

import streamlit as st
import pandas as pd
import joblib

@st.cache_resource
def load_resources():
    try:
        # Cargar Pipeline
        try: pipeline = joblib.load('../DATOS/pipeline_final_gbr.pkl')
        except: 
            try: pipeline = joblib.load('../DATOS/pipeline_final_xgb.pkl')
            except: pipeline = joblib.load('../DATOS/pipeline_final_rf.pkl')
            
        model_cols = joblib.load('../DATOS/features_columns.pkl')
        
        # Limpieza
        for bad_col in ['Precio', 'Precio_m2_Real', 'Log_Precio', 'Precio_m2']:
            if bad_col in model_cols: model_cols.remove(bad_col)
        
        # Datos
        try: df_ref = pd.read_parquet("../DATOS/tecnocasa_modelo_AUMENTADO.parquet", engine='fastparquet')
        except: df_ref = pd.read_parquet("tecnocasa_modelo.parquet", engine='fastparquet')
        
        options = {
            'zonas': sorted(df_ref['Localizacion_Clave'].dropna().astype(str).unique().tolist()),
            'tipos_inmueble': sorted(df_ref['Tipo_de_inmueble'].dropna().astype(str).unique().tolist()),
            'suelos': sorted(df_ref['tipo_suelo'].dropna().astype(str).unique().tolist()),
            'ventanas': sorted(df_ref['tipo_ventana'].dropna().astype(str).unique().tolist()),
            'calefaccion': sorted(df_ref['Calefaccion'].dropna().astype(str).unique().tolist()),
            'paredes': sorted(df_ref['material_pared'].dropna().astype(str).unique().tolist()),
            'estilos': sorted(df_ref['estilo_principal'].dropna().astype(str).unique().tolist())
        }
        
        renta_map = df_ref.groupby('Localizacion_Clave')['Renta_Neta_Media'].mean().to_dict()
        
        return pipeline, model_cols, options, renta_map, df_ref
        
    except Exception as e:
        st.error(f"Error cargando recursos: {e}")
        st.stop()