"""
CONFIGURACIÓN GLOBAL Y CONSTANTES
---------------------------------
Almacena de forma centralizada las rutas de directorios, credenciales (API Keys),
parámetros del modelo (ej. columnas esperadas por el pipeline) y variables 
de entorno críticas para el funcionamiento de la aplicación en despliegue.
"""

import streamlit as st
import os
import warnings

def setup_page():
    # Silenciar ruido
    os.environ["GRPC_VERBOSITY"] = "ERROR"
    os.environ["GLOG_minloglevel"] = "2"
    warnings.filterwarnings("ignore")

    st.set_page_config(
        page_title="Tecnocasa AI Valuator",
        page_icon="🏠",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown("""
        <style>
        .main {background-color: #f8f9fa;}
        .stButton>button {
            width: 100%;
            background-color: #2c3e50;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            height: 3em;
        }
        .metric-card {
            background-color: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }
        .stFileUploader {padding-bottom: 20px;}
        </style>
        """, unsafe_allow_html=True)