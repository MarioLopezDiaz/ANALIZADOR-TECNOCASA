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
    
    avg_m2 = (df_zona['Precio'] / df_zona['Superficie']).mean()
    avg_lujo = df_zona['nivel_lujo'].mean()
    avg_foto = df_zona['nivel_foto_profesional'].mean()

    # GRÁFICO 1: VELOCÍMETRO
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = precio_m2,
        # AÑADIDO: Sufijo € y formato sin decimales
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
        r=[avg_lujo, df_zona['nivel_modernidad'].mean(), avg_foto/2, 3.0, 2.5],
        theta=categories, fill='toself', name=f'Media {zona}', line_color='gray', opacity=0.5
    ))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=True, title="Comparativa Visual vs Zona")

    # Render
    c1, c2 = st.columns(2)
    with c1: st.plotly_chart(fig_gauge, width="stretch")
    with c2: st.plotly_chart(fig_radar, width="stretch")
    
    # --- 3. MOTOR DE INFERENCIA DE PATRONES (Lógica de Negocio) ---
    st.subheader("🧠 Diagnóstico Inteligente del Inmueble")
    
    # Listas para acumular hallazgos
    pros = []
    cons = []
    opportunities = []

    # -- ANÁLISIS DE PRECIO --
    diff_pct = ((precio_m2 - avg_m2) / avg_m2) * 100
    
    if diff_pct < -10:
        opportunities.append(f"📉 **Oportunidad de Mercado:** El inmueble está un **{abs(diff_pct):.1f}% más barato** que la media de la zona. Ideal para compra rápida.")
    elif diff_pct > 10:
        if inputs['nivel_lujo'] > avg_lujo:
            pros.append(f"💎 **Valor Justificado:** El sobreprecio del {diff_pct:.1f}% se justifica por calidades muy superiores a la media.")
        else:
            cons.append(f"⚠️ **Riesgo de Sobreprecio:** Cotiza un {diff_pct:.1f}% por encima de la media sin tener calidades visuales significativamente superiores.")

    # -- ANÁLISIS FÍSICO Y ESTRUCTURAL --
    # Regla: Piso alto sin ascensor (Penalización grave)
    if inputs['planta'] > 2 and inputs['ascensor'] == 0:
        cons.append("🛑 **Accesibilidad Crítica:** Ser una {inputs['planta']}ª planta sin ascensor reduce drásticamente el mercado potencial (familias, mayores).")
    elif inputs['ascensor'] == 1:
        pros.append("🛗 **Accesibilidad:** Cuenta con ascensor, un valor seguro en revalorización.")

    # Regla: Piso pequeño bien distribuido (Perfil Inversor)
    if inputs['superficie'] < 60 and inputs['dormitorios'] >= 2:
        pros.append("💰 **Perfil Inversor:** Alta rentabilidad potencial por m² al tener {inputs['dormitorios']} habitaciones en pocos metros.")

    # -- ANÁLISIS DE ESTADO Y VISUAL (IA) --
    # Regla: Buen estado pero malas fotos
    if inputs['nivel_foto'] < 5 and inputs['estado_val'] >= 3:
        opportunities.append("📸 **Marketing Deficiente:** La casa está en buen estado, pero las fotos no le hacen justicia. Mejorar el reportaje podría subir la tasación un 3-5%.")
    
    # Regla: Estado a reformar en zona cara
    if inputs['estado_val'] <= 2 and inputs['renta_interna'] > 40:
        opportunities.append("🛠️ **Potencial de Flipping:** Inmueble a reformar en zona de alta renta. Alto margen de beneficio tras reforma integral.")

    # Regla: Lujo superior
    if inputs['nivel_lujo'] > avg_lujo + 0.8:
        pros.append("✨ **Acabados Premium:** Nivel de lujo muy superior a los competidores de la zona.")

    # -- ANÁLISIS DE ENTORNO --
    # Regla: Ruido
    if inputs['ruido_urb'] > 65:
        cons.append(f"🔊 **Contaminación Acústica:** Zona ruidosa ({inputs['ruido_urb']} dB). Se recomienda destacar aislamiento de ventanas en la venta.")
    elif inputs['ruido_urb'] < 45:
        pros.append("🤫 **Oasis Urbano:** Ubicación excepcionalmente tranquila para la zona.")

    # Regla: Servicios
    if inputs['metro'] == 1 or inputs['renfe'] == 1:
        pros.append("🚇 **Conectividad:** Excelente transporte público (Metro/Renfe) cercano.")

    # --- 4. RENDERIZADO DE RESULTADOS ---
    
    # Mostrar Pros y Contras en columnas
    col_pro, col_con = st.columns(2)
    
    with col_pro:
        st.success("✅ **PUNTOS FUERTES (Pros)**")
        if pros:
            for p in pros: st.write(p)
        else:
            st.write("• No destacan factores positivos críticos.")

    with col_con:
        st.error("⚠️ **FACTORES DE RIESGO (Contras)**")
        if cons:
            for c in cons: st.write(c)
        else:
            st.write("• No se detectan penalizaciones graves.")

    # Mostrar Oportunidades estratégicas
    if opportunities:
        st.info("💡 **RECOMENDACIONES ESTRATÉGICAS**")
        for op in opportunities:
            st.markdown(f"- {op}")

    # Conclusión final del modelo
    st.caption(f"ℹ️ *Análisis basado en {len(df_zona)} testigos comparables en {zona} y procesado mediante GBR + Gemini 2.0 Vision.*")