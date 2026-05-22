"""
CONTROLADOR DEL ASISTENTE VIRTUAL INMOBILIARIO
----------------------------------------------
Módulo encargado de gestionar la lógica conversacional del dashboard.
Mantiene el contexto de los mensajes del usuario e interactúa con la API 
de Google Gemini para proporcionar asesoramiento dinámico basado en las 
tasaciones calculadas y los datos del mercado.
"""

import pandas as pd

def generar_contexto_mercado(df, zona):
    """Genera un resumen textual de los datos reales para alimentar a la IA."""
    if zona not in df['Localizacion_Clave'].values:
        return "No hay datos suficientes de esta zona."
        
    df_zona = df[df['Localizacion_Clave'] == zona]
    
    stats = {
        'precio_m2_medio': df_zona['Precio'].sum() / df_zona['Superficie'].sum(),
        'stock': len(df_zona),
        'lujo_promedio': df_zona['nivel_lujo'].mean(),
        'renta_zona': df_zona['Renta_Neta_Media'].mean()
    }
    
    contexto = f"""
    - Zona analizada: {zona}
    - Precio medio real del m²: {stats['precio_m2_medio']:.0f} €/m²
    - Nivel de stock analizado: {stats['stock']} viviendas
    - Nivel de lujo promedio en la zona: {stats['lujo_promedio']:.1f}/5
    - Renta Neta Media de los vecinos: {stats['renta_zona']:.3f} k€
    """
    return contexto

def formatear_prediccion_actual(user_inputs, precio_estimado):
    """Resume qué está viendo el usuario en el dashboard."""
    return f"""
    El usuario está analizando una vivienda en {user_inputs['zona']} de {user_inputs['superficie']}m².
    Nuestro modelo de Machine Learning la ha tasado en: {precio_estimado:,.0f} €.
    Calidad visual detectada: Lujo {user_inputs['nivel_lujo']}/5.
    """