"""
Script de descarga y descompresión de archivos desde Google Drive

Este script automatiza la descarga de archivos (como .csv, .zip o .tar) desde Google Drive usando sus IDs,
y los guarda en directorios específicos definidos en un archivo de configuración (`archivos_raw.txt`).
Además, descomprime automáticamente los archivos ZIP o TAR descargados en las carpetas de destino.

Requisitos:
- El archivo `archivos_raw.txt` debe estar en BASE_DIR y contener líneas con el siguiente formato:
  <ID de Google Drive>,<nombre del archivo>,<directorio destino relativo>

Nota: Este script usa `requests`, `zipfile`, `tarfile` y `pathlib`, y no maneja confirmaciones de Google Drive
para archivos grandes o protegidos. Para esos casos, se recomienda usar `gdown`.

Autor: Mario López Díaz
"""


from pathlib import Path
import os
import requests
import zipfile

BASE_DIR = Path("../ANALIZADOR-TECNOCASA/DATOS")


def descargar_archivo_directo(id_archivo, directorio_destino, archivo_destino):
    url = f"https://drive.google.com/uc?export=download&id={id_archivo}"
    respuesta = requests.get(url, allow_redirects=True)

    if respuesta.status_code != 200:
        raise Exception(f"❌ Error al descargar el archivo con ID {id_archivo}")

    os.makedirs(directorio_destino, exist_ok=True)
    ruta_completa = os.path.join(directorio_destino, archivo_destino)

    with open(ruta_completa, 'wb') as archivo:
        archivo.write(respuesta.content)

    return archivo_destino, ruta_completa


def procesar_archivo_info(ruta_archivo_info):
    archivos_info = []
    with open(ruta_archivo_info, 'r') as archivo:
        for linea in archivo:
            id_archivo, nombre_archivo, directorio_destino = linea.strip().split(',')
            archivos_info.append((id_archivo, nombre_archivo, directorio_destino))
    return archivos_info


def descomprimir_zip(ruta_zip, destino):
    with zipfile.ZipFile(ruta_zip, 'r') as zip_ref:
        zip_ref.extractall(destino)
    print(f"📂 Carpeta descomprimida en: {destino}")


import tarfile

def descomprimir_tar(ruta_tar, destino):
    with tarfile.open(ruta_tar, "r:") as tar:
        tar.extractall(path=destino)
    print(f"📂 Carpeta descomprimida en: {destino}")


def main(nombre_archivo_info='archivos_raw.txt'):
    ruta_archivo_info = BASE_DIR / nombre_archivo_info
    archivos_a_descargar = procesar_archivo_info(ruta_archivo_info)

    for id_archivo, nombre_archivo, directorio_relativo in archivos_a_descargar:
        directorio_destino = BASE_DIR / directorio_relativo
        nombre_archivo_descargado, ruta_archivo_guardado = descargar_archivo_directo(
            id_archivo,
            directorio_destino,
            nombre_archivo
        )
        print(f"✅ Archivo '{nombre_archivo_descargado}' guardado en: {ruta_archivo_guardado}")

        if nombre_archivo.endswith(".zip"):
            carpeta_destino = directorio_destino / nombre_archivo.replace('.zip', '')
            descomprimir_zip(ruta_archivo_guardado, carpeta_destino)

        # Descomprimir si es TAR
        elif nombre_archivo.endswith(".tar"):
            carpeta_destino = directorio_destino / nombre_archivo.replace('.tar', '')
            descomprimir_tar(ruta_archivo_guardado, carpeta_destino)


if __name__ == "__main__":
    main()
