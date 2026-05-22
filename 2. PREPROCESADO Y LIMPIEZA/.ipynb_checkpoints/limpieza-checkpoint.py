import os
import shutil
import numpy as np
import pandas as pd
import re
from time import sleep
from geopy.geocoders import Nominatim
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.experimental import enable_iterative_imputer  # Habilita IterativeImputer
from sklearn.impute import IterativeImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from textblob import TextBlob


# ---------------------
# TRANSFORMACIONES BÁSICAS
# ---------------------

def string_to_int(x):
    if pd.notnull(x):
        x_split = x.split()
        return int(x_split[0])
    return np.nan


def obtener_tipo_casa(x):
    """ Recibe un enlace como el siguiente "https://www.tecnocasa.es/venta/piso/madrid/madrid/523991.html" y devuelve
    que tipo de vivienda es, en este caso /piso/"""
    return x.split("/")[4]


def string_to_price(x):
    """Transforma precios tipo '250.000 €' en enteros."""
    if isinstance(x, str):
        return pd.to_numeric(x.split()[0].replace(".", ""), errors='coerce')
    return np.nan


def limpiar_superficie(x):
    """Extrae m2 desde texto tipo '125 m²'."""
    if pd.notnull(x):
        match = re.search(r'(\d+)', str(x))
        return int(match.group(1)) if match else np.nan
    return np.nan


def limpiar_estado(x):
    """Normaliza estado del inmueble."""
    if pd.isnull(x): return np.nan
    x = x.lower()
    if "nuevo" in x:
        return "Nuevo"
    elif "reformado" in x:
        return "Reformado"
    elif "buen estado" in x:
        return "Buen estado"
    elif "a reformar" in x:
        return "A reformar"
    return "Desconocido"


def limpiar_vistas(x):
    return np.nan if str(x).lower() == "desconocidas" else x.strip().lower()


def limpiar_estado_conservacion(x):
    if pd.isnull(x) or str(x).lower() == "desconocido":
        return np.nan
    return limpiar_estado(x)


def limpiar_columna_dormitorios_banos(columna):
    return columna.apply(lambda x: extraer_numero_dormitorios_baños(str(x), r'(\d+)'))


def calcular_precio_m2(df, columna_precio='Precio', columna_superficie='Superficie'):
    """Agrega columna de precio por metro cuadrado."""
    df["Precio_m2"] = df[columna_precio] / df[columna_superficie]
    df["Precio_m2"] = df["Precio_m2"].replace([np.inf, -np.inf], np.nan)
    return df


def convertir_planta_ordinal(valor):
    if pd.isna(valor) or valor == 'Desconocido':
        return -1  # Desconocido
    valor = str(valor).lower()

    if "ático" in valor or "atico" in valor:
        return 4
    if "alta" in valor:
        return 3
    if "media" in valor:
        return 2
    if "baja" in valor or "bajo" in valor:
        return 1
    if "sótano" in valor or "sotano" in valor:
        return 0

    # Intentar extraer un número si lo hay
    try:
        num = int(''.join(filter(str.isdigit, valor)))
        return num
    except:
        return -1


# ---------------------
# DICOTÓMICAS
# ---------------------

def string_to_dicotomic(x):
    return 1 if pd.notnull(x) else 0


def transformar_en_dicotomicas(datos):
    """Convierte columnas indicadas a formato dicotómico (1 = presente, 0 = ausente o desconocido)."""

    # Columnas donde la presencia de texto implica valor 1
    columnas_texto_presente = ["Calefaccion", "Ascensor", "Aire acondicionado", "Jardin", "Vistas"]

    # Columnas con "Sí"/"Desconocido"
    columnas_si_desconocido = ["Garaje", "Piscina", "Terraza_balcon", "Trastero", "Seguridad_portero", "Amueblado"]

    # Procesar columnas con presencia textual
    for columna in columnas_texto_presente:
        if columna == "Vistas":
            datos[columna] = datos[columna].apply(
                lambda x: 0 if pd.isnull(x) or str(x).lower() == "desconocidas" else 1)
        else:
            datos[columna] = datos[columna].replace("No disponible", np.nan)
            datos[columna] = datos[columna].apply(string_to_dicotomic)

    # Procesar columnas "Sí"/"Desconocido"
    for columna in columnas_si_desconocido:
        datos[columna] = datos[columna].apply(lambda x: 1 if str(x).strip().lower() == "sí" else 0)

    datos['Calle_tranquila'] = datos['Calle_tranquila'].astype(int)

    return datos


# ---------------------
# NORMALIZACIÓN SERVICIOS Y COMERCIOS
# ---------------------

SERVICIOS_VALIDOS = {'Colegios', 'Hospitales', 'Parques/Zonas verdes'}
COMERCIOS_VALIDOS = {'Supermercados', 'Tiendas', 'Restaurantes'}


def limpiar_lista_categorias(lista, categorias_validas):
    if isinstance(lista, list):
        limpia = sorted(set([x.strip().title() for x in lista if x.strip().title() in categorias_validas]))
        return limpia if limpia else None
    return None


# ---------------------
# ANÁLISIS DESCRIPCIÓN
# ---------------------

def buscar_palabra(texto, palabra):
    if pd.notnull(texto):
        texto = texto.lower()
        palabra = palabra.lower()
        return bool(re.search(r'\b' + re.escape(palabra) + r'(?=\s|\W|$)', texto))
    return False


def extraer_numero_dormitorios_baños(texto, exp_regular):
    if pd.notnull(texto):
        resultado = re.search(exp_regular, texto, re.IGNORECASE)
        if resultado:
            numero = resultado.group(1)
            if numero.isdigit():
                return int(numero)
            else:
                numeros_texto = {"un": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4,
                                 "cinco": 5, "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10}
                return numeros_texto.get(numero.lower(), None)
    return None


def extraer_anio_construccion(texto, exp_regular=r'\b(19|20)\d{2}\b'):
    if pd.notnull(texto):
        resultado = re.search(exp_regular, texto, re.IGNORECASE)
        return resultado.group(0) if resultado else None
    return None


def detectar_lenguaje_urgente(texto):
    if pd.isnull(texto):
        return 0
    patrones_urgencia = [
        r"(oportunidad única|no lo dejes escapar|última oportunidad|ideal para|llama ya)",
        r"(promoción especial|ocasión irrepetible|reserva ya)"
    ]
    return any(re.search(pat, texto.lower()) for pat in patrones_urgencia)


def contar_adjetivos(texto):
    if pd.isnull(texto):
        return 0
    adjetivos_positivos = ["luminoso", "moderno", "reformado", "amplio", "exclusivo", "tranquilo", "céntrico"]
    count = sum(1 for adj in adjetivos_positivos if adj in texto.lower())
    return count


def analizar_sentimiento(texto):
    if pd.isnull(texto):
        return 0.0, 0.0
    blob = TextBlob(texto)
    return blob.sentiment.polarity, blob.sentiment.subjectivity


def analizar_longitud_y_riqueza(texto):
    if pd.isnull(texto):
        return 0, 0
    palabras = texto.split()
    num_palabras = len(palabras)
    num_unicas = len(set(palabras))
    return num_palabras, num_unicas


def analizar_descripcion(texto):
    ascensor = buscar_palabra(texto, "ascensor")
    num_habitaciones = extraer_numero_dormitorios_baños(texto,
                                                        r'(\d+|un(o|a)?|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez)\s+(dormitorio|habitación)es?')
    num_baños = extraer_numero_dormitorios_baños(texto,
                                                 r'(\d+|un(o|a)?|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez)\s+bañ(o|os)')
    anio = extraer_anio_construccion(texto)

    longitud, riqueza = analizar_longitud_y_riqueza(texto)
    polaridad, subjetividad = analizar_sentimiento(texto)
    adj_positivos = contar_adjetivos(texto)
    urgencia = detectar_lenguaje_urgente(texto)

    return {
        "Longitud_desc": longitud,
        "Riqueza_desc": riqueza,
        "Polaridad_desc": polaridad,
        "Subjetividad_desc": subjetividad,
        "Adjetivos_positivos": adj_positivos,
        "Urgencia_desc": int(urgencia)
    }


# ---------------------
# LOCALIZACIÓN Y GEODATOS
# ---------------------


def get_coords(lugar):
    geolocator = Nominatim(user_agent="Usuario")
    location = geolocator.geocode(str(lugar))
    sleep(2)
    if location:
        return pd.Series({"Latitud": location.latitude, "Longitud": location.longitude})
    return pd.Series({"Latitud": np.nan, "Longitud": np.nan})


def get_coords_cached(lista_lugares, cache_coords):
    geolocator = Nominatim(user_agent="Usuario")
    nuevas_coords = {}

    for lugar in lista_lugares:
        if pd.isnull(lugar) or lugar in cache_coords:
            continue
        try:
            location = geolocator.geocode(str(lugar))
            sleep(1)  # Para evitar bloqueo de Nominatim
            if location:
                nuevas_coords[lugar] = (location.latitude, location.longitude)
            else:
                nuevas_coords[lugar] = (np.nan, np.nan)
        except Exception as e:
            nuevas_coords[lugar] = (np.nan, np.nan)

    return nuevas_coords


def asignar_coords(df, col_localizacion, cache_coords):
    df["Latitud"] = df[col_localizacion].map(lambda x: cache_coords.get(x, (np.nan, np.nan))[0])
    df["Longitud"] = df[col_localizacion].map(lambda x: cache_coords.get(x, (np.nan, np.nan))[1])
    return df


def guardar_coords_csv(cache_coords, ruta_csv):
    df_coords = pd.DataFrame.from_dict(cache_coords, orient='index', columns=['Latitud', 'Longitud'])
    df_coords.index.name = 'Localizacion'
    df_coords.reset_index(inplace=True)
    df_coords.to_csv(ruta_csv, index=False)


def cargar_coords_csv(ruta_csv):
    try:
        df_coords = pd.read_csv(ruta_csv)
        return dict(zip(df_coords['Localizacion'], zip(df_coords['Latitud'], df_coords['Longitud'])))
    except FileNotFoundError:
        return {}


def get_distrito(localizacion, nom_localizaciones):
    for distrito in nom_localizaciones:
        if buscar_palabra(str(localizacion), distrito):
            return distrito
    return None


def analizar_localizacion_descripcion(texto, localizaciones):
    if pd.notnull(texto):
        texto = str(texto).lower()
        regex = r'\b(?:' + '|'.join(localizaciones) + r')\b'
        match = re.search(regex, texto, re.IGNORECASE)
        return match.group() if match else None
    return None


def normalizar_columna_localizacion(x):
    return x.strip().title() if isinstance(x, str) else x


def filtrar_fuera_comunidad_madrid(df, lat_min=39.7, lat_max=41.3, lon_min=-4.6, lon_max=-3.0):
    # Filtra filas que tienen latitud y longitud dentro del rango
    mask = (
            (df["Latitud"] >= lat_min) &
            (df["Latitud"] <= lat_max) &
            (df["Longitud"] >= lon_min) &
            (df["Longitud"] <= lon_max)
    )
    df_filtrado = df[mask].reset_index(drop=True)
    return df_filtrado


# ---------------------
# CARGA DE LOCALIZACIONES
# ---------------------

def leer_distritos_barrios(url):
    df = pd.read_csv(url, encoding='utf-8', sep=";")
    return [s.strip() for s in df["distrito_nombre"].unique()], [s.strip() for s in df["barrio_nombre"].unique()]


def leer_municipios(url):
    df = pd.read_csv(url, encoding='utf-8', sep=";")
    return [s.strip() for s in df["municipio_nombre"].unique()]


def arreglar_localizaciones(loc):
    adicionales = [
        "El Molar", "El Álamo", "Rio", "Montecarmelo", "Arroyo Del Fresno",
        "Salvador", "Virgen del Cortijo", "San Cristóbal", "Moscardo",
        "Pilar", "Fuencarral", "Puerta Del Ángel", "Peñagrande",
        "Las Rozas De Madrid", "Los Santos De La Humosa", "Centro", "Madrid"
    ]
    base = [l for l in loc if l not in ["Centro", "Madrid"]]
    return np.unique(base + adicionales)


def transformar_localizacion(df, urls):
    nom_distritos, nom_barrios = leer_distritos_barrios(urls[0])
    nom_municipios = leer_municipios(urls[1])
    localizaciones = arreglar_localizaciones(nom_distritos + nom_barrios + nom_municipios)
    df["distrito/ciudad"] = df["Localización"].apply(lambda x: get_distrito(x, localizaciones))
    return df, localizaciones


# ---------------------
# IMPUTAR VALORES
# ---------------------

def imputar_valores_rf(datos_viviendas, columnas_objetivo):
    """
    Imputa valores NaN utilizando un RandomForest en un IterativeImputer.

    Parámetros:
    - datos_viviendas: DataFrame con los datos
    - columnas_objetivo: lista de columnas a imputar

    Retorna:
    - DataFrame imputado
    """
    # Filtrar solo las columnas relevantes para imputación
    columnas_utiles = columnas_objetivo + ['Precio', 'Superficie']
    df = datos_viviendas[columnas_utiles].copy()

    # Convertir a float para imputación (necesario para IterativeImputer)
    df = df.astype(float)

    # Configurar el imputador
    imputador = IterativeImputer(estimator=RandomForestRegressor(n_estimators=20, random_state=42),
                                 max_iter=10, random_state=0)

    # Ajustar e imputar
    df_imputado = imputador.fit_transform(df)

    # Convertir de nuevo a DataFrame
    df_imputado = pd.DataFrame(df_imputado, columns=df.columns)

    # Redondear los campos que deberían ser enteros
    if 'Dormitorios' in df_imputado.columns:
        df_imputado['Dormitorios'] = df_imputado['Dormitorios'].round().astype(int)
    if 'Num_baños' in df_imputado.columns:
        df_imputado['Num_baños'] = df_imputado['Num_baños'].round().astype(int)
    if 'Año_de_construccion' in df_imputado.columns:
        df_imputado['Año_de_construccion'] = df_imputado['Año_de_construccion'].round().astype(int)

    # Sustituir columnas originales en el DataFrame principal
    for col in columnas_objetivo:
        datos_viviendas[col] = df_imputado[col]

    return datos_viviendas


# ---------------------
# LIMPIEZA CARPETAS
# ---------------------

import stat


def obtener_anuncios_validos(df):
    return set(df["announcement_id"].dropna().astype(int))


def extraer_id_anuncio(lista_rutas):
    if isinstance(lista_rutas, str):
        lista_rutas = eval(lista_rutas)
    for ruta in lista_rutas:
        partes = ruta.replace("\\", "/").split("/")
        for p in partes:
            if p.startswith("anuncio_"):
                try:
                    return int(p.split("_")[1])
                except:
                    pass
    return None


def mover_carpetas_no_validas(carpeta_base, carpeta_respaldo, anuncios_validos):
    os.makedirs(carpeta_respaldo, exist_ok=True)
    for nombre_carpeta in os.listdir(carpeta_base):
        if nombre_carpeta.startswith("anuncio_"):
            try:
                num = int(nombre_carpeta.split("_")[1])
                if num not in anuncios_validos:
                    ruta_completa = os.path.join(carpeta_base, nombre_carpeta)
                    if os.path.exists(ruta_completa):
                        destino = os.path.join(carpeta_respaldo, nombre_carpeta)
                        shutil.move(ruta_completa, destino)
                        print(f"📦 Carpeta movida a: {destino}")
            except Exception as e:
                print(f"❌ Error con carpeta {nombre_carpeta}: {e}")


# ---------------------
# LIMPIEZA
# ---------------------

def limpiar_datos_tecnocasa(ruta_csv, urls_localizacion):
    """Carga, limpia y transforma los datos desde Parquet."""

    # Cargar datos
    df = pd.read_parquet(ruta_csv, engine='fastparquet')

    # Conversión básica de columnas
    df["Precio"] = df["Precio"].apply(string_to_price)
    df["Dormitorios"] = limpiar_columna_dormitorios_banos(df["Dormitorios"])
    df["Num_baños"] = limpiar_columna_dormitorios_banos(df["Num_baños"])
    df["Superficie"] = df["Superficie"].apply(limpiar_superficie)
    df["Estado_conservacion"] = df["Estado_conservacion"].apply(limpiar_estado_conservacion)
    df["Vistas"] = df["Vistas"].apply(limpiar_vistas)
    df["Tipo_vivienda"] = df["Enlace"].apply(obtener_tipo_casa)
    df['Planta_ordinal'] = df['Planta'].apply(convertir_planta_ordinal)

    # Dicótomicas
    df = transformar_en_dicotomicas(df)

    # Localización
    df, localizaciones = transformar_localizacion(df, urls_localizacion)
    df["Localización_normalizada"] = df["Localización"].apply(normalizar_columna_localizacion)

    # Filtrar el DataFrame
    viviendas_validas = ["casa", "piso", "atico"]
    df = df[df["Tipo_vivienda"].isin(viviendas_validas)].reset_index(drop=True)

    # Obtener coordenadas si no existen CSVs
    if not os.path.exists(rutas_coords_csv[0]):
        print("Generando coordenadas por distrito/ciudad...")
        dataframe_cord = df["distrito/ciudad"].apply(get_coords)
        dataframe_cord.to_csv(rutas_coords_csv[0], index=False)
    else:
        dataframe_cord = pd.read_csv(rutas_coords_csv[0], usecols=lambda col: col != "Unnamed: 0")

    if not os.path.exists(rutas_coords_csv[1]):
        print("Generando coordenadas por localización...")
        cordenadas_aux = df["Localización"].apply(get_coords)
        cordenadas_aux.to_csv(rutas_coords_csv[1], index=False)
    else:
        cordenadas_aux = pd.read_csv(rutas_coords_csv[1], usecols=lambda col: col != "Unnamed: 0")

    # Asignar coordenadas
    df = pd.concat([df.reset_index(drop=True), dataframe_cord], axis=1)
    df["Latitud"] = df["Latitud"].fillna(cordenadas_aux["Latitud"])
    df["Longitud"] = df["Longitud"].fillna(cordenadas_aux["Longitud"])

    df["announcement_id"] = df["Imagenes_locales"].apply(extraer_id_anuncio)

    df = filtrar_fuera_comunidad_madrid(df).reset_index(drop=True)

    # Obtener lista final de anuncios válidos tras todos los filtros
    anuncios_validos = set(df["announcement_id"].dropna().astype(int))

    # Mover carpetas que no estén en el conjunto válido
    carpeta_base = "C:/Users/mario/imagenes_tecnocasa"
    carpeta_respaldo = "C:/Users/mario/imagenes_descartadas"
    mover_carpetas_no_validas(carpeta_base, carpeta_respaldo, anuncios_validos)

    # Precio por m2
    df = calcular_precio_m2(df)

    df_descrip = df["Descripción"].apply(analizar_descripcion).apply(pd.Series)
    df = pd.concat([df, df_descrip], axis=1)

    # IMPUTACIÓN DE DATOS FALTANTES
    columnas_a_imputar = ['Dormitorios', 'Num_baños', 'Año_de_construccion']
    df = imputar_valores_rf(df, columnas_a_imputar)

    df.drop(["Localización"], axis=1, inplace=True)

    campos_categoricos = ['Estado_conservacion', 'Planta', 'Etiqueta', 'Amueblado']

    for campo in campos_categoricos:
        df[campo] = df[campo].fillna('Desconocido')

    def imputar_planta(row):
        if row['Planta_ordinal'] != -1:
            return row['Planta_ordinal']
        else:
            return moda_por_localizacion.get(row['Localización_normalizada'],
                                             df[df['Planta_ordinal'] != -1]['Planta_ordinal'].mode().iloc[0])

    moda_por_localizacion = (
        df[df['Planta_ordinal'] != -1]
        .groupby('Localización_normalizada')['Planta_ordinal']
        .agg(lambda x: x.mode().iloc[0] if not x.mode().empty else -1)
    )

    df['Planta_ordinal'] = df.apply(imputar_planta, axis=1)

    if 'Planta' in df.columns:
        df.drop(columns=['Planta'], inplace=True)

    return df


if __name__ == "__main__":
    ruta_datos = "C:/Users/mario/OneDrive/Mario/CARRERA/TFG/ANALIZADOR-TECNOCASA/DATOS/tecnocasa_datos_sin_limpiar.parquet"
    urls_localizacion = [
        "C:/Users/mario/OneDrive/Mario/CARRERA/TFG/ANALIZADOR-TECNOCASA/DATOS/distrito_barrios.parquet", #son csv
        "C:/Users/mario/OneDrive/Mario/CARRERA/TFG/ANALIZADOR-TECNOCASA/DATOS/municipios.parquet"
    ]
    rutas_coords_csv = [
        "C:/Users/mario/OneDrive/Mario/CARRERA/TFG/ANALIZADOR-TECNOCASA/DATOS/coords_distrito.csv", #si son nuevos datos hay que borrar estos archivos
        "C:/Users/mario/OneDrive/Mario/CARRERA/TFG/ANALIZADOR-TECNOCASA/DATOS/coords_localizacion.csv"
    ]

    df_limpio = limpiar_datos_tecnocasa(ruta_datos, urls_localizacion)

    # Guardar resultado
    df_limpio.to_parquet("C:/Users/mario/OneDrive/Mario/CARRERA/TFG/ANALIZADOR-TECNOCASA/DATOS/tecnocasa_datos_limpios.parquet", index=False)
