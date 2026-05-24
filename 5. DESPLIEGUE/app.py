"""
PUNTO DE ENTRADA DEL DASHBOARD (STREAMLIT APP)
----------------------------------------------
Script principal que orquesta la Interfaz de Usuario (UI) del Tecnocasa AI Valuator.
Gestiona el estado de la sesión, la navegación entre las distintas herramientas
(Tasador IA, Chatbot, Simulador de Inversión) y coordina la ejecución de los
modelos de Machine Learning subyacentes.
"""

import streamlit as st
import numpy as np
from PIL import Image

# Importamos módulos
from utils import config, loader, gemini, features, plots, assistant, pdf_gen, market

# 1. Configuración
config.setup_page()
pipeline, feature_columns, options, renta_map, df_ref = loader.load_resources()

# 2. Sidebar
with st.sidebar:
    st.title("Panel Principal")
    
    # API KEY (Necesaria para Gemini)
    api_key = st.text_input("🔑 Gemini API Key", type="password", help="Pega aquí tu clave API para usar la visión artificial.")
    
    st.markdown("### 📍 Ubicación")
    zona = st.selectbox("Barrio / Zona", options['zonas'])
    
    # --- CAMBIO: Renta Neta OCULTA al usuario ---
    # Recuperamos el valor internamente para usarlo luego en el cálculo
    renta_interna = float(renta_map.get(zona, 35.0))
    # No mostramos ningún st.number_input para la renta
    
    st.markdown("---")
    st.markdown("### 🏠 Dimensiones")
    superficie = st.number_input("Superficie (m²)", min_value=30, max_value=600, value=90)
    dormitorios = st.slider("Dormitorios", 0, 8, 3)
    banos = st.slider("Num. Baños", 1, 6, 2)

# 3. Estado IA
if 'ia_params' not in st.session_state:
    st.session_state.ia_params = {
        'lujo': 3.0,
        'estado': "Bueno",
        'modernidad': 3.0,
        'foto': 6.0,
        'luz': 3.0
    }

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# 4. Interfaz
st.title("🏡 Tasador Inteligente (Tecnocasa AI)")

tab_visual, tab_calidades, tab_servicios, tab_nlp, tab_roi = st.tabs([
    "📸 Análisis Visual (IA)", 
    "🏗️ Extras y Calidades", 
    "🏙️ Entorno y Servicios",
    "📝 Descripción",
    "💰 Inversión"
])

# VISUAL
with tab_visual:
    # Sección de Carga de Imagen
    col_upload, col_result = st.columns([1, 2])
    
    with col_upload:
        st.info("Sube una foto para autocompletar.")
        uploaded_file = st.file_uploader("Subir imagen", type=['jpg', 'jpeg', 'png'], label_visibility="collapsed")
        
        if uploaded_file and api_key:
            if st.button("✨ Analizar con Gemini"):
                with st.spinner("Analizando calidades..."):
                    img = Image.open(uploaded_file)
                    datos = gemini.analizar_imagen(img, api_key)
                    if datos:
                        st.session_state.ia_params['lujo'] = float(datos.get('nivel_lujo', 3.0))
                        st.session_state.ia_params['estado'] = datos.get('estado', "Bueno")
                        st.session_state.ia_params['modernidad'] = float(datos.get('modernidad', 3.0))
                        st.session_state.ia_params['foto'] = float(datos.get('calidad_foto', 6.0))
                        st.session_state.ia_params['luz'] = float(datos.get('luminosidad', 3.0))
                        st.success("¡Parámetros actualizados!")

    with col_result:
        col_v1, col_v2, col_v3 = st.columns(3)
        with col_v1:
            st.markdown("#### ⭐ Estado")
            # Usamos st.session_state para el valor por defecto
            nivel_lujo = st.slider("Nivel de Lujo (1-5)", 1.0, 5.0, st.session_state.ia_params['lujo'])
            nivel_modernidad = st.slider("Modernidad", 1.0, 5.0, st.session_state.ia_params['modernidad'])
            
            estado_txt = st.select_slider("Estado Conservación", 
                                          options=["A reformar", "Bueno", "Muy bueno", "Reformado"], 
                                          value=st.session_state.ia_params['estado'])
            estado_map = {"A reformar": 1, "Bueno": 2, "Muy bueno": 3, "Reformado": 4}
            estado_val = estado_map[estado_txt]
            
        with col_v2:
            st.markdown("#### 📐 Espacio")
            calidad_iluminacion = st.slider("Luminosidad", 1.0, 5.0, st.session_state.ia_params['luz'])
            espacio_abierto = st.slider("Sensación Espacio", 1.0, 5.0, 3.0)
            distribucion = st.slider("Distribución", 1.0, 5.0, 3.0)
            vistas = st.checkbox("Buenas Vistas", value=False)

        with col_v3:
            st.markdown("#### 🖼️ Fotos")
            nivel_foto = st.slider("Calidad Fotos (IA)", 1.0, 10.0, st.session_state.ia_params['foto'])
            num_imgs = st.number_input("Num. Imágenes", 1, 50, 15)
            equilibrio = st.slider("Equilibrio Visual", 1.0, 10.0, 5.0)

    # Expander original mantenido
    with st.expander("Detalles Técnicos (Avanzado)"):
        c1, c2, c3 = st.columns(3)
        estilo = c1.selectbox("Estilo", options['estilos'])
        calidad_bano = c2.slider("Calidad Baño", 1.0, 5.0, 3.0)
        equip_cocina = c3.slider("Equip. Cocina", 1.0, 5.0, 3.0)

# EXTRAS
with tab_calidades:
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        tipo_inmueble = st.selectbox("Tipo Inmueble", options['tipos_inmueble'])
        anio = st.number_input("Año Construcción", 1900, 2025, 1990)
        planta = st.number_input("Planta", 0, 15, 2)
        ascensor = st.toggle("Ascensor", value=True)
        portero = st.toggle("Portero")
    with col_c2:
        calefaccion = st.selectbox("Calefacción", options['calefaccion'])
        aire = st.checkbox("Aire Acondicionado")
        amueblado = st.checkbox("Amueblado")
        garaje = st.checkbox("Garaje")
        trastero = st.checkbox("Trastero")
    with col_c3:
        suelo = st.selectbox("Suelo", options['suelos'])
        ventana = st.selectbox("Ventana", options['ventanas'])
        pared = st.selectbox("Pared", options['paredes'])
        terraza = st.checkbox("Terraza")
        piscina = st.checkbox("Piscina")

# SERVICIOS
with tab_servicios:
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        metro = st.checkbox("Metro Cerca", value=True)
        renfe = st.checkbox("Renfe Cerca")
        ruido_urb = st.slider("Ruido Urbano", 0, 100, 40)
        ruido_traf = st.slider("Ruido Tráfico", 0, 100, 45)
    with col_s2:
        n_super = st.number_input("Supermercados", 0, 10, 2)
        n_rest = st.number_input("Restaurantes", 0, 20, 5)
        n_hosp = st.number_input("Hospitales", 0, 5, 0)
        n_tienda = st.number_input("Tiendas", 0, 20, 4)
        n_farm = st.number_input("Farmacias", 0, 10, 1)
        n_bar = st.number_input("Bares", 0, 20, 3)

# NLP
with tab_nlp:
    c1, c2, c3 = st.columns(3)
    long_desc = c1.number_input("Long. Descripción", 0, 2000, 200)
    adj_pos = c2.number_input("Adjetivos Positivos", 0, 50, 5)
    urgencia = c3.slider("Urgencia", 0.0, 1.0, 0.0)

# 5. Predicción
st.markdown("---")

# Recopilar inputs
user_data = {
    'zona': zona, 'renta_interna': renta_interna,
    'superficie': superficie, 'dormitorios': dormitorios, 'banos': banos,
    'anio': anio, 'planta': planta, 'tipo_inmueble': tipo_inmueble,
    'nivel_lujo': nivel_lujo, 'nivel_modernidad': nivel_modernidad,
    'estado_val': estado_val, 'calidad_iluminacion': calidad_iluminacion,
    'nivel_foto': nivel_foto, 'espacio_abierto': espacio_abierto,
    'estilo': estilo, 'calidad_bano': calidad_bano, 'equip_cocina': equip_cocina,
    'distribucion': distribucion, 'equilibrio': equilibrio, 'num_imgs': num_imgs,
    'ascensor': ascensor, 'garaje': garaje, 'portero': portero, 'aire': aire,
    'terraza': terraza, 'piscina': piscina, 'metro': metro, 'renfe': renfe,
    'ruido_urb': ruido_urb, 'ruido_traf': ruido_traf,
    'calefaccion': calefaccion, 'suelo': suelo, 'ventana': ventana, 'pared': pared,
    'amueblado': amueblado, 'trastero': trastero,
    'long_desc': long_desc, 'adj_pos': adj_pos, 'urgencia': urgencia,
    'n_farm': n_farm, 'n_bar': n_bar, 'n_rest': n_rest, 
    'n_hosp': n_hosp, 'n_super': n_super, 'n_tienda': n_tienda,
    'vistas': 0
}
col_btn, col_debug = st.columns([1, 4])

# --- CÁLCULO DE PREDICCIÓN ---
# Lo calculamos silenciosamente para tener el dato 'precio_estimado' disponible para la IA
try:
    df_input_silent = features.preparar_dataframe(user_data, feature_columns)
    log_pred_silent = pipeline.predict(df_input_silent)[0]
    precio_estimado_global = np.expm1(log_pred_silent) * superficie
except:
    precio_estimado_global = 0

# INVERSIÓN
with tab_roi:
    col_inv1, col_inv2 = st.columns(2)
    with col_inv1:
        valor_defecto = int(precio_estimado_global) if precio_estimado_global > 0 else 200000
        precio_oferta = st.number_input("Precio de Compra (€)", value=valor_defecto, step=1000)
        impuestos     = st.number_input("Impuestos (%)", value=10.0,
                            help="ITP segunda mano: 6-10% según CCAA. IVA obra nueva: 10%.")
        reforma       = st.number_input("Reforma (€)", value=0, step=1000)

    with col_inv2:
        pct_financiacion = st.slider("% Financiación", 0, 100, 80)
        interes          = st.number_input("Interés Anual (%)", value=3.5, step=0.1)
        plazo            = st.slider("Años Hipoteca", 10, 40, 30)
        # ── NUEVO: gastos operativos ──
        gastos_pct       = st.number_input(
            "Gastos operativos anuales (%)",
            value=1.5, step=0.1,
            help="IBI + comunidad + seguro + vacíos. Típicamente 1–2% del precio."
        )

    # ── Cálculos ──────────────────────────────────────────────────────
    total_inversion = precio_oferta * (1 + impuestos / 100) + reforma
    prestamo        = precio_oferta * (pct_financiacion / 100)
    entrada         = total_inversion - prestamo

    # Cuota (Fórmula Francesa)
    if prestamo > 0 and interes > 0:
        r     = interes / 100 / 12
        n     = plazo * 12
        cuota = prestamo * r * (1 + r)**n / ((1 + r)**n - 1)
    elif prestamo > 0:
        cuota = prestamo / (plazo * 12)   # interés 0%
    else:
        cuota = 0

    # ── Yield dinámico según renta de la zona ────────────────
    # Zonas de renta alta → menos yield (precio alto, alquiler no sube igual)
    if renta_interna >= 50:
        yield_zona = 0.035
    elif renta_interna >= 35:
        yield_zona = 0.05
    else:
        yield_zona = 0.065
    alquiler_estimado = (precio_oferta * yield_zona) / 12

    # ── Cash flow y ROI netos (descontando gastos operativos) ─
    gastos_mensuales = (precio_oferta * gastos_pct / 100) / 12
    cash_flow        = alquiler_estimado - cuota - gastos_mensuales
    roi_bruto        = (alquiler_estimado * 12) / total_inversion * 100
    roi_neto         = ((alquiler_estimado - gastos_mensuales) * 12) / total_inversion * 100

    st.markdown("---")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Cuota Mensual",      f"{cuota:,.0f} €")
    m2.metric("Alquiler Estimado",  f"{alquiler_estimado:,.0f} €",
              delta=f"Yield {yield_zona*100:.1f}%")
    m3.metric("Cash Flow Neto",     f"{cash_flow:,.0f} €",
              delta_color="normal" if cash_flow > 0 else "inverse")
    m4.metric("ROI Neto",           f"{roi_neto:.1f}%",
              delta=f"Bruto {roi_bruto:.1f}%")

    # Desglose transparente
    with st.expander("📊 Desglose financiero completo"):
        st.write(f"**Entrada necesaria:** {entrada:,.0f} € (20% precio + impuestos + reforma)")
        st.write(f"**Préstamo:** {prestamo:,.0f} € a {interes}% durante {plazo} años")
        st.write(f"**Gastos operativos:** {gastos_mensuales:,.0f} €/mes "
                 f"({gastos_pct}% anual sobre precio de compra)")
        st.write(f"**ROI bruto:** {roi_bruto:.2f}%  |  **ROI neto:** {roi_neto:.2f}%")

col_btn, col_chat = st.columns([1, 4])
with col_btn:
    predict_btn = st.button("🚀 CALCULAR VALOR")

if predict_btn:
    
    try:
        # Preparar y Predecir
        df_input = features.preparar_dataframe(user_data, feature_columns)
        log_pred = pipeline.predict(df_input)[0]
        precio_m2 = np.expm1(log_pred)
        precio_total = precio_m2 * superficie
        
        # Resultados
        st.success("✅ Tasación Completada")
        c1, c2 = st.columns([2, 1])
        c1.metric("PRECIO ESTIMADO", f"{precio_total:,.0f} €")
        c1.caption(f"Horquilla: {precio_total*0.89:,.0f} - {precio_total*1.11:,.0f} €")
        c2.metric("Precio Unitario", f"{precio_m2:,.0f} €/m²")
        
        with st.expander("🛠️ Ver datos calculados internamente (Hidden vars)"):
            st.write(f"Renta Neta Usada: {renta_interna}")
            st.write(f"Superficie x Lujo: {user_data['superficie'] * user_data['nivel_lujo']}")
            st.dataframe(df_input)

        # Gráficos
        plots.render_analysis(precio_m2, user_data, df_ref)

        # TESTIGOS DE VENTA (MARKET)
        st.subheader("🏘️ Testigos Comparables (Vendidos en la zona)")
        testigos = market.encontrar_testigos(df_ref, user_data)
        if testigos is not None:
            st.dataframe(testigos, width='stretch')
            st.caption("Estos son los 5 inmuebles más similares encontrados en nuestra base de datos histórica.")
        else:
            st.warning("No se encontraron suficientes testigos similares en esta zona.")

        # GENERADOR DE COPYWRITING
        st.subheader("✍️ Generador de Anuncios IA")
        if api_key:
            client_gen = gemini.configurar_cliente(api_key)
            if client_gen:
                with st.spinner("Redactando anuncio perfecto..."):
                    copy_ad = market.generar_copy_anuncio(client_gen, user_data, precio_estimado_global)
                    st.text_area("Copia este texto para Idealista/Fotocasa:", value=copy_ad, height=200)
        else:
            st.info("Introduce tu API Key para generar el anuncio de venta.")

        # Generar PDF
        pdf_bytes = pdf_gen.crear_informe(user_data, precio_estimado_global, precio_estimado_global/superficie)
        col_chat.download_button(
            label="📄 Descargar Informe PDF",
            data=pdf_bytes,
            file_name="informe_tasacion.pdf",
            mime="application/pdf"
        )
        
    except Exception as e:
        st.error(f"Error durante el cálculo: {e}")

# 6. ASISTENTE IA (FLOATING CHAT)

# Botón flotante para abrir el asistente
with st.popover("💬 Hablar con el Asistente IA"):
    st.markdown("### 🤖 Asesor Inmobiliario")
    st.caption(f"Contexto actual: {zona} | {superficie}m² | Valoración: {precio_estimado_global:,.0f}€")
    
    # Historial de chat
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Input del usuario
    if prompt := st.chat_input("Ej: Me lo venden por 200k, ¿es buen precio?"):
        if not api_key:
            st.error("Por favor, introduce tu API Key en la barra lateral.")
        else:
            # Añadir mensaje usuario
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

            # Generar respuesta
            with st.chat_message("assistant"):
                with st.spinner("Analizando mercado..."):
                    # Preparar contexto (RAG Lite)
                    contexto_mercado = assistant.generar_contexto_mercado(df_ref, zona)
                    contexto_casa = assistant.formatear_prediccion_actual(user_data, precio_estimado_global)
                    
                    # Llamada a Gemini
                    respuesta = gemini.chat_inmobiliario(
                        prompt, 
                        contexto_mercado, 
                        contexto_casa, 
                        api_key
                    )
                    st.write(respuesta)
            
            # Guardar respuesta
            st.session_state.chat_history.append({"role": "assistant", "content": respuesta})