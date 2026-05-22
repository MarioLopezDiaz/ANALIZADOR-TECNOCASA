"""
Script de Web Scraping de Inmuebles en Tecnocasa

Este script utiliza Selenium para realizar web scraping en la página de Tecnocasa, específicamente en la sección de venta de inmuebles en la Comunidad de Madrid. El objetivo es extraer datos detallados sobre los anuncios de propiedades, incluyendo información como:

- Precio
- Dormitorios
- Superficie
- Baños
- Localización
- Descripción
- Imágenes de la propiedad
- Características adicionales como garaje, piscina, terraza, entre otras.

El script también descarga las imágenes asociadas a cada anuncio y las guarda localmente en una carpeta organizada por anuncio.

Requisitos:
- Selenium y ChromeDriver para la automatización del navegador.
- Requests para la descarga de imágenes.
- BeautifulSoup (si fuera necesario) para parseo adicional (no se usa aquí pero podría ser útil para futuras modificaciones).

El script guarda los datos obtenidos en un archivo Parquet con el nombre `tecnocasa_datos_sin_limpiar.csv` en la ubicación especificada.

Autor: Mario López Díaz
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException, StaleElementReferenceException
import pandas as pd
import re
from time import sleep
import os
import requests
from urllib.parse import urlparse

def descargar_imagen(url, carpeta, nombre_base):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            parsed_url = urlparse(url)
            extension = os.path.splitext(parsed_url.path)[-1]
            if not extension or extension.lower() not in ['.jpg', '.jpeg', '.png', '.webp']:
                extension = '.jpg'
            nombre_archivo = f"{nombre_base}{extension}"
            ruta = os.path.join(carpeta, nombre_archivo)
            with open(ruta, 'wb') as f:
                f.write(response.content)
            return ruta
    except Exception as e:
        print(f"Error al descargar imagen: {e}")
    return None


def tecnocasaWebScraping():
    base_url = 'https://www.tecnocasa.es/venta/inmuebles/comunidad-de-madrid/madrid.html/pag-{}'
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Ejecución en segundo plano
    options.add_argument('--disable-images')  # Acelera la carga
    driver = webdriver.Chrome(options=options)
    cont = 0
    data_list = []
    image_folder = "imagenes_tecnocasa"
    os.makedirs(image_folder, exist_ok=True)

    num_anuncios_deseados = 1660
    anuncios_por_pagina = 15
    num_paginas = (num_anuncios_deseados // anuncios_por_pagina) + 1 #111 paginas (04/06/2025)

    for page_num in range(1, 11):

        try:
            url = base_url.format(page_num)
            driver.get(url)
            print(f"\n🟢 Procesando página {page_num}...")
            driver.implicitly_wait(2)

            for i in range(15):
                try:
                    divs_hijos = driver.find_elements(By.CLASS_NAME, 'estate-card')
                    if i >= len(divs_hijos):
                        break

                    link = divs_hijos[i].find_element(By.TAG_NAME, 'a').get_attribute('href')
                    driver.get(link)
                    estate_info = {
                        'Enlace': link,
                        'Precio': "No disponible",
                        'Dormitorios': "No disponible",
                        'Superficie': "No disponible",
                        'Num_baños': "No disponible",
                        'Localización': "No disponible",
                        'Descripción': "No disponible",
                        'Metro': 0,
                        'Renfe': 0,
                        'Bus': 0,
                        'Farmacia': 0,
                        'Bar': 0,
                        'Restaurante': 0,
                        'Hospital': 0,
                        'Supermercado': 0,
                        'Tienda': 0,
                        'Colegio': 0,
                        'Imagenes': [],
                        'Vistas': "Desconocidas",
                        'Estado_conservacion': "Desconocido",
                        'Garaje': "Desconocido",
                        'Trastero': "Desconocido",
                        'Piscina': "Desconocido",
                        'Terraza_balcon': "Desconocido",
                        'Seguridad_portero': "Desconocido",
                        'Etiqueta': "Desconocida",
                        'Amueblado': "Desconocido",
                        'Calle_tranquila': False
                    }

                    # Imágenes
                    try:
                        estate_info['Imagenes'] = []

                        # 1. Buscar dentro del contenedor principal de imágenes
                        gallery = driver.find_element(By.CLASS_NAME, "estate-images")
                        image_elements = gallery.find_elements(By.TAG_NAME, "img")

                        for img in image_elements:
                            src = img.get_attribute("data-src") or img.get_attribute("src")
                            if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                                estate_info['Imagenes'].append(src)

                        # 2. Eliminar duplicados
                        estate_info['Imagenes'] = list(set(estate_info['Imagenes']))

                        # 3. Fallback: si no se encontraron imágenes
                        if not estate_info['Imagenes']:
                            try:
                                img_meta = driver.find_element(By.XPATH, "//meta[@property='og:image']")
                                estate_info['Imagenes'].append(img_meta.get_attribute('content'))
                            except NoSuchElementException:
                                print("No se encontraron imágenes en el anuncio")

                        # 4. Descargar todas las imágenes en carpeta individual por anuncio
                        carpeta_anuncio = os.path.join(image_folder, f"anuncio_{cont}")
                        os.makedirs(carpeta_anuncio, exist_ok=True)

                        estate_info['Imagenes_locales'] = []
                        for idx, url in enumerate(estate_info['Imagenes']):
                            nombre_base = f"{idx}"
                            ruta_local = descargar_imagen(url, carpeta_anuncio, nombre_base)
                            if ruta_local:
                                estate_info['Imagenes_locales'].append(ruta_local)


                    except Exception as e:
                        print(f"Error al extraer imágenes: {str(e)}")
                        estate_info['Imagenes'] = []
                        estate_info['Imagenes_locales'] = []

                    # Descripción y búsqueda semántica de características
                    try:
                        desc_element = driver.find_element(By.CLASS_NAME, 'estate-description-container')
                        descripcion = desc_element.text
                        estate_info['Descripción'] = descripcion

                        # --------------------
                        # Características extendidas
                        # --------------------
                        patrones_ext = {
                            'Vistas': r'\b(vistas (?:a|al|hacia)?[\w\s]+|con vistas(?: al| a| hacia)?[\w\s]+|panor[aá]micas|vistas despejadas|vistas al mar|mirador)\b',
                            'Estado_conservacion': r'\b(reformado|a reformar|reforma integral|necesita reformas|reformado recientemente|en buen estado|nuevo a estrenar)\b',
                            'Garaje': r'\b(garaje|plaza de garaje|parking|aparcamiento|estacionamiento)\b',
                            'Trastero': r'\b(trastero|cuarto de almacenamiento|almacén)\b',
                            'Piscina': r'\b(piscina|piscina comunitaria|piscina privada|zona de baño|pileta)\b',
                            'Terraza_balcon': r'\b(terraza|balc[oó]n|solarium|patio exterior|espacio al aire libre)\b',
                            'Seguridad_portero': r'\b(portero|seguridad|vigilancia|portero físico|conserje|control de acceso|cámara de seguridad|circuito cerrado)\b',
                            'Amueblado': r'\b(amueblado|con muebles|totalmente amueblado|equipado|mobiliario incluido)\b',
                            'Calle_tranquila': r'\b(calle tranquila|zona tranquila|zona silenciosa|poco transitada|sin ruido|entorno apacible|'
                                               r'ambiente relajado|sin tráfico|vecindario tranquilo|zona sin ruidos|zona apacible|'
                                               r'entorno silencioso|ubicación silenciosa|calle sin salida|zona alejada del ruido|'
                                               r'lugar sereno|entorno sin bullicio)\b'
                        }

                        # Vistas → extraer el fragmento si aplica
                        match_vistas = re.search(patrones_ext['Vistas'], descripcion, re.IGNORECASE)
                        if match_vistas:
                            estate_info['Vistas'] = match_vistas.group(0).strip()

                        # Estado de conservación → extraer si aplica
                        match_estado = re.search(patrones_ext['Estado_conservacion'], descripcion, re.IGNORECASE)
                        if match_estado:
                            estate_info['Estado_conservacion'] = match_estado.group(1).strip()

                        # Otras características binarias → marcar como "Sí" si se encuentra
                        for clave in ['Garaje', 'Trastero', 'Piscina', 'Terraza_balcon', 'Seguridad_portero',
                                      'Amueblado']:
                            if re.search(patrones_ext[clave], descripcion, re.IGNORECASE):
                                estate_info[clave] = "Sí"

                        # Calle tranquila como booleano
                        estate_info['Calle_tranquila'] = bool(
                            re.search(patrones_ext['Calle_tranquila'], descripcion, re.IGNORECASE))

                    except Exception as e:
                        print(f"Error procesando descripción: {e}")
                        pass

                    # Resto de datos
                    try:
                        estate_info['Precio'] = driver.find_element(By.CLASS_NAME, 'current-price').text
                    except: pass
                    try:
                        estate_info['Localización'] = driver.find_element(By.CLASS_NAME, 'estate-subtitle').text
                    except: pass
                    try:
                        estate_info['Dormitorios'] = driver.find_element(By.CLASS_NAME, 'estate-card-rooms').text
                    except: pass
                    try:
                        estate_info['Superficie'] = driver.find_element(By.CLASS_NAME, 'estate-card-surface').text
                    except: pass
                    try:
                        estate_info['Num_baños'] = driver.find_element(By.CLASS_NAME, 'estate-card-bathrooms').text
                    except: pass


                    features_element = driver.find_element(By.CLASS_NAME, 'estate-features')
                    rows = features_element.find_elements(By.CLASS_NAME, 'row')
                    for row in rows:
                        title_element = row.find_element(By.CLASS_NAME, 'estate-features-title')
                        value_element = row.find_element(By.CLASS_NAME, 'estate-features-value')
                        title = title_element.text.strip(':')
                        value = value_element.text.strip()

                        # Verifica el título y extrae la información específica
                        if title == 'Calefacción':
                            estate_info['Calefaccion'] = value
                        elif title == 'Jardín':
                            estate_info['Jardin'] = value
                        elif title == 'Tipo de inmueble':
                            estate_info['Tipo_de_inmueble'] = value
                        elif title == 'Año de construcción':
                            estate_info['Año_de_construccion'] = value
                        elif title == 'Planta':
                            estate_info['Planta'] = value
                        elif title == 'Aire acondicionado':
                            estate_info['Aire acondicionado'] = value
                        elif title == 'Ascensor':
                            estate_info['Ascensor'] = value

                    try:
                        energy_graph_element = driver.find_element(By.CLASS_NAME, 'energy-graph')
                        # Encuentra el elemento con la clase "square active" dentro del elemento "energy-graph"
                        active_square_element = energy_graph_element.find_element(By.CLASS_NAME, 'square.active')
                        # Extrae el texto del elemento encontrado
                        value = active_square_element.text
                        estate_info['Etiqueta'] = value
                    except StaleElementReferenceException:
                        print("El elemento energy_graph_element se volvió obsoleto. Volviendo a encontrar el elemento.")
                        energy_graph_element = driver.find_element(By.CLASS_NAME, 'energy-graph')
                        active_square_element = energy_graph_element.find_element(By.CLASS_NAME, 'square.active')
                        value = active_square_element.text
                        estate_info['Etiqueta'] = value
                    except NoSuchElementException:
                        pass


                    # Servicios cercanos
                    servicios = {
                        'pharmacy': 'Farmacia',
                        'school': 'Colegio',
                        'hospital': 'Hospital',
                        'market': 'Supermercado',
                        'shop': 'Tienda',
                        'bar': 'Bar',
                        'restaurant': 'Restaurante'
                    }

                    for clase_css, nombre_col in servicios.items():
                        try:
                            contenedor = driver.find_element(By.CSS_SELECTOR, f'.poi-category-data.{clase_css}')
                            filas = contenedor.find_elements(By.CLASS_NAME, 'row')
                            for fila in filas:
                                try:
                                    dist_elem = fila.find_element(By.CLASS_NAME, 'col-auto')
                                    # Forzamos lectura del texto usando JavaScript por si Selenium no lo ve
                                    dist_text = driver.execute_script("return arguments[0].textContent;",dist_elem).strip()
                                    if dist_text:
                                        distancia = float(dist_text.replace(",", ".").split()[0])
                                        if 'km' in dist_text.lower():
                                            distancia *= 1000
                                        if distancia < 1000:
                                            estate_info[nombre_col] = 1
                                            break
                                except Exception as inner_e:
                                    print(f"[ERROR interno] {nombre_col}: {inner_e}")
                                    continue
                        except: pass

                    # Transporte
                    try:
                        transportes = driver.find_element(By.CSS_SELECTOR, '.poi-category-data.public_transport')
                        rows = transportes.find_elements(By.CLASS_NAME, 'row')
                        for row in rows:
                            dist_text = row.find_element(By.CLASS_NAME, 'col-auto').text
                            icon = row.find_element(By.TAG_NAME, 'img').get_attribute('src')
                            dist = float(dist_text.replace(",", ".").split()[0])
                            if 'km' in dist_text:
                                dist *= 1000
                            if dist < 1000:
                                if 'subway' in icon:
                                    estate_info['Metro'] = 1
                                elif 'station' in icon:
                                    estate_info['Renfe'] = 1
                                elif 'bus_stop' in icon:
                                    estate_info['Bus'] = 1
                    except: pass


                    data_list.append(estate_info)
                    print(f"  🔹 Anuncio {cont} extraído: {link}")
                    cont += 1
                    driver.get(base_url.format(page_num))
                    sleep(1)

                except Exception as e:
                    print(f"Error en anuncio {i} página {page_num}: {e}")
                    driver.get(base_url.format(page_num))
                    sleep(1)

        except WebDriverException as e:
            print(f"WebDriverException: {e}. Reiniciando navegador.")
            driver.quit()
            driver = webdriver.Chrome()

    print("Proceso completado.")
    print(f"Total de anuncios extraídos: {len(data_list)}")
    driver.quit()
    df = pd.DataFrame(data_list)
    return df

# Uso
if __name__ == "__main__":
    df = tecnocasaWebScraping()
    df.to_parquet("../DATOS/tecnocasa_datos_sin_limpiar.parquet", index=False)