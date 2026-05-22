"""
GENERADOR DE INFORMES TÉCNICOS AUTOMATIZADOS
--------------------------------------------
Módulo encargado de compilar los resultados de la inferencia, las características
de la IA y las proyecciones de inversión en un documento PDF estructurado,
profesional y listo para descargar por el usuario final.
"""

import streamlit as st
from fpdf import FPDF
import base64
from datetime import datetime

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Tecnocasa AI Valuator - Informe de Tasación', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def crear_informe(datos_inmueble, precio_estimado, precio_m2):
    pdf = PDF()
    pdf.add_page()
    
    # 1. Título y Fecha
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Fecha de emisión: {datetime.now().strftime('%d/%m/%Y')}", 0, 1)
    pdf.ln(5)
    
    # 2. Resumen de Valoración
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 15, f"Valor Estimado: {precio_estimado:,.0f} EUR", 1, 1, 'C', 1)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Precio Unitario: {precio_m2:,.0f} EUR/m2", 0, 1, 'C')
    pdf.ln(10)
    
    # 3. Detalles del Inmueble
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Características del Inmueble:", 0, 1)
    pdf.set_font("Arial", size=11)
    
    detalles = [
        f"Zona: {datos_inmueble['zona']}",
        f"Superficie: {datos_inmueble['superficie']} m2",
        f"Habitaciones: {datos_inmueble['dormitorios']} | Baños: {datos_inmueble['banos']}",
        f"Planta: {datos_inmueble['planta']} | Ascensor: {'Sí' if datos_inmueble['ascensor'] else 'No'}",
        f"Estado: Nivel {datos_inmueble['estado_val']}/4",
        f"Calidad Visual (IA): Lujo {datos_inmueble['nivel_lujo']}/5"
    ]
    
    for det in detalles:
        pdf.cell(0, 8, f"- {det}", 0, 1)
        
    # 4. Descargo de responsabilidad
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 9)
    pdf.multi_cell(0, 5, "Nota: Este informe es una estimación basada en Inteligencia Artificial y datos históricos. No sustituye una tasación oficial (ECO).")
    
    return pdf.output(dest='S').encode('latin-1')