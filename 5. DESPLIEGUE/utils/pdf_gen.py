"""
GENERADOR DE INFORMES TÉCNICOS AUTOMATIZADOS
--------------------------------------------
Módulo encargado de compilar los resultados de la inferencia, las características
de la IA y las proyecciones de inversión en un documento PDF estructurado,
profesional y listo para descargar por el usuario final.

"""

import io
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable, KeepTogether
)

# ── Paleta corporativa ────────────────────────────────────────────────────────
AZUL_OSCURO = colors.HexColor('#1B2A4A')
AZUL_MEDIO  = colors.HexColor('#2C5282')
AZUL_CLARO  = colors.HexColor('#4A90D9')
GRIS_FONDO  = colors.HexColor('#F7F9FC')
GRIS_LINEA  = colors.HexColor('#DEE3EA')
VERDE       = colors.HexColor('#27AE60')
NARANJA     = colors.HexColor('#E67E22')
BLANCO      = colors.white

PAGE_W, PAGE_H = A4
CONTENT_W = PAGE_W - 40 * mm   # ancho útil con márgenes de 20 mm


# ── Estilos de párrafo ────────────────────────────────────────────────────────
def _estilos():
    e = {}
    e['titulo_doc'] = ParagraphStyle(
        'titulo_doc', fontSize=20, fontName='Helvetica-Bold',
        textColor=BLANCO, alignment=TA_CENTER)
    e['subtitulo_doc'] = ParagraphStyle(
        'subtitulo_doc', fontSize=9, fontName='Helvetica',
        textColor=colors.HexColor('#BDD7F5'), alignment=TA_CENTER)
    e['seccion'] = ParagraphStyle(
        'seccion', fontSize=11, fontName='Helvetica-Bold',
        textColor=AZUL_OSCURO, spaceBefore=4, spaceAfter=3)
    e['normal'] = ParagraphStyle(
        'normal', fontSize=9, fontName='Helvetica',
        textColor=colors.HexColor('#333333'), leading=13)
    e['precio_grande'] = ParagraphStyle(
        'precio_grande', fontSize=26, fontName='Helvetica-Bold',
        textColor=AZUL_OSCURO, alignment=TA_CENTER)
    e['precio_sub'] = ParagraphStyle(
        'precio_sub', fontSize=10, fontName='Helvetica',
        textColor=colors.HexColor('#555555'), alignment=TA_CENTER)
    e['etiqueta'] = ParagraphStyle(
        'etiqueta', fontSize=8, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#555555'))
    e['valor'] = ParagraphStyle(
        'valor', fontSize=9, fontName='Helvetica',
        textColor=AZUL_OSCURO)
    e['metrica'] = ParagraphStyle(
        'metrica', fontSize=14, fontName='Helvetica-Bold',
        alignment=TA_CENTER)
    e['disclaimer'] = ParagraphStyle(
        'disclaimer', fontSize=7.5, fontName='Helvetica-Oblique',
        textColor=colors.HexColor('#888888'), alignment=TA_CENTER, leading=11)
    return e


# ── Bloques reutilizables ─────────────────────────────────────────────────────

def _header_banner(story, estilos, fecha):
    """Banner de cabecera azul oscuro + franja secundaria."""
    banner = Table(
        [[Paragraph('TECNOCASA AI VALUATOR', estilos['titulo_doc'])]],
        colWidths=[CONTENT_W]
    )
    banner.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), AZUL_OSCURO),
        ('TOPPADDING',    (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING',   (0, 0), (-1, -1), 8),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 8),
    ]))
    story.append(banner)

    sub = Table(
        [[Paragraph(f'Informe de Tasación Inteligente  ·  Emitido el {fecha}',
                    estilos['subtitulo_doc'])]],
        colWidths=[CONTENT_W]
    )
    sub.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), AZUL_MEDIO),
        ('TOPPADDING',    (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(sub)
    story.append(Spacer(1, 6 * mm))


def _bloque_precio(story, estilos, precio_estimado, precio_m2):
    """Caja central con el precio estimado y horquilla."""
    rango_low  = precio_estimado * 0.89
    rango_high = precio_estimado * 1.11

    datos = [
        [Paragraph('VALORACIÓN ESTIMADA', estilos['etiqueta'])],
        [Paragraph(f'{precio_estimado:,.0f} \u20ac', estilos['precio_grande'])],
        [Paragraph(f'Precio unitario: {precio_m2:,.0f} \u20ac/m\u00b2', estilos['precio_sub'])],
        [Paragraph(
            f'Horquilla de mercado:  {rango_low:,.0f} \u20ac \u2014 {rango_high:,.0f} \u20ac',
            estilos['precio_sub']
        )],
    ]
    t = Table(datos, colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), GRIS_FONDO),
        ('BOX',           (0, 0), (-1, -1), 1.5, AZUL_CLARO),
        ('TOPPADDING',    (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING',   (0, 0), (-1, -1), 10),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 10),
        ('ALIGN',         (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(KeepTogether(t))
    story.append(Spacer(1, 6 * mm))


def _titulo_seccion(story, estilos, texto):
    story.append(HRFlowable(width='100%', thickness=1, color=AZUL_CLARO, spaceAfter=3))
    story.append(Paragraph(texto, estilos['seccion']))


def _tabla_detalle(story, estilos, datos, col_widths=None):
    """Tabla de dos columnas etiqueta | valor con filas cebra."""
    if col_widths is None:
        col_widths = [CONTENT_W * 0.42, CONTENT_W * 0.58]

    rows = [
        [Paragraph(etiq, estilos['etiqueta']), Paragraph(str(val), estilos['valor'])]
        for etiq, val in datos
    ]
    t = Table(rows, colWidths=col_widths)
    style = [
        ('FONTSIZE',      (0, 0), (-1, -1), 9),
        ('TOPPADDING',    (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING',   (0, 0), (-1, -1), 6),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID',          (0, 0), (-1, -1), 0.5, GRIS_LINEA),
    ]
    for i in range(0, len(rows), 2):
        style.append(('BACKGROUND', (0, i), (-1, i), GRIS_FONDO))
    t.setStyle(TableStyle(style))
    story.append(t)
    story.append(Spacer(1, 5 * mm))


def _grid_metricas(story, metricas):
    """Grid 2 × N de tarjetas para puntuaciones de la IA."""
    estilos = _estilos()
    cell_w = CONTENT_W / 2 - 2 * mm
    rows = []
    row = []
    for label, valor_txt, color in metricas:
        celda = Table([
            [Paragraph(label, estilos['etiqueta'])],
            [Paragraph(valor_txt, ParagraphStyle(
                'mv', fontSize=15, fontName='Helvetica-Bold',
                textColor=color, alignment=TA_CENTER))],
        ], colWidths=[cell_w])
        celda.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, -1), GRIS_FONDO),
            ('BOX',           (0, 0), (-1, -1), 0.8, GRIS_LINEA),
            ('TOPPADDING',    (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ('ALIGN',         (0, 0), (-1, -1), 'CENTER'),
        ]))
        row.append(celda)
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row + [''])

    t = Table(rows, colWidths=[cell_w, cell_w], hAlign='CENTER')
    t.setStyle(TableStyle([
        ('TOPPADDING',    (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING',   (0, 0), (-1, -1), 2),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 2),
    ]))
    story.append(t)
    story.append(Spacer(1, 4 * mm))


def _barra_progreso(story, estilos, label, valor, maximo, color=AZUL_CLARO):
    """Fila con barra de progreso proporcional al valor/maximo."""
    label_w = 55 * mm
    valor_w = 18 * mm
    barra_total = CONTENT_W - label_w - valor_w - 4 * mm
    pct      = min(valor / maximo, 1.0)
    fill_w   = max(barra_total * pct, 0.5)
    empty_w  = max(barra_total - fill_w, 0.5)

    fill_cell  = Table([['']], colWidths=[fill_w],  rowHeights=[7])
    empty_cell = Table([['']], colWidths=[empty_w], rowHeights=[7])
    fill_cell.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), color)]))
    empty_cell.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), GRIS_LINEA)]))

    row = [[
        Paragraph(label, estilos['etiqueta']),
        fill_cell,
        empty_cell,
        Paragraph(f'{valor}/{maximo}', estilos['valor']),
    ]]
    t = Table(row, colWidths=[label_w, fill_w, empty_w, valor_w])
    t.setStyle(TableStyle([
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING',    (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING',   (0, 0), (-1, -1), 0),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 0),
    ]))
    story.append(t)


def _footer(story, estilos):
    story.append(Spacer(1, 8 * mm))
    story.append(HRFlowable(width='100%', thickness=0.5, color=GRIS_LINEA))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(
        'Este informe ha sido generado autom\u00e1ticamente por Tecnocasa AI Valuator mediante modelos de '
        'Machine Learning (GBR) e Inteligencia Artificial Generativa (Google Gemini). '
        'Los valores son orientativos y no constituyen una tasaci\u00f3n oficial homologada (norma ECO/805/2003). '
        'Para transacciones legales o hipotecarias, consulte con un tasador certificado.',
        estilos['disclaimer']
    ))


# ── Función pública ───────────────────────────────────────────────────────────

def crear_informe(datos_inmueble, precio_estimado, precio_m2):
    """
    Genera el PDF de tasación y devuelve los bytes listos para st.download_button.

    Parámetros
    ----------
    datos_inmueble : dict   — diccionario user_data de app.py
    precio_estimado : float — precio total estimado en euros
    precio_m2 : float       — precio por metro cuadrado estimado
    """
    buffer  = io.BytesIO()
    doc     = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=20 * mm, rightMargin=20 * mm,
        topMargin=15 * mm, bottomMargin=15 * mm,
        title='Informe de Tasacion — Tecnocasa AI',
        author='Tecnocasa AI Valuator'
    )
    estilos = _estilos()
    story   = []
    fecha   = datetime.now().strftime('%d/%m/%Y')
    d       = datos_inmueble
    si_no   = lambda v: 'Si' if v else 'No'

    # 0. Cabecera
    _header_banner(story, estilos, fecha)

    # 1. Precio central
    _bloque_precio(story, estilos, precio_estimado, precio_m2)

    # 2. Características básicas
    _titulo_seccion(story, estilos, '1.  Caracteristicas del Inmueble')
    estado_txt = {1: 'A reformar', 2: 'Bueno', 3: 'Muy bueno', 4: 'Reformado'}.get(
        int(d.get('estado_val', 2)), 'Bueno'
    )
    _tabla_detalle(story, estilos, [
        ('Zona / Localizacion',     d.get('zona', '—')),
        ('Tipo de inmueble',        d.get('tipo_inmueble', '—')),
        ('Superficie',              f"{d.get('superficie', 0)} m2"),
        ('Dormitorios',             d.get('dormitorios', 0)),
        ('Banos',                   d.get('banos', 0)),
        ('Planta',                  d.get('planta', 0)),
        ('Ano de construccion',     d.get('anio', '—')),
        ('Estado de conservacion',  f"{estado_txt}  (Nivel {d.get('estado_val', 2)}/4)"),
    ])

    # 3. Dotaciones
    _titulo_seccion(story, estilos, '2.  Dotaciones y Extras')
    _tabla_detalle(story, estilos, [
        ('Ascensor',           si_no(d.get('ascensor'))),
        ('Garaje',             si_no(d.get('garaje'))),
        ('Terraza / Balcon',   si_no(d.get('terraza'))),
        ('Piscina',            si_no(d.get('piscina'))),
        ('Portero',            si_no(d.get('portero'))),
        ('Aire acondicionado', si_no(d.get('aire'))),
        ('Amueblado',          si_no(d.get('amueblado'))),
        ('Trastero',           si_no(d.get('trastero'))),
        ('Calefaccion',        d.get('calefaccion', '—')),
        ('Tipo de suelo',      d.get('suelo', '—')),
    ])

    # 4. Calidades IA
    _titulo_seccion(story, estilos, '3.  Analisis de Calidades (IA Visual)')
    _grid_metricas(story, [
        ('Nivel de Lujo',  f"{d.get('nivel_lujo', 3.0):.1f} / 5",  AZUL_CLARO),
        ('Modernidad',     f"{d.get('nivel_modernidad', 3.0):.1f} / 5", AZUL_MEDIO),
        ('Luminosidad',    f"{d.get('calidad_iluminacion', 3.0):.1f} / 5", VERDE),
        ('Calidad Fotos',  f"{d.get('nivel_foto', 6.0):.1f} / 10", NARANJA),
    ])
    for label, val, maximo, color in [
        ('Nivel de Lujo',    d.get('nivel_lujo', 3.0),              5,  AZUL_CLARO),
        ('Modernidad',       d.get('nivel_modernidad', 3.0),        5,  AZUL_MEDIO),
        ('Luminosidad',      d.get('calidad_iluminacion', 3.0),     5,  VERDE),
        ('Calidad de Fotos', d.get('nivel_foto', 6.0),             10,  NARANJA),
    ]:
        _barra_progreso(story, estilos, label, val, maximo, color)
    story.append(Spacer(1, 5 * mm))

    # 5. Entorno
    _titulo_seccion(story, estilos, '4.  Entorno y Conectividad')
    _tabla_detalle(story, estilos, [
        ('Metro cercano',    si_no(d.get('metro'))),
        ('Renfe cercana',    si_no(d.get('renfe'))),
        ('Ruido urbano',     f"{d.get('ruido_urb', 0)} dB"),
        ('Ruido de trafico', f"{d.get('ruido_traf', 0)} dB"),
        ('Supermercados',    d.get('n_super', 0)),
        ('Restaurantes',     d.get('n_rest', 0)),
        ('Farmacias',        d.get('n_farm', 0)),
        ('Bares',            d.get('n_bar', 0)),
    ])

    # 6. Footer / Disclaimer
    _footer(story, estilos)

    doc.build(story)
    return buffer.getvalue()