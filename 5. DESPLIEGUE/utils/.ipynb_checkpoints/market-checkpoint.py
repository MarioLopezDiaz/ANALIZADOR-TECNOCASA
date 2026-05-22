"""
SIMULADOR FINANCIERO Y DE ESCENARIOS DE INVERSIÓN
-------------------------------------------------
Contiene la lógica de negocio económico del TFG. Calcula métricas clave para
inversores inmobiliarios como el Retorno de Inversión (ROI), el Cash Flow,
la rentabilidad bruta (Cap Rate) y proyecta el valor post-reforma del inmueble.
"""

import pandas as pd
import streamlit as st
import numpy as np

def encontrar_testigos(df_ref, inputs):
    """
    Algoritmo KNN simplificado para encontrar viviendas similares en el histórico.
    """
    # 1. Filtrar por la misma zona (Condición obligatoria)
    df_zona = df_ref[df_ref['Localizacion_Clave'] == inputs['zona']].copy()
    
    if len(df_zona) < 5:
        return None # No hay suficientes datos
    
    # 2. Calcular "Distancia" (Similitud)
    # Penalizamos la diferencia de superficie y habitaciones
    df_zona['diff_superficie'] = abs(df_zona['Superficie'] - inputs['superficie'])
    df_zona['diff_habs'] = abs(df_zona['Dormitorios'] - inputs['dormitorios'])
    
    # Score de similitud (cuanto menor, más parecido)
    # Damos más peso a la superficie
    df_zona['similarity_score'] = (df_zona['diff_superficie'] * 2) + (df_zona['diff_habs'] * 10)
    
    # 3. Seleccionar los 5 mejores (los que tengan menor score)
    testigos = df_zona.sort_values('similarity_score').head(5)
    
    return testigos[['Superficie', 'Dormitorios', 'Num_baños', 'Precio', 'Localizacion_Clave']]

def generar_copy_anuncio(client, inputs, precio_estimado):
    """
    Usa Gemini para redactar un anuncio de venta persuasivo.
    """
    prompt = f"""
    Actúa como un experto en Copywriting Inmobiliario y Neuromarketing.
    Redacta un anuncio de venta atractivo para un portal inmobiliario (Idealista) basado en estos datos:
    
    - Zona: {inputs['zona']} (Renta media: {inputs['renta_interna']})
    - Características: {inputs['superficie']}m², {inputs['dormitorios']} habs, {inputs['banos']} baños.
    - Extras: Ascensor: {inputs['ascensor']}, Terraza: {inputs['terraza']}.
    - Estado Visual (IA): Nivel de Lujo {inputs['nivel_lujo']}/5, Luminosidad {inputs['calidad_iluminacion']}/5.
    - Precio Sugerido: {precio_estimado:,.0f}€
    
    OBJETIVO:
    Genera 2 opciones breves:
    1. Opción EMOCIONAL (Para familias/parejas): Enfócate en el hogar, la luz, la zona. Usa emojis.
    2. Opción INVERSOR (Para rentabilidad): Enfócate en el precio, la zona y el potencial de alquiler.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        return f"Error generando copy: {e}"