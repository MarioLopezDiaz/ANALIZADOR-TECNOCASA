"""
MOTOR DE INGENIERÍA DE CARACTERÍSTICAS (INFERENCIA)
---------------------------------------------------
Alinea los datos crudos introducidos por el usuario en la aplicación web con
las expectativas matemáticas del modelo entrenado. Ejecuta transformaciones
al vuelo, cálculos de ratios (Dormitorios/m²) y conversiones logarítmicas necesarias.
"""

import pandas as pd
from datetime import datetime

def preparar_dataframe(u, feature_columns):
    """Convierte el diccionario de inputs (u) en un DataFrame."""
    
    # Cálculos derivados
    dorm_m2 = u['dormitorios'] / u['superficie'] if u['superficie'] > 0 else 0
    banos_m2 = u['banos'] / u['superficie'] if u['superficie'] > 0 else 0
    edad = datetime.now().year - u['anio']
    
    servicios_total = (1 if u['metro'] else 0) + (1 if u['renfe'] else 0) + \
                      u['n_farm'] + u['n_bar'] + u['n_rest'] + u['n_hosp'] + u['n_super'] + u['n_tienda']
    
    superficie_x_lujo = u['superficie'] * u['nivel_lujo']
    recien_reformado = 1 if u['estado_val'] == 4 else 0

    # Diccionario alineado
    input_dict = {
        'Superficie': u['superficie'], 'Dormitorios': u['dormitorios'], 'Num_baños': u['banos'],
        'Año_de_construccion': u['anio'], 'Planta_ordinal': u['planta'],
        'Localizacion_Clave': u['zona'], 'Renta_Neta_Media': u['renta_interna'], 
        
        'Dormitorios_por_m2': dorm_m2, 'Banos_por_m2': banos_m2,
        'Edad_inmueble': edad, 'Servicios_cercanos': servicios_total,
        'Superficie_x_Lujo': superficie_x_lujo, 'Recien_reformado': recien_reformado,
        
        'Metro': 1 if u['metro'] else 0, 'Renfe': 1 if u['renfe'] else 0,
        'Farmacia': u['n_farm'], 'Bar': u['n_bar'], 'Restaurante': u['n_rest'], 
        'Hospital': u['n_hosp'], 'Supermercado': u['n_super'], 'Tienda': u['n_tienda'],
        
        'Garaje': 1 if u['garaje'] else 0, 'Trastero': 1 if u['trastero'] else 0,
        'Piscina': 1 if u['piscina'] else 0, 'Terraza_balcon': 1 if u['terraza'] else 0,
        'Seguridad_portero': 1 if u['portero'] else 0, 'Amueblado': 1 if u['amueblado'] else 0,
        'Aire acondicionado': 1 if u['aire'] else 0, 'Ascensor': 1 if u['ascensor'] else 0,
        'Vistas': 1 if u['vistas'] else 0,
        
        'Estado_conservacion': u['estado_val'], 'Tipo_de_inmueble': u['tipo_inmueble'],
        'Tipo_vivienda': u['tipo_inmueble'], 'Calefaccion': u['calefaccion'],
        'tipo_suelo': u['suelo'], 'tipo_ventana': u['ventana'], 'material_pared': u['pared'],
        'estilo_principal': u['estilo'], 'Etiqueta': 'Desconocida',
        
        'nivel_lujo': u['nivel_lujo'], 'nivel_modernidad': u['nivel_modernidad'],
        'calidad_iluminacion': u['calidad_iluminacion'], 'espacio_abierto': u['espacio_abierto'],
        'distribucion_espacios': u['distribucion'], 'nivel_foto_profesional': u['nivel_foto'],
        'equilibrio_composicion': u['equilibrio'], 'num_imagenes': u['num_imgs'],
        'calidad_bano': u['calidad_bano'], 'equipamiento_cocina': u['equip_cocina'],
        
        'distorsion_perspectiva': 0.0, 'color_diversidad': 0.5, 'color_principal': '#FFFFFF',
        'espacios_almacenaje': 3.0, 'Calle_tranquila': 1 if u['ruido_urb'] < 40 else 0,
        
        'ruido_carretera': u['ruido_traf'], 'dist_a_carretera': 100,
        'ruido_ferrocarril': 0, 'dist_a_ferrocarril': 1000,
        'ruido_urbano': u['ruido_urb'], 'dist_a_aglomeracion': 500,
        'ruido_aeropuerto': 0, 'Longitud_desc': u['long_desc'],
        'Subjetividad_desc': 0.5, 'Adjetivos_positivos': u['adj_pos'], 'Urgencia_desc': u['urgencia']
    }
    
    df = pd.DataFrame([input_dict])
    missing = set(feature_columns) - set(df.columns)
    for c in missing: df[c] = 0
    return df[feature_columns]