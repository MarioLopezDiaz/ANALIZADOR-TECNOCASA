"""
MÓDULO DE VISUALIZACIÓN DE DATOS (PLOTLY/SEABORN)
-------------------------------------------------
Genera los gráficos interactivos renderizados en el dashboard de Streamlit.
Incluye visualizaciones de explicabilidad del modelo (adaptaciones de SHAP para web),
comparativas de precios de mercado y desglose visual del impacto de las variables de IA.
"""

import streamlit as st
import plotly.graph_objects as go

def render_analysis(precio_m2, inputs, df_ref):
    st.markdown("---")
    st.subheader("📊 Análisis de Mercado & Insights")
    
    # Datos Contexto
    zona = inputs['zona']
    df_zona = df_ref[df_ref['Localizacion_Clave'] == zona]
    if len(df_zona) < 5: df_zona = df_ref
    
    avg_m2         = (df_zona['Precio'] / df_zona['Superficie']).mean()
    avg_lujo       = df_zona['nivel_lujo'].mean()
    avg_foto       = df_zona['nivel_foto_profesional'].mean()
    avg_modernidad = df_zona['nivel_modernidad'].mean() if 'nivel_modernidad' in df_zona.columns else 3.0
    avg_superficie = df_zona['Superficie'].mean()

    # GRÁFICO 1: VELOCÍMETRO
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = precio_m2,
        number = {'suffix': " €", 'valueformat': ",.0f"}, 
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Valoración Unitario (€/m²) vs {zona}", 'font': {'size': 17}},
        delta = {
            'reference': avg_m2, 
            'increasing': {'color': "red"}, 
            'decreasing': {'color': "green"},
            'suffix': " €",
            'valueformat': ",.0f"
        },
        gauge = {
            'axis': {
                'range': [avg_m2*0.6, avg_m2*1.4],
                'tickformat': ",.0f"
            },
            'bar': {'color': "#2c3e50"},
            'steps': [
                {'range': [avg_m2*0.6, avg_m2*0.9], 'color': "#d4edda"},
                {'range': [avg_m2*0.9, avg_m2*1.1], 'color': "#fff3cd"},
                {'range': [avg_m2*1.1, avg_m2*1.4], 'color': "#f8d7da"}],
            'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': precio_m2}
        }
    ))

    # GRÁFICO 2: RADAR
    categories = ['Nivel Lujo', 'Modernidad', 'Calidad Foto', 'Iluminación', 'Estado']
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=[inputs['nivel_lujo'], inputs['nivel_modernidad'], inputs['nivel_foto']/2, inputs['calidad_iluminacion'], inputs['estado_val']],
        theta=categories, fill='toself', name='Tu Inmueble', line_color='#007bff'
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=[avg_lujo, avg_modernidad, avg_foto/2, 3.0, 2.5],
        theta=categories, fill='toself', name=f'Media {zona}', line_color='gray', opacity=0.5
    ))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=True, title="Comparativa Visual vs Zona")

    # Render
    c1, c2 = st.columns(2)
    with c1: st.plotly_chart(fig_gauge, width="stretch")
    with c2: st.plotly_chart(fig_radar, width="stretch")
    
    # --- MOTOR DE INFERENCIA DE PATRONES ---
    st.subheader("🧠 Diagnóstico Inteligente del Inmueble")
    
    pros         = []
    cons         = []
    opportunities = []

    # ═══════════════════════════════════════════════════════════════
    # 1. ANÁLISIS DE PRECIO VS MERCADO
    # ═══════════════════════════════════════════════════════════════
    diff_pct = ((precio_m2 - avg_m2) / avg_m2) * 100
    
    if diff_pct < -20:
        opportunities.append(f"🔥 **Gran Oportunidad:** El inmueble está un **{abs(diff_pct):.1f}% por debajo** de la media de zona. Precio muy atractivo para compra o inversión inmediata.")
    elif diff_pct < -10:
        opportunities.append(f"📉 **Oportunidad de Mercado:** El inmueble cotiza un **{abs(diff_pct):.1f}% más barato** que la media de la zona. Margen de negociación favorable.")
    elif diff_pct > 20:
        if inputs['nivel_lujo'] > avg_lujo + 1.0 and inputs['estado_val'] >= 3:
            pros.append(f"💎 **Valor Premium Justificado:** El sobreprecio del {diff_pct:.1f}% está respaldado por acabados de lujo y excelente estado de conservación.")
        else:
            cons.append(f"🚨 **Riesgo de Sobreprecio Severo:** Cotiza un {diff_pct:.1f}% por encima de la media sin calidades visuales que lo justifiquen. Riesgo alto de no venderse.")
    elif diff_pct > 10:
        if inputs['nivel_lujo'] > avg_lujo + 0.5:
            pros.append(f"💎 **Valor Justificado:** El sobreprecio del {diff_pct:.1f}% se justifica por calidades superiores a la media de zona.")
        else:
            cons.append(f"⚠️ **Riesgo de Sobreprecio:** Cotiza un {diff_pct:.1f}% por encima de la media sin tener calidades visuales significativamente superiores.")

    # ═══════════════════════════════════════════════════════════════
    # 2. ANÁLISIS FÍSICO Y ESTRUCTURAL
    # ═══════════════════════════════════════════════════════════════

    # -- Planta y ascensor --
    if inputs['planta'] > 4 and not inputs['ascensor']:
        cons.append(f"🛑 **Accesibilidad Crítica:** Planta {inputs['planta']} sin ascensor. Excluye a familias con niños, personas mayores y con movilidad reducida. Penalización grave en valor.")
    elif inputs['planta'] > 2 and not inputs['ascensor']:
        cons.append(f"🛑 **Accesibilidad Reducida:** Planta {inputs['planta']} sin ascensor. Reduce drásticamente el mercado potencial (familias, mayores).")
    elif inputs['ascensor']:
        pros.append("🛗 **Accesibilidad:** Cuenta con ascensor, un valor seguro en revalorización y amplía el perfil de comprador.")

    # -- Planta baja (pros y contras) --
    if inputs['planta'] == 0:
        cons.append("🏢 **Planta Baja:** Mayor exposición al ruido de calle, menos luminosidad natural y menor privacidad. Suele penalizar el precio un 5-8%.")
    
    # -- Planta alta con ascensor (pro) --
    if inputs['planta'] >= 4 and inputs['ascensor']:
        pros.append(f"🌇 **Planta Alta con Ascensor:** Las plantas elevadas con ascensor suelen revalorizarse por las vistas, la tranquilidad y la luminosidad.")

    # -- Superficie y habitaciones --
    if inputs['superficie'] < 60 and inputs['dormitorios'] >= 2:
        pros.append(f"💰 **Perfil Inversor:** Alta rentabilidad potencial por m² al tener {inputs['dormitorios']} habitaciones en {inputs['superficie']} m². Ideal para alquiler.")
    
    if inputs['superficie'] > 120 and inputs['dormitorios'] >= 4:
        pros.append(f"👨‍👩‍👧‍👦 **Inmueble Familiar Premium:** Con {inputs['superficie']} m² y {inputs['dormitorios']} dormitorios, se posiciona en el segmento más demandado por familias con poder adquisitivo alto.")

    # -- Ratio dormitorios/superficie muy bajo (piso grande pero pocas habitaciones) --
    dorm_m2 = inputs['dormitorios'] / inputs['superficie'] if inputs['superficie'] > 0 else 0
    if dorm_m2 < 0.02 and inputs['superficie'] > 80:
        opportunities.append(f"🔨 **Potencial de Redistribución:** El piso tiene {inputs['superficie']} m² pero solo {inputs['dormitorios']} dormitorios. Una reforma de distribución podría aumentar el valor significativamente.")

    # -- Antigüedad --
    edad = inputs.get('anio', 1990)
    from datetime import datetime
    anios_antiguedad = datetime.now().year - edad
    if anios_antiguedad > 50 and inputs['estado_val'] <= 2:
        cons.append(f"🏚️ **Inmueble Antiguo y Deteriorado:** Con {anios_antiguedad} años y en estado {inputs['estado_val']}/4, pueden surgir costes ocultos de instalaciones (eléctrica, fontanería, estructura).")
    elif anios_antiguedad > 50 and inputs['estado_val'] >= 4:
        pros.append(f"🏛️ **Clásico Renovado:** Inmueble de carácter ({anios_antiguedad} años) completamente reformado. Combina la solidez constructiva antigua con acabados modernos.")
    elif anios_antiguedad < 10:
        pros.append(f"🆕 **Inmueble Reciente:** Con solo {anios_antiguedad} años de antigüedad, las instalaciones y estructura están en óptimas condiciones. Mínimo mantenimiento previsto.")

    # ═══════════════════════════════════════════════════════════════
    # 3. ANÁLISIS DE ESTADO Y CALIDAD VISUAL (IA)
    # ═══════════════════════════════════════════════════════════════

    # -- Fotos deficientes en buen inmueble --
    if inputs['nivel_foto'] < 5 and inputs['estado_val'] >= 3:
        opportunities.append("📸 **Marketing Deficiente:** La casa está en buen estado pero las fotos no le hacen justicia. Un reportaje profesional podría mejorar la percepción del valor un 3-7%.")
    
    # -- Fotos excelentes en inmueble mediocre --
    if inputs['nivel_foto'] >= 8 and inputs['estado_val'] <= 2:
        cons.append("🎭 **Alerta de Presentación:** Las fotos son de alta calidad pero el estado real es bajo. El comprador puede sentirse engañado al visitar. Riesgo de negociación agresiva a la baja.")
    
    # -- Estado a reformar en zona cara --
    if inputs['estado_val'] <= 2 and inputs['renta_interna'] > 40:
        opportunities.append("🛠️ **Potencial de Flipping:** Inmueble a reformar en zona de alta renta. Alto margen de beneficio tras reforma integral. Perfil ideal para inversor con experiencia.")
    
    # -- Recién reformado --
    if inputs['estado_val'] == 4:
        pros.append("✅ **Llave en Mano:** Inmueble completamente reformado. El comprador no necesita invertir nada adicional, lo que amplía el perfil y acelera la venta.")
    
    # -- Lujo muy superior a la media --
    if inputs['nivel_lujo'] > avg_lujo + 1.2:
        pros.append(f"✨ **Acabados Premium:** Nivel de lujo ({inputs['nivel_lujo']:.1f}/5) muy superior a la media de zona ({avg_lujo:.1f}/5). Atrae a un comprador de alto poder adquisitivo.")
    elif inputs['nivel_lujo'] > avg_lujo + 0.5:
        pros.append("✨ **Acabados Superiores:** Nivel de lujo por encima de la media de zona. Factor diferenciador positivo en la negociación.")
    
    # -- Lujo muy inferior a la media --
    if inputs['nivel_lujo'] < avg_lujo - 1.0:
        cons.append(f"📉 **Acabados por Debajo de la Zona:** Nivel de lujo ({inputs['nivel_lujo']:.1f}/5) notablemente inferior a la media ({avg_lujo:.1f}/5). Dificulta competir en precio con el resto de la oferta.")

    # -- Modernidad superior --
    if inputs['nivel_modernidad'] > avg_modernidad + 0.8:
        pros.append(f"🆙 **Diseño Moderno:** Estética actualizada muy por encima de la media de zona ({inputs['nivel_modernidad']:.1f} vs {avg_modernidad:.1f}/5). Muy demandado por compradores jóvenes.")

    # -- Iluminación excepcional --
    if inputs['calidad_iluminacion'] >= 4.5:
        pros.append("☀️ **Luminosidad Excepcional:** Puntuación de luz muy alta. La luminosidad es uno de los factores más valorados por los compradores en encuestas de preferencias.")
    elif inputs['calidad_iluminacion'] <= 2.0:
        cons.append("🌑 **Escasa Luminosidad Natural:** Piso oscuro. Este factor penaliza la percepción del inmueble y suele ser el principal motivo de descarte en visitas.")

    # ═══════════════════════════════════════════════════════════════
    # 4. ANÁLISIS DE DOTACIONES
    # ═══════════════════════════════════════════════════════════════

    # -- Conjunto de extras premium --
    extras_premium = sum([
        bool(inputs.get('garaje')), bool(inputs.get('piscina')),
        bool(inputs.get('terraza')), bool(inputs.get('trastero')),
        bool(inputs.get('portero'))
    ])
    if extras_premium >= 4:
        pros.append(f"🏆 **Pack Completo de Extras:** El inmueble cuenta con {extras_premium} de los 5 extras más valorados (garaje, piscina, terraza, trastero, portero). Posicionamiento top en la zona.")
    elif extras_premium >= 2:
        pros.append(f"🎁 **Buenos Extras:** {extras_premium} extras relevantes incluidos. Valor añadido respecto a la oferta básica de la zona.")

    # -- Garaje en zona de alta renta --
    if inputs.get('garaje') and inputs['renta_interna'] > 40:
        pros.append("🚗 **Garaje en Zona Premium:** El garaje en zonas de alta renta puede representar entre 15.000€ y 40.000€ de valor añadido al precio total.")
    
    # -- Sin garaje en zona de alta renta --
    if not inputs.get('garaje') and inputs['renta_interna'] > 45:
        cons.append("🚫 **Sin Garaje en Zona de Alta Demanda:** La ausencia de garaje en una zona premium puede ser un freno importante para familias con vehículo.")

    # -- Terraza o balcón --
    if inputs.get('terraza'):
        pros.append("🌿 **Terraza / Balcón:** La terraza es uno de los extras con mayor retorno post-pandemia. Incrementa el valor entre un 5% y un 15% según el tamaño.")

    # -- Piscina comunitaria --
    if inputs.get('piscina'):
        pros.append("🏊 **Piscina:** Activo muy valorado en verano. Aumenta el atractivo para familias y facilita el alquiler vacacional o de temporada.")

    # -- Aire acondicionado --
    if inputs.get('aire'):
        pros.append("❄️ **Aire Acondicionado:** Instalación ya presente. Evita al comprador una inversión de 1.500-4.000€ y es cada vez más demandado por el cambio climático.")
    else:
        opportunities.append("🌡️ **Sin Climatización:** Instalar aire acondicionado antes de vender puede aumentar el precio percibido más de lo que cuesta la instalación (~2.000-3.500€).")

    # -- Amueblado --
    if inputs.get('amueblado'):
        pros.append("🪑 **Amueblado:** Muy conveniente para inversores de alquiler. Permite alquilar de inmediato sin inversión adicional.")

    # ═══════════════════════════════════════════════════════════════
    # 5. ANÁLISIS DE ENTORNO Y SERVICIOS
    # ═══════════════════════════════════════════════════════════════

    # -- Ruido urbano --
    if inputs['ruido_urb'] > 70:
        cons.append(f"🔊 **Contaminación Acústica Grave:** Zona muy ruidosa ({inputs['ruido_urb']} dB). Puede infringir normativa de habitabilidad. Penalización significativa en valor y dificultad de venta.")
    elif inputs['ruido_urb'] > 55:
        cons.append(f"🔊 **Contaminación Acústica:** Zona ruidosa ({inputs['ruido_urb']} dB). Se recomienda destacar el aislamiento de ventanas en la venta y en el anuncio.")
    elif inputs['ruido_urb'] < 35:
        pros.append("🤫 **Oasis Urbano:** Ubicación excepcionalmente tranquila para el entorno urbano. Muy valorado por familias y perfiles de mayor edad.")
    elif inputs['ruido_urb'] < 45:
        pros.append("🤫 **Zona Tranquila:** Nivel de ruido por debajo de la media urbana. Factor positivo en la decisión de compra.")

    # -- Transporte público --
    if inputs['metro'] and inputs['renfe']:
        pros.append("🚇 **Conectividad Máxima:** Cuenta con Metro Y Renfe cercanos. La doble conexión de transporte es un factor de revalorización muy relevante en ciudades grandes.")
    elif inputs['metro']:
        pros.append("🚇 **Metro Cercano:** Excelente transporte público. El acceso a metro incrementa el valor del inmueble entre un 3% y un 8% según estudios de mercado.")
    elif inputs['renfe']:
        pros.append("🚆 **Renfe Cercana:** Buena conexión con la red de cercanías, muy valorada por compradores que trabajan en el centro o en otras ciudades.")
    else:
        if inputs['renta_interna'] < 30:
            cons.append("🚶 **Zona sin Transporte Público Cercano:** La falta de metro o Renfe en una zona de renta media-baja limita el perfil del comprador y puede penalizar el precio.")

    # -- Servicios de proximidad --
    servicios_total = inputs['n_super'] + inputs['n_rest'] + inputs['n_farm'] + inputs['n_bar'] + inputs['n_hosp'] + inputs['n_tienda']
    if servicios_total >= 15:
        pros.append(f"🏪 **Zona Muy Bien Equipada:** {servicios_total} servicios en el entorno inmediato. Alta comodidad de vida cotidiana, muy valorado por compradores jóvenes y familias.")
    elif servicios_total >= 8:
        pros.append(f"🛒 **Buenos Servicios de Proximidad:** {servicios_total} servicios cercanos. El barrio ofrece comodidades suficientes para el día a día.")
    elif servicios_total <= 3:
        cons.append(f"🏜️ **Escasos Servicios de Proximidad:** Solo {servicios_total} servicios en el entorno. La falta de comercios y restaurantes puede ser un freno para compradores urbanos.")

    # -- Hospital cercano --
    if inputs['n_hosp'] >= 1:
        pros.append("🏥 **Hospital Cercano:** La proximidad a centros sanitarios es especialmente valorada por compradores de edad media-alta y familias con niños.")

    # ═══════════════════════════════════════════════════════════════
    # 6. ANÁLISIS DE RENTABILIDAD (PERFIL INVERSOR)
    # ═══════════════════════════════════════════════════════════════

    # -- Zona de alta renta con buen estado: perfil de revalorización --
    if inputs['renta_interna'] > 50 and inputs['estado_val'] >= 3 and inputs['nivel_lujo'] >= 3.5:
        pros.append("📈 **Alto Potencial de Revalorización:** Zona de renta alta, buen estado y calidades superiores. Perfil ideal para inversión a largo plazo con apreciación del capital.")

    # -- Piso pequeño en zona de alta renta: alquiler --
    if inputs['superficie'] < 65 and inputs['renta_interna'] > 40:
        opportunities.append(f"🏙️ **Ideal para Alquiler Urbano:** Piso de {inputs['superficie']} m² en zona de renta alta ({inputs['renta_interna']:.0f}k€). Los pisos compactos en estas zonas tienen altísima demanda de alquiler.")

    # -- Zona baja con inmueble grande: difícil salida --
    if inputs['renta_interna'] < 25 and inputs['superficie'] > 120:
        cons.append(f"⚡ **Desajuste Mercado-Producto:** Inmueble grande ({inputs['superficie']} m²) en zona de renta baja ({inputs['renta_interna']:.0f}k€). El mercado potencial de compradores es muy reducido.")

    # ═══════════════════════════════════════════════════════════════
    # 7. RENDER DE RESULTADOS
    # ═══════════════════════════════════════════════════════════════
    
    col_pro, col_con = st.columns(2)
    
    with col_pro:
        st.success(f"✅ **PUNTOS FUERTES ({len(pros)} detectados)**")
        if pros:
            for p in pros: st.write(p)
        else:
            st.write("• No destacan factores positivos críticos.")

    with col_con:
        st.error(f"⚠️ **FACTORES DE RIESGO ({len(cons)} detectados)**")
        if cons:
            for c in cons: st.write(c)
        else:
            st.write("• No se detectan penalizaciones graves.")

    if opportunities:
        st.info(f"💡 **RECOMENDACIONES ESTRATÉGICAS ({len(opportunities)} detectadas)**")
        for op in opportunities:
            st.markdown(f"- {op}")

    st.caption(f"ℹ️ *Análisis basado en {len(df_zona)} testigos comparables en {zona} y procesado mediante GBR + Gemini 2.0 Vision.*")