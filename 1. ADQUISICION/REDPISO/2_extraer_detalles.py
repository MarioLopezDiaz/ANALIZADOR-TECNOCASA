#!/usr/bin/env python3
"""
PASO 2: EXTRACCIÓN DETALLADA - Redpiso Madrid
=============================================
Lee el índice generado en el Paso 1 y visita cada URL
para extraer TODOS los datos detallados
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re
from datetime import datetime
import os

# ============================================================
# CONFIGURACIÓN - AJUSTA AQUÍ LOS TIEMPOS
# ============================================================

DELAY_MIN_SECONDS = 3.0       # Tiempo mínimo entre peticiones (más alto que paso 1)
DELAY_MAX_SECONDS = 36.0       # Tiempo máximo entre peticiones
GUARDAR_CADA_N = 10           # Guardar Excel cada N propiedades procesadas

# ============================================================
# NO TOCAR A PARTIR DE AQUÍ
# ============================================================

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9",
}

def get_soup(url):
    """Obtiene HTML con delay configurable"""
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        delay = random.uniform(DELAY_MIN_SECONDS, DELAY_MAX_SECONDS)
        print(f"      ⏱️  Delay: {delay:.1f}s", end='')
        time.sleep(delay)
        return BeautifulSoup(r.text, 'lxml')
    except Exception as e:
        print(f" ❌ Error: {e}")
        return None

def extraer_detalles_ficha(url):
    """
    Extrae TODOS los detalles de una ficha individual
    Basado en la estructura que enviaste
    """
    soup = get_soup(url)
    if not soup:
        return None
    
    detalles = {}
    
    # Buscar sección de características
    # <div class="col-lg-3 col-md-4 col-sm-6 property-features-item">
    items = soup.find_all('div', class_='property-features-item')
    
    for item in items:
        texto = item.get_text(strip=True)
        
        # Metros útiles
        if 'Metros útiles:' in texto:
            m = re.search(r'(\d+)\s*m²', texto)
            detalles['metros_utiles'] = int(m.group(1)) if m else None
        
        # Garajes
        elif 'Garajes:' in texto:
            g = re.search(r'(\d+)', texto)
            detalles['garajes'] = int(g.group(1)) if g else None
        
        # Estado detallado
        elif 'Estado:' in texto:
            estado = texto.replace('Estado:', '').strip()
            detalles['estado_detallado'] = estado
        
        # Orientación
        elif 'Orientación:' in texto:
            orientacion = texto.replace('Orientación:', '').strip()
            detalles['orientacion'] = orientacion
        
        # Aire acondicionado
        elif 'Aire acondicionado' in texto:
            detalles['aire_acondicionado'] = True
        
        # Agua caliente
        elif 'Agua caliente:' in texto:
            agua = texto.replace('Agua caliente:', '').strip()
            detalles['agua_caliente'] = agua
        
        # Calefacción
        elif 'Calefacción:' in texto:
            calef = texto.replace('Calefacción:', '').strip()
            detalles['calefaccion'] = calef
        
        # Tipo de suelo
        elif 'Tipo de suelo:' in texto:
            suelo = texto.replace('Tipo de suelo:', '').strip()
            detalles['tipo_suelo'] = suelo
        
        # Tipo de fachada
        elif 'Tipo de fachada:' in texto:
            fachada = texto.replace('Tipo de fachada:', '').strip()
            detalles['tipo_fachada'] = fachada
        
        # Antigüedad
        elif 'Antigüedad:' in texto:
            antig = texto.replace('Antigüedad:', '').strip()
            detalles['antiguedad'] = antig
        
        # Año de construcción
        elif 'Año de construcción:' in texto:
            anio = re.search(r'(\d{4})', texto)
            detalles['anio_construccion'] = int(anio.group(1)) if anio else None
        
        # Número de terrazas
        elif 'Número de terrazas:' in texto:
            terr = re.search(r'(\d+)', texto)
            detalles['numero_terrazas'] = int(terr.group(1)) if terr else None
        
        # Planta
        elif 'Planta:' in texto:
            planta = texto.replace('Planta:', '').strip()
            detalles['planta'] = planta
        
        # Ascensor
        elif 'Ascensor' in texto and ':' not in texto:
            detalles['ascensor'] = True
        
        # Parking/Plaza de garaje
        elif 'Plaza de garaje' in texto or 'Parking' in texto:
            detalles['parking'] = True
        
        # Trastero
        elif 'Trastero' in texto and ':' not in texto:
            detalles['trastero'] = True
        
        # Terraza (si no está en número)
        elif 'Terraza' in texto and 'Número' not in texto and ':' not in texto:
            detalles['tiene_terraza'] = True
        
        # Balcón
        elif 'Balcón' in texto:
            detalles['balcon'] = True
        
        # Jardín
        elif 'Jardín' in texto:
            detalles['jardin'] = True
        
        # Piscina
        elif 'Piscina' in texto:
            detalles['piscina'] = True
        
        # Amueblado
        elif 'Amueblado' in texto:
            detalles['amueblado'] = True
        
        # Cocina equipada
        elif 'Cocina equipada' in texto:
            detalles['cocina_equipada'] = True
    
    # Valores por defecto para campos booleanos
    detalles.setdefault('aire_acondicionado', False)
    detalles.setdefault('ascensor', False)
    detalles.setdefault('parking', False)
    detalles.setdefault('trastero', False)
    detalles.setdefault('tiene_terraza', False)
    detalles.setdefault('balcon', False)
    detalles.setdefault('jardin', False)
    detalles.setdefault('piscina', False)
    detalles.setdefault('amueblado', False)
    detalles.setdefault('cocina_equipada', False)
    
    return detalles

def procesar_indice(excel_path):
    """
    Lee el índice y completa datos faltantes
    """
    print("=" * 70)
    print("🔍 PASO 2: EXTRACCIÓN DETALLADA")
    print("=" * 70)
    
    # Leer Excel
    if not os.path.exists(excel_path):
        print(f"❌ No se encontró el archivo: {excel_path}")
        print(f"   Ejecuta primero: python 1_indice_rapido.py")
        return
    
    df = pd.read_excel(excel_path)
    print(f"✅ Índice cargado: {len(df)} propiedades")
    
    # Filtrar las que NO tienen datos completos
    pendientes = df[df['datos_completos'] == False]
    print(f"📋 Propiedades pendientes: {len(pendientes)}")
    
    if len(pendientes) == 0:
        print("✅ ¡Todas las propiedades ya tienen datos completos!")
        return
    
    print(f"\n⚙️  CONFIGURACIÓN:")
    print(f"   • Delay: {DELAY_MIN_SECONDS}s - {DELAY_MAX_SECONDS}s")
    print(f"   • Guardar cada: {GUARDAR_CADA_N} propiedades")
    print()
    
    input("Pulsa ENTER para iniciar o CTRL+C para cancelar...")
    
    # Procesar
    procesadas = 0
    errores = 0
    
    for idx, row in pendientes.iterrows():
        procesadas += 1
        print(f"\n[{procesadas}/{len(pendientes)}] {row['referencia']}")
        print(f"   URL: {row['url'][:60]}...")
        
        # Extraer detalles
        detalles = extraer_detalles_ficha(row['url'])
        
        if detalles:
            # Actualizar DataFrame
            for key, value in detalles.items():
                df.at[idx, key] = value
            
            df.at[idx, 'datos_completos'] = True
            df.at[idx, 'visitado_fecha'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            print(f" ✅ OK")
            
            # Mostrar algunos datos extraídos
            if detalles.get('metros_utiles'):
                print(f"      • Metros útiles: {detalles['metros_utiles']} m²")
            if detalles.get('orientacion'):
                print(f"      • Orientación: {detalles['orientacion']}")
            if detalles.get('anio_construccion'):
                print(f"      • Año: {detalles['anio_construccion']}")
        else:
            errores += 1
            print(f" ⚠️  Error al extraer")
        
        # Guardar cada N propiedades
        if procesadas % GUARDAR_CADA_N == 0:
            df.to_excel(excel_path, index=False, engine='openpyxl')
            print(f"\n💾 Guardado automático ({procesadas} procesadas)")
    
    # Guardar final
    df.to_excel(excel_path, index=False, engine='openpyxl')
    
    # También guardar versión con timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    backup_path = excel_path.replace('.xlsx', f'_completo_{timestamp}.xlsx')
    df.to_excel(backup_path, index=False, engine='openpyxl')
    
    print(f"\n{'=' * 70}")
    print(f"✅ PROCESO COMPLETADO")
    print("=" * 70)
    print(f"   Procesadas: {procesadas}")
    print(f"   Errores: {errores}")
    print(f"   Éxito: {procesadas - errores}")
    print(f"\n📊 ARCHIVOS:")
    print(f"   • Principal: {excel_path}")
    print(f"   • Backup: {backup_path}")
    
    # Estadísticas
    completas = df[df['datos_completos'] == True]
    print(f"\n📈 ESTADO FINAL:")
    print(f"   Con datos completos: {len(completas)}/{len(df)}")
    
    if len(completas) > 0:
        print(f"\n📋 CAMPOS ADICIONALES EXTRAÍDOS:")
        campos_nuevos = ['metros_utiles', 'garajes', 'orientacion', 'aire_acondicionado',
                        'agua_caliente', 'calefaccion', 'tipo_suelo', 'tipo_fachada',
                        'antiguedad', 'anio_construccion', 'numero_terrazas']
        
        for campo in campos_nuevos:
            if campo in df.columns:
                no_nulos = df[campo].notna().sum()
                print(f"   • {campo}: {no_nulos} propiedades")

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    excel_path = '/localSpace/scrappers/indice_redpiso.xlsx'
    procesar_indice(excel_path)
