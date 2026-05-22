"""
INTERFAZ DE VISIÓN ARTIFICIAL (GOOGLE GEMINI)
---------------------------------------------
Módulo que encapsula las peticiones a la API de Gemini Pro Vision. Recibe las
imágenes subidas por el usuario, construye el prompt sistémico (Ingeniería de Prompts)
y extrae en formato estructurado JSON las métricas intangibles del inmueble
(Nivel de Lujo, Estado de Conservación, Luminosidad, etc.).
"""

import streamlit as st
import json
import time
from PIL import Image

try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

def configurar_cliente(api_key):
    if not HAS_GENAI or not api_key: return None
    return genai.Client(api_key=api_key)

def analizar_imagen(image, api_key):
    client = configurar_cliente(api_key)
    if not client: return None # AIzaSyCWy79pZRxnxoHWdHl_iNLzBXWkruRZXGs
    
    modelos_candidatos = [
        'models/gemini-2.0-flash',
        'models/gemini-2.0-flash-exp',
        'models/gemini-2.5-flash',
        'models/gemini-flash-latest'
    ]

    prompt = """
    Eres un experto tasador inmobiliario. Analiza esta imagen.
    Responde ÚNICAMENTE con un JSON válido (sin markdown) con estos campos:
    {"nivel_lujo": (float 1.0-5.0), "estado": ("A reformar", "Bueno", "Muy bueno", "Reformado"), "modernidad": (float 1.0-5.0), "calidad_foto": (float 1.0-10.0), "luminosidad": (float 1.0-5.0)}
    """

    for nombre_modelo in modelos_candidatos:
        try:
            response = client.models.generate_content(model=nombre_modelo, contents=[prompt, image])
            txt = response.text
            if "```json" in txt: txt = txt.split("```json")[1].split("```")[0]
            elif "```" in txt: txt = txt.split("```")[1].split("```")[0]
            
            st.success(f"✅ Imagen analizada con IA ({nombre_modelo.replace('models/', '')})")
            return json.loads(txt.strip())
        except Exception as e:
            print(f"Error al procesar JSON de Gemini: {e}")
            continue
    
    st.error("No se pudo conectar con IA.")
    return None

def chat_inmobiliario(mensaje_usuario, contexto_datos, prediccion_actual, api_key):
    """
    Chat con capacidad de puntuación (Scoring) de ofertas.
    """
    client = configurar_cliente(api_key)
    if not client: return "Error: Falta API Key."

    # --- CAMBIO CLAVE: Prompt con reglas de puntuación ---
    system_prompt = f"""
    Eres el Asistente Experto de Tecnocasa Valuator.
    
    TUS DATOS:
    {contexto_datos}
    {prediccion_actual}
    
    TU MISIÓN:
    Analizar la consulta del usuario. Si menciona un precio de oferta (ej: "me lo venden por X"), debes calcular una "Puntuación de Oportunidad" (Deal Score) basada en nuestra tasación.
    
    REGLAS DE PUNTUACIÓN (0-10):
    - 10/10: Si el precio ofertado es un 30% MENOR que nuestra tasación (Chollazo).
    - 7-8/10: Si es ligeramente inferior a nuestra tasación (Buena compra).
    - 5/10: Si el precio es igual a la tasación (Precio Justo).
    - 3-4/10: Si es un poco más caro (10-20% sobreprecio).
    - 0-2/10: Si es mucho más caro (>30% sobreprecio).
    
    FORMATO DE RESPUESTA:
    1. Empieza con la puntuación grande: "⭐ **Puntuación de Oportunidad: X/10**"
    2. Da tu veredicto directo (Comprar, Negociar o Huir).
    3. Explica la diferencia en euros (Ahorro o Sobreprecio).
    4. Sé breve y profesional.
    """

    modelos_chat = ['gemini-2.5-flash', 'gemini-2.0-flash']

    for modelo in modelos_chat:
        try:
            response = client.models.generate_content(
                model=modelo,
                contents=[system_prompt, mensaje_usuario]
            )
            return response.text
        except Exception as e:
            if "429" in str(e):
                time.sleep(2)
                continue
            return f"Error de conexión ({modelo}): {str(e)}"
    
    return "⚠️ Sistema saturado. Inténtalo de nuevo en unos segundos."