#!/usr/bin/env python3
"""
PASO 1: ÍNDICE RÁPIDO - Redpiso Madrid
======================================
Extrae datos básicos del listado y genera un Excel índice
para luego completar con detalles
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

MAX_PAGES = 237                # Número máximo de páginas a scrapear
DELAY_MIN_SECONDS = 2.0       # Tiempo mínimo entre peticiones (segundos)
DELAY_MAX_SECONDS = 24.5       # Tiempo máximo entre peticiones (segundos)

# ============================================================
# NO TOCAR A PARTIR DE AQUÍ
# ============================================================

BASE_URL = "https://www.redpiso.es"
START_URL = "https://www.redpiso.es/venta-viviendas/madrid/con-piso"

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
        print(f"   ⏱️  Esperando {delay:.1f}s...")
        time.sleep(delay)
        return BeautifulSoup(r.text, 'lxml')
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def parse_property(article):
    """Extrae datos básicos de un article"""
    data = {}
    
    # URL y TÍTULO
    link = article.find('a', class_='item-link')
    if not link:
        return None
    
    data['url'] = link['href']
    data['titulo'] = link.get_text(strip=True)
    data['referencia'] = link.get('data-id-property')
    
    # PRECIO
    h3 = article.find('h3')
    if h3:
        data['precio'] = h3.get_text(strip=True)
        num = re.sub(r'[^\d]', '', data['precio'])
        data['precio_num'] = int(num) if num else None
    else:
        return None
    
    # CARACTERÍSTICAS
    options = article.find_all('div', class_='property-list-options-item')
    
    for opt in options:
        text = opt.get_text(strip=True)
        
        # Superficie
        if 'm²' in text or 'm2' in text:
            m2 = re.search(r'(\d+)', text)
            data['superficie_m2'] = int(m2.group(1)) if m2 else None
        
        # Habitaciones
        elif 'hab' in text.lower():
            hab = re.search(r'(\d+)', text)
            data['habitaciones'] = int(hab.group(1)) if hab else None
        
        # Baños
        elif opt.find('i', class_='fa-bath'):
            bano = re.search(r'(\d+)', text)
            data['banos'] = int(bano.group(1)) if bano else None
    
    # ESTADO
    estado_div = article.find('div', class_='flag-reserved')
    if estado_div:
        data['estado'] = estado_div.get_text(strip=True).upper()
    else:
        data['estado'] = 'DISPONIBLE'
    
    # CALIFICACIÓN ENERGÉTICA
    energy = article.find('img', class_='property-list-energy')
    if energy:
        alt = energy.get('alt', '')
        cert = re.search(r'([a-g])$', alt, re.I)
        data['calificacion_energetica'] = cert.group(1).upper() if cert else None
    else:
        data['calificacion_energetica'] = None
    
    # TOUR VIRTUAL
    tour = article.find('img', class_='property-list-matterport')
    data['tour_virtual'] = bool(tour)
    
    # TELÉFONO
    tel_link = article.find('a', class_='office-phone')
    data['telefono'] = tel_link.get_text(strip=True) if tel_link else None
    
    # OFICINA
    oficina = article.find('a', class_='office-link')
    data['oficina'] = oficina.get_text(strip=True) if oficina else None
    
    # PRECIO/M²
    if data.get('precio_num') and data.get('superficie_m2') and data['superficie_m2'] > 0:
        data['precio_por_m2'] = round(data['precio_num'] / data['superficie_m2'], 2)
    else:
        data['precio_por_m2'] = None
    
    # Timestamp
    data['fecha_extraccion'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # MARCADORES PARA FASE 2
    data['datos_completos'] = False
    data['visitado_fecha'] = None
    
    return data

def scrape_redpiso_indice(max_pages=10):
    """Scraper de índice rápido"""
    propiedades = []
    current_url = START_URL
    page = 1
    
    print("=" * 70)
    print("📋 PASO 1: GENERANDO ÍNDICE RÁPIDO")
    print("=" * 70)
    print(f"Páginas máximas: {max_pages}")
    print(f"Delay entre peticiones: {DELAY_MIN_SECONDS}s - {DELAY_MAX_SECONDS}s")
    print(f"URL inicial: {current_url}")
    print()
    
    while page <= max_pages:
        print(f"\n→ Página {page}/{max_pages}")
        
        soup = get_soup(current_url)
        if not soup:
            break
        
        # Buscar articles
        articles = soup.find_all('article')
        print(f"   📄 {len(articles)} articles encontrados")
        
        if not articles:
            print("   ⚠️  No hay articles - fin de resultados")
            break
        
        # Extraer
        page_props = []
        seen = set()
        
        for art in articles:
            prop = parse_property(art)
            if prop and prop['url'] not in seen:
                seen.add(prop['url'])
                page_props.append(prop)
        
        print(f"   ✅ {len(page_props)} propiedades extraídas")
        
        if page_props:
            ejemplo = page_props[0]
            print(f"   📌 Ejemplo: {ejemplo['titulo'][:50]}... | {ejemplo['precio']} | {ejemplo['superficie_m2']}m²")
        
        propiedades.extend(page_props)
        
        # PAGINACIÓN
        page += 1
        next_part = f"/pagina-{page}"
        
        if '/pagina-' in current_url:
            current_url = current_url.rsplit('/pagina-', 1)[0] + next_part
        else:
            current_url = current_url.rstrip('/') + next_part
        
        if len(page_props) == 0:
            print("   ✓ No más datos")
            break
    
    # DataFrame
    df = pd.DataFrame(propiedades)
    if not df.empty:
        df = df.drop_duplicates(subset=['url'], keep='first')
    
    print(f"\n{'=' * 70}")
    print(f"✅ ÍNDICE COMPLETADO: {len(df)} propiedades únicas")
    print("=" * 70)
    
    return df

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print(f"\n⚙️  CONFIGURACIÓN ACTUAL:")
    print(f"   • Páginas máximas: {MAX_PAGES}")
    print(f"   • Delay mínimo: {DELAY_MIN_SECONDS}s")
    print(f"   • Delay máximo: {DELAY_MAX_SECONDS}s")
    print()
    
    # Confirmar
    input("Pulsa ENTER para continuar o CTRL+C para cancelar...")
    
    # Scrapear
    df = scrape_redpiso_indice(max_pages=MAX_PAGES)
    
    if not df.empty:
        # Guardar
        out_dir = '/localSpace/scrappers'
        os.makedirs(out_dir, exist_ok=True)
        
        # Nombre fijo para facilitar el paso 2
        excel_file = os.path.join(out_dir, 'indice_redpiso.xlsx')
        csv_file = os.path.join(out_dir, 'indice_redpiso.csv')
        
        df.to_excel(excel_file, index=False, engine='openpyxl')
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        
        print(f"\n📊 ARCHIVOS GUARDADOS:")
        print(f"   📄 Excel: {excel_file}")
        print(f"   📄 CSV: {csv_file}")
        
        # RESUMEN
        print(f"\n📊 RESUMEN ÍNDICE:")
        print(f"   Total propiedades: {len(df)}")
        print(f"   Precio medio: {df['precio_num'].mean():,.0f} €")
        print(f"   Superficie media: {df['superficie_m2'].mean():.1f} m²")
        print(f"   Con datos completos: {df['datos_completos'].sum()} (todas False por ahora)")
        
        print(f"\n✅ SIGUIENTE PASO:")
        print(f"   Ejecuta: python 2_extraer_detalles.py")
        print(f"   Esto completará los datos visitando cada URL")
    else:
        print("\n❌ No se extrajeron datos")
