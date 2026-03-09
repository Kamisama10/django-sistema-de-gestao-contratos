# utils/exportar.py

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from openpyxl import Workbook
from openpyxl.styles import (
    Font, PatternFill, Alignment, Border, Side, numbers
)
from openpyxl.utils import get_column_letter
from django.http import HttpResponse
from datetime import date
import io


# ── Cores Vale ────────────────────────────────────────────────────────────────
VALE_BLUE  = colors.HexColor('#003087')
VALE_GREEN = colors.HexColor('#00703c')
CINZA      = colors.HexColor('#f8f9fc')
CINZA_BORDA= colors.HexColor('#eef0f5')
BRANCO     = colors.white
VERMELHO   = colors.HexColor('#dc2626')
AMARELO    = colors.HexColor('#d97706')


def _header_pdf(canvas, doc, titulo, subtitulo=''):
    """Cabeçalho padrão Vale em todas as páginas."""
    canvas.saveState()
    w, h = doc.pagesize

    # Faixa azul
    canvas.setFillColor(VALE_BLUE)
    canvas.rect(0, h - 52, w, 52, fill=1, stroke=0)

    # Logo / título
    canvas.setFillColor(BRANCO)
    canvas.setFont('Helvetica-Bold', 16)
    canvas.drawString(1.5*cm, h - 34, 'VALE')
    canvas.setFont('Helvetica', 10)
    canvas.drawString(3.2*cm, h - 30, '|  Gestão de Contratos')

    # Título do relatório
    canvas.setFont('Helvetica-Bold', 11)
    canvas.drawRightString(w - 1.5*cm, h - 26, titulo)
    if subtitulo:
        canvas.setFont('Helvetica', 9)
        canvas.drawRightString(w - 1.5*cm, h - 38, subtitulo)

    # Linha verde
    canvas.setFillColor(VALE_GREEN)
    canvas.rect(0, h - 56, w, 4, fill=1, stroke=0)

    # Rodapé
    canvas.setFillColor(colors.HexColor('#6b7280'))
    canvas.setFont('Helvetica', 8)
    canvas.drawString(1.5*cm, 0.6*cm,
        f'Gerado em {date.today().strftime("%d/%m/%Y")}  —  Vale S.A.')
    canvas.drawRightString(w - 1.5*cm, 0.6*cm,
        f'Pág. {canvas.getPageNumber()}')

    canvas.restoreState()


# ══════════════════════════════════════════════════════════════════════════════
# PDF — DRE Mensal
# ══════════════════════════════════════════════════════════════════════════════
def pdf_dre(contrato, mes, medicoes, gastos_por_categoria,
            fat_bruto, fat_glosa, fat_retencao, fat_liquido,
            total_gastos, margem, margem_pct,
            fat_acumulado, gastos_acumulado,
            margem_acumulada, margem_acumulada_pct):

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=2.2*cm, bottomMargin=1.5*cm
    )

    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        'titulo', fontSize=13, fontName='Helvetica-Bold',
        textColor=VALE_BLUE, spaceAfter=4
    )
    sub_style = ParagraphStyle(
        'sub', fontSize=9, fontName='Helvetica',
        textColor=colors.HexColor('#6b7280'), spaceAfter=12
    )
    secao_style = ParagraphStyle(
        'secao', fontSize=10, fontName='Helvetica-Bold',
        textColor=VALE_BLUE, spaceBefore=12, spaceAfter=6
    )

    story = []

    # Cabeçalho do documento
    story.append(Paragraph(
        f'DRE Mensal — {contrato.numero_sap}', titulo_style
    ))
    story.append(Paragraph(
        f'{contrato.empresa.razao_social}  ·  Competência: {mes.strftime("%m/%Y")}',
        sub_style
    ))
    story.append(HRFlowable(width='100%', color=CINZA_BORDA, thickness=1))
    story.append(Spacer(1, 0.3*cm))

    # KPIs acumulados
    story.append(Paragraph('Resumo Acumulado do Contrato', secao_style))
    kpi_data = [
        ['Faturamento Acumulado', 'Gastos Acumulados',
         'Margem Acumulada', 'Margem %'],
        [
            f'R$ {fat_acumulado:,.2f}',
            f'R$ {gastos_acumulado:,.2f}',
            f'R$ {margem_acumulada:,.2f}',
            f'{margem_acumulada_pct}%',
        ]
    ]
    kpi_table = Table(kpi_data, colWidths=[4.3*cm]*4)
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), VALE_BLUE),
        ('TEXTCOLOR',  (0,0), (-1,0), BRANCO),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,0), 9),
        ('BACKGROUND', (0,1), (-1,1), CINZA),
        ('FONTNAME',   (0,1), (-1,1), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,1), (-1,1), 11),
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,1), [CINZA]),
        ('GRID',       (0,0), (-1,-1), 0.5, CINZA_BORDA),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('ROUNDEDCORNERS', [4]),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 0.4*cm))

    # DRE do mês
    story.append(Paragraph(f'DRE — {mes.strftime("%m/%Y")}', secao_style))

    dre_data = [['Descrição', 'Valor (R$)']]

    dre_data.append(['(+) Faturamento Bruto', f'{fat_bruto:,.2f}'])
    if fat_glosa > 0:
        dre_data.append(['(-) Glosas', f'({fat_glosa:,.2f})'])
    if fat_retencao > 0:
        dre_data.append(['(-) Retenções', f'({fat_retencao:,.2f})'])
    dre_data.append(['(=) Faturamento Líquido', f'{fat_liquido:,.2f}'])
    dre_data.append(['', ''])

    for cat, valor in gastos_por_categoria.items():
        dre_data.append([f'(-) {cat}', f'({valor:,.2f})'])
    dre_data.append(['(=) Total de Gastos', f'({total_gastos:,.2f})'])
    dre_data.append(['', ''])
    dre_data.append([
        f'(=) MARGEM BRUTA  ({margem_pct}%)',
        f'{margem:,.2f}'
    ])

    dre_table = Table(dre_data, colWidths=[13*cm, 4.5*cm])
    dre_style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), VALE_BLUE),
        ('TEXTCOLOR',  (0,0), (-1,0), BRANCO),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 9),
        ('ALIGN',      (1,0), (1,-1), 'RIGHT'),
        ('GRID',       (0,0), (-1,-1), 0.3, CINZA_BORDA),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [BRANCO, CINZA]),
    ])

    # Destaca linha de faturamento líquido
    liq_idx = 3 if fat_glosa > 0 else (2 if fat_retencao > 0 else 1)
    dre_style.add('FONTNAME', (0, liq_idx), (-1, liq_idx), 'Helvetica-Bold')
    dre_style.add('BACKGROUND', (0, liq_idx), (-1, liq_idx),
                  colors.HexColor('#e6f4ed'))

    # Destaca margem final
    last = len(dre_data) - 1
    cor_margem = colors.HexColor('#e6f4ed') if margem >= 0 \
                 else colors.HexColor('#fee2e2')
    dre_style.add('BACKGROUND', (0, last), (-1, last), cor_margem)
    dre_style.add('FONTNAME',   (0, last), (-1, last), 'Helvetica-Bold')
    dre_style.add('FONTSIZE',   (0, last), (-1, last), 10)

    dre_table.setStyle(dre_style)
    story.append(dre_table)
    story.append(Spacer(1, 0.4*cm))

    # Tabela de medições
    if medicoes:
        story.append(Paragraph('Medições do Mês', secao_style))
        med_data = [['BM', 'Status', 'Valor Bruto', 'Glosa', 'Valor Líquido', 'NF']]
        for m in medicoes:
            med_data.append([
                f'BM-{m.numero:03d}',
                m.get_status_display(),
                f'R$ {m.valor_bruto:,.2f}',
                f'R$ {m.valor_glosa:,.2f}',
                f'R$ {m.valor_liquido:,.2f}',
                m.numero_nf or '—',
            ])
        med_table = Table(med_data,
            colWidths=[2*cm, 2.5*cm, 3.2*cm, 3*cm, 3.2*cm, 3.6*cm])
        med_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), VALE_BLUE),
            ('TEXTCOLOR',  (0,0), (-1,0), BRANCO),
            ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',   (0,0), (-1,-1), 8),
            ('ALIGN',      (2,1), (4,-1), 'RIGHT'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [BRANCO, CINZA]),
            ('GRID', (0,0), (-1,-1), 0.3, CINZA_BORDA),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(med_table)

    def _header(c, d):
        _header_pdf(c, d,
            titulo=f'DRE — {contrato.numero_sap}',
            subtitulo=f'Competência: {mes.strftime("%m/%Y")}')

    doc.build(story, onFirstPage=_header, onLaterPages=_header)
    buf.seek(0)
    return buf


# ══════════════════════════════════════════════════════════════════════════════
# PDF — Quadro de Mobilização
# ══════════════════════════════════════════════════════════════════════════════
def pdf_mobilizacao(contrato, cargos, colaboradores):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=2.2*cm, bottomMargin=1.5*cm
    )

    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        'titulo', fontSize=13, fontName='Helvetica-Bold',
        textColor=VALE_BLUE, spaceAfter=4
    )
    sub_style = ParagraphStyle(
        'sub', fontSize=9, fontName='Helvetica',
        textColor=colors.HexColor('#6b7280'), spaceAfter=12
    )
    secao_style = ParagraphStyle(
        'secao', fontSize=10, fontName='Helvetica-Bold',
        textColor=VALE_BLUE, spaceBefore=12, spaceAfter=6
    )

    story = []

    story.append(Paragraph(
        f'Quadro de Mobilização — {contrato.numero_sap}', titulo_style
    ))
    story.append(Paragraph(
        f'{contrato.empresa.razao_social}  ·  '
        f'Emitido em {date.today().strftime("%d/%m/%Y")}',
        sub_style
    ))
    story.append(HRFlowable(width='100%', color=CINZA_BORDA, thickness=1))
    story.append(Spacer(1, 0.3*cm))

    # Quadro mínimo
    story.append(Paragraph('Quadro Mínimo Obrigatório', secao_style))
    cargo_data = [['Função / Cargo', 'CBO', 'Mínimo', 'Ativos', 'Situação']]
    for c in cargos:
        situacao = {
            'ok':      'Regular',
            'alerta':  f'Déficit {c.deficit}',
            'critico': f'CRÍTICO — Déficit {c.deficit}',
        }.get(c.situacao, '—')
        cargo_data.append([
            c.funcao + (' ★' if c.is_critico else ''),
            c.cbo or '—',
            str(c.quantidade_minima),
            str(c.total_ativos),
            situacao,
        ])

    cargo_table = Table(cargo_data,
        colWidths=[6.5*cm, 2*cm, 1.8*cm, 1.8*cm, 5.4*cm])
    cargo_style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), VALE_BLUE),
        ('TEXTCOLOR',  (0,0), (-1,0), BRANCO),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 8),
        ('ALIGN',      (2,0), (3,-1), 'CENTER'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [BRANCO, CINZA]),
        ('GRID', (0,0), (-1,-1), 0.3, CINZA_BORDA),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ])
    # Colorir linhas críticas
    for i, c in enumerate(cargos, start=1):
        if c.situacao == 'critico':
            cargo_style.add('BACKGROUND', (0,i), (-1,i),
                            colors.HexColor('#fee2e2'))
            cargo_style.add('FONTNAME', (0,i), (-1,i), 'Helvetica-Bold')
        elif c.situacao == 'alerta':
            cargo_style.add('BACKGROUND', (0,i), (-1,i),
                            colors.HexColor('#fef3c7'))

    cargo_table.setStyle(cargo_style)
    story.append(cargo_table)
    story.append(Spacer(1, 0.4*cm))

    # Lista de colaboradores
    story.append(Paragraph('Colaboradores Mobilizados', secao_style))
    colab_data = [[
        'Nome', 'CPF', 'Matrícula', 'Função', 'Mobilização', 'Status'
    ]]
    for col in colaboradores:
        colab_data.append([
            col.nome_completo,
            col.cpf,
            col.matricula_empresa or '—',
            col.funcao,
            col.data_mobilizacao.strftime('%d/%m/%Y'),
            col.get_status_display(),
        ])

    colab_table = Table(colab_data,
        colWidths=[4.5*cm, 2.5*cm, 2*cm, 3*cm, 2.5*cm, 2.5*cm])
    colab_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), VALE_BLUE),
        ('TEXTCOLOR',  (0,0), (-1,0), BRANCO),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [BRANCO, CINZA]),
        ('GRID', (0,0), (-1,-1), 0.3, CINZA_BORDA),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    if not colaboradores:
        story.append(Paragraph(
            'Nenhum colaborador mobilizado.', styles['Normal']
        ))
    else:
        story.append(colab_table)

    def _header(c, d):
        _header_pdf(c, d,
            titulo=f'Mobilização — {contrato.numero_sap}')

    doc.build(story, onFirstPage=_header, onLaterPages=_header)
    buf.seek(0)
    return buf


# ══════════════════════════════════════════════════════════════════════════════
# PDF — Lista de Contratos
# ══════════════════════════════════════════════════════════════════════════════
def pdf_contratos(contratos):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=landscape(A4),
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=2.2*cm, bottomMargin=1.5*cm
    )

    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        'titulo', fontSize=13, fontName='Helvetica-Bold',
        textColor=VALE_BLUE, spaceAfter=4
    )
    sub_style = ParagraphStyle(
        'sub', fontSize=9, fontName='Helvetica',
        textColor=colors.HexColor('#6b7280'), spaceAfter=12
    )

    story = []
    story.append(Paragraph('Lista de Contratos', titulo_style))
    story.append(Paragraph(
        f'Total: {len(contratos)} contrato(s)  ·  '
        f'Emitido em {date.today().strftime("%d/%m/%Y")}',
        sub_style
    ))
    story.append(HRFlowable(width='100%', color=CINZA_BORDA, thickness=1))
    story.append(Spacer(1, 0.3*cm))

    data = [[
        'Nº SAP', 'Empresa', 'Área', 'Valor Atual (R$)',
        'Início', 'Término', 'Status'
    ]]
    for c in contratos:
        data.append([
            c.numero_sap,
            c.empresa.razao_social[:35],
            c.get_area_display(),
            f'{c.valor_atual:,.0f}',
            c.data_inicio.strftime('%d/%m/%Y'),
            c.data_termino_atual.strftime('%d/%m/%Y'),
            c.get_status_display(),
        ])

    tabela = Table(data,
        colWidths=[3*cm, 8*cm, 3*cm, 3.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
    estilo = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), VALE_BLUE),
        ('TEXTCOLOR',  (0,0), (-1,0), BRANCO),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 8),
        ('ALIGN',      (3,1), (3,-1), 'RIGHT'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [BRANCO, CINZA]),
        ('GRID', (0,0), (-1,-1), 0.3, CINZA_BORDA),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ])
    # Colorir por status
    status_cores = {
        'vigente':   colors.HexColor('#dcfce7'),
        'suspenso':  colors.HexColor('#fef3c7'),
        'encerrado': colors.HexColor('#f1f5f9'),
    }
    for i, c in enumerate(contratos, start=1):
        cor = status_cores.get(c.status)
        if cor:
            estilo.add('BACKGROUND', (6,i), (6,i), cor)

    tabela.setStyle(estilo)
    story.append(tabela)

    def _header(cv, d):
        _header_pdf(cv, d, titulo='Lista de Contratos — Vale S.A.')

    doc.build(story, onFirstPage=_header, onLaterPages=_header)
    buf.seek(0)
    return buf


# ══════════════════════════════════════════════════════════════════════════════
# EXCEL — DRE Mensal
# ══════════════════════════════════════════════════════════════════════════════
def excel_dre(contrato, mes, medicoes, gastos_por_categoria,
              fat_bruto, fat_glosa, fat_retencao, fat_liquido,
              total_gastos, margem, margem_pct,
              fat_acumulado, gastos_acumulado,
              margem_acumulada, margem_acumulada_pct):

    wb = Workbook()

    # ── Estilos ──────────────────────────────────────────────────────────────
    azul_fill   = PatternFill('solid', fgColor='003087')
    verde_fill  = PatternFill('solid', fgColor='00703c')
    cinza_fill  = PatternFill('solid', fgColor='f8f9fc')
    verde_claro = PatternFill('solid', fgColor='e6f4ed')
    vermelho_cl = PatternFill('solid', fgColor='fee2e2')

    fonte_titulo  = Font(name='Arial', size=14, bold=True, color='003087')
    fonte_branca  = Font(name='Arial', size=10, bold=True, color='FFFFFF')
    fonte_header  = Font(name='Arial', size=9,  bold=True, color='FFFFFF')
    fonte_normal  = Font(name='Arial', size=9)
    fonte_bold    = Font(name='Arial', size=9,  bold=True)
    fonte_negrito_verde = Font(name='Arial', size=10, bold=True, color='00703c')
    fonte_negrito_vermelho = Font(name='Arial', size=10, bold=True, color='dc2626')

    borda = Border(
        left=Side(style='thin', color='eef0f5'),
        right=Side(style='thin', color='eef0f5'),
        top=Side(style='thin', color='eef0f5'),
        bottom=Side(style='thin', color='eef0f5'),
    )

    centro = Alignment(horizontal='center', vertical='center')
    direita = Alignment(horizontal='right', vertical='center')
    esquerda = Alignment(horizontal='left', vertical='center')

    fmt_brl = '#,##0.00'
    fmt_pct = '0.0"%"'

    # ── Aba DRE ──────────────────────────────────────────────────────────────
    ws = wb.active
    ws.title = f'DRE {mes.strftime("%m-%Y")}'
    ws.sheet_view.showGridLines = False
    ws.column_dimensions['A'].width = 32
    ws.column_dimensions['B'].width = 18
    ws.column_dimensions['C'].width = 18
    ws.column_dimensions['D'].width = 14

    # Título
    ws.merge_cells('A1:D1')
    ws['A1'] = f'DRE Mensal — {contrato.numero_sap}'
    ws['A1'].font = fonte_titulo
    ws['A1'].alignment = esquerda
    ws.row_dimensions[1].height = 28

    ws.merge_cells('A2:D2')
    ws['A2'] = (f'{contrato.empresa.razao_social}  ·  '
                f'Competência: {mes.strftime("%m/%Y")}')
    ws['A2'].font = Font(name='Arial', size=9, color='6b7280')
    ws.row_dimensions[2].height = 16

    # Linha separadora
    ws.row_dimensions[3].height = 4
    for col in range(1, 5):
        ws.cell(3, col).fill = PatternFill('solid', fgColor='003087')

    # Header KPIs acumulados
    ws.row_dimensions[4].height = 6

    def _header_row(row, cols, labels):
        for i, (col, label) in enumerate(zip(cols, labels)):
            c = ws.cell(row, col, label)
            c.font = fonte_header
            c.fill = azul_fill
            c.alignment = centro
            c.border = borda

    def _val_row(row, cols, vals, fmt=None, negrito=False, fill=None):
        for col, val in zip(cols, vals):
            c = ws.cell(row, col, val)
            c.font = fonte_bold if negrito else fonte_normal
            c.alignment = direita if isinstance(val, (int, float)) else esquerda
            c.border = borda
            if fmt:
                c.number_format = fmt
            if fill:
                c.fill = fill

    # KPIs acumulados
    _header_row(5, [1,2,3,4],
        ['Faturamento Acumulado', 'Gastos Acumulados',
         'Margem Acumulada', 'Margem %'])
    ws.row_dimensions[5].height = 20
    _val_row(6, [1,2,3,4],
        [fat_acumulado, gastos_acumulado, margem_acumulada, margem_acumulada_pct/100],
        fmt=fmt_brl, negrito=True, fill=cinza_fill)
    ws.cell(6,4).number_format = fmt_pct
    ws.row_dimensions[6].height = 22

    ws.row_dimensions[7].height = 12

    # DRE
    _header_row(8, [1,2], ['Descrição', 'Valor (R$)'])
    ws.merge_cells('A8:A8')
    ws.row_dimensions[8].height = 20

    linha = 9
    def _dre_row(desc, valor, negrito=False, fill=None, cor_fonte=None):
        nonlocal linha
        c_desc = ws.cell(linha, 1, desc)
        c_val  = ws.cell(linha, 2, valor)
        f = Font(name='Arial', size=9, bold=negrito,
                 color=cor_fonte or '000000')
        c_desc.font = f
        c_val.font  = f
        c_desc.border = borda
        c_val.border  = borda
        c_val.number_format = fmt_brl
        c_val.alignment = direita
        c_desc.alignment = esquerda
        if fill:
            c_desc.fill = fill
            c_val.fill  = fill
        ws.row_dimensions[linha].height = 18
        linha += 1

    _dre_row('(+) Faturamento Bruto', fat_bruto)
    if fat_glosa > 0:
        _dre_row('(-) Glosas', -fat_glosa, cor_fonte='dc2626')
    if fat_retencao > 0:
        _dre_row('(-) Retenções', -fat_retencao, cor_fonte='dc2626')
    _dre_row('(=) Faturamento Líquido', fat_liquido,
             negrito=True, fill=verde_claro, cor_fonte='00703c')

    ws.cell(linha, 1).fill = PatternFill('solid', fgColor='f8f9fc')
    linha += 1

    for cat, valor in gastos_por_categoria.items():
        _dre_row(f'(-) {cat}', -valor, cor_fonte='dc2626')
    _dre_row('(=) Total de Gastos', -total_gastos,
             negrito=True, cor_fonte='dc2626')

    ws.cell(linha, 1).fill = PatternFill('solid', fgColor='f8f9fc')
    linha += 1

    fill_margem = verde_claro if margem >= 0 else vermelho_cl
    cor_margem  = '00703c'   if margem >= 0 else 'dc2626'
    _dre_row(f'(=) MARGEM BRUTA  ({margem_pct}%)', margem,
             negrito=True, fill=fill_margem, cor_fonte=cor_margem)

    linha += 1

    # Medições
    if medicoes:
        _header_row(linha, [1,2,3,4,5,6],
            ['BM', 'Status', 'Valor Bruto', 'Glosa', 'Valor Líquido', 'NF'])
        ws.merge_cells(f'A{linha}:A{linha}')
        ws.row_dimensions[linha].height = 20
        linha += 1
        for m in medicoes:
            for col, val in zip(
                [1,2,3,4,5,6],
                [f'BM-{m.numero:03d}', m.get_status_display(),
                 m.valor_bruto, m.valor_glosa,
                 m.valor_liquido, m.numero_nf or '—']
            ):
                c = ws.cell(linha, col, val)
                c.font = fonte_normal
                c.border = borda
                c.alignment = direita if isinstance(val, (int,float)) else esquerda
                if isinstance(val, (int, float)):
                    c.number_format = fmt_brl
            ws.row_dimensions[linha].height = 16
            linha += 1

    # ── Aba Gastos ────────────────────────────────────────────────────────────
    ws2 = wb.create_sheet('Gastos por Categoria')
    ws2.sheet_view.showGridLines = False
    ws2.column_dimensions['A'].width = 28
    ws2.column_dimensions['B'].width = 18

    ws2.merge_cells('A1:B1')
    ws2['A1'] = f'Gastos por Categoria — {mes.strftime("%m/%Y")}'
    ws2['A1'].font = fonte_titulo
    ws2.row_dimensions[1].height = 28

    for i, col in enumerate(['A','B']):
        c = ws2[f'{col}2']
        c.value = ['Categoria', 'Total (R$)'][i]
        c.font  = fonte_branca
        c.fill  = azul_fill
        c.border = borda
        c.alignment = centro
    ws2.row_dimensions[2].height = 20

    for r, (cat, val) in enumerate(gastos_por_categoria.items(), start=3):
        ws2.cell(r, 1, cat).font = fonte_normal
        ws2.cell(r, 1).border = borda
        c = ws2.cell(r, 2, val)
        c.font = fonte_normal
        c.number_format = fmt_brl
        c.alignment = direita
        c.border = borda
        if r % 2 == 0:
            ws2.cell(r,1).fill = cinza_fill
            ws2.cell(r,2).fill = cinza_fill
        ws2.row_dimensions[r].height = 16

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


# ══════════════════════════════════════════════════════════════════════════════
# EXCEL — Quadro de Mobilização
# ══════════════════════════════════════════════════════════════════════════════
def excel_mobilizacao(contrato, cargos, colaboradores):
    wb = Workbook()

    azul_fill  = PatternFill('solid', fgColor='003087')
    cinza_fill = PatternFill('solid', fgColor='f8f9fc')
    verde_fill = PatternFill('solid', fgColor='dcfce7')
    verm_fill  = PatternFill('solid', fgColor='fee2e2')
    amar_fill  = PatternFill('solid', fgColor='fef3c7')

    fonte_titulo = Font(name='Arial', size=14, bold=True, color='003087')
    fonte_header = Font(name='Arial', size=9,  bold=True, color='FFFFFF')
    fonte_normal = Font(name='Arial', size=9)
    fonte_bold   = Font(name='Arial', size=9,  bold=True)
    borda = Border(
        left=Side(style='thin', color='eef0f5'),
        right=Side(style='thin', color='eef0f5'),
        top=Side(style='thin', color='eef0f5'),
        bottom=Side(style='thin', color='eef0f5'),
    )
    centro   = Alignment(horizontal='center', vertical='center')
    esquerda = Alignment(horizontal='left',   vertical='center')

    # ── Aba Cargos ────────────────────────────────────────────────────────────
    ws = wb.active
    ws.title = 'Quadro Mínimo'
    ws.sheet_view.showGridLines = False
    ws.column_dimensions['A'].width = 28
    ws.column_dimensions['B'].width = 10
    ws.column_dimensions['C'].width = 10
    ws.column_dimensions['D'].width = 10
    ws.column_dimensions['E'].width = 20

    ws.merge_cells('A1:E1')
    ws['A1'] = f'Quadro Mínimo — {contrato.numero_sap}'
    ws['A1'].font = fonte_titulo
    ws.row_dimensions[1].height = 28

    headers = ['Função / Cargo', 'CBO', 'Mínimo', 'Ativos', 'Situação']
    for col, h in enumerate(headers, 1):
        c = ws.cell(2, col, h)
        c.font  = fonte_header
        c.fill  = azul_fill
        c.border = borda
        c.alignment = centro
    ws.row_dimensions[2].height = 20

    for r, cargo in enumerate(cargos, start=3):
        vals = [
            cargo.funcao + (' ★' if cargo.is_critico else ''),
            cargo.cbo or '—',
            cargo.quantidade_minima,
            cargo.total_ativos,
            {'ok':'Regular','alerta':f'Déficit {cargo.deficit}',
             'critico':f'CRÍTICO — Déficit {cargo.deficit}'
             }.get(cargo.situacao, '—')
        ]
        fill = (verm_fill if cargo.situacao == 'critico'
                else amar_fill if cargo.situacao == 'alerta'
                else verde_fill if cargo.situacao == 'ok'
                else cinza_fill)
        for col, val in enumerate(vals, 1):
            c = ws.cell(r, col, val)
            c.font   = fonte_bold if cargo.situacao == 'critico' else fonte_normal
            c.border = borda
            c.fill   = fill if col == 5 else (cinza_fill if r%2==0 else None)
            c.alignment = centro if col in [2,3,4] else esquerda
        ws.row_dimensions[r].height = 16

    # ── Aba Colaboradores ─────────────────────────────────────────────────────
    ws2 = wb.create_sheet('Colaboradores')
    ws2.sheet_view.showGridLines = False
    cols_w = [28, 14, 12, 20, 12, 12]
    for i, w in enumerate(cols_w, 1):
        ws2.column_dimensions[get_column_letter(i)].width = w

    ws2.merge_cells('A1:F1')
    ws2['A1'] = f'Colaboradores Mobilizados — {contrato.numero_sap}'
    ws2['A1'].font = fonte_titulo
    ws2.row_dimensions[1].height = 28

    headers2 = ['Nome', 'CPF', 'Matrícula', 'Função', 'Mobilização', 'Status']
    for col, h in enumerate(headers2, 1):
        c = ws2.cell(2, col, h)
        c.font  = fonte_header
        c.fill  = azul_fill
        c.border = borda
        c.alignment = centro
    ws2.row_dimensions[2].height = 20

    status_fill = {
        'mobilizado':    verde_fill,
        'afastado':      amar_fill,
        'ferias':        amar_fill,
        'desmobilizado': cinza_fill,
    }
    for r, col in enumerate(colaboradores, start=3):
        vals = [
            col.nome_completo, col.cpf,
            col.matricula_empresa or '—', col.funcao,
            col.data_mobilizacao.strftime('%d/%m/%Y'),
            col.get_status_display(),
        ]
        for ci, val in enumerate(vals, 1):
            c = ws2.cell(r, ci, val)
            c.font   = fonte_normal
            c.border = borda
            c.alignment = esquerda
            if ci == 6:
                c.fill = status_fill.get(col.status, cinza_fill)
            elif r % 2 == 0:
                c.fill = cinza_fill
        ws2.row_dimensions[r].height = 16

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


# ══════════════════════════════════════════════════════════════════════════════
# EXCEL — Lista de Contratos
# ══════════════════════════════════════════════════════════════════════════════
def excel_contratos(contratos):
    wb = Workbook()
    ws = wb.active
    ws.title = 'Contratos'
    ws.sheet_view.showGridLines = False

    azul_fill  = PatternFill('solid', fgColor='003087')
    cinza_fill = PatternFill('solid', fgColor='f8f9fc')
    verde_fill = PatternFill('solid', fgColor='dcfce7')
    amar_fill  = PatternFill('solid', fgColor='fef3c7')
    cinza2     = PatternFill('solid', fgColor='f1f5f9')

    fonte_titulo = Font(name='Arial', size=14, bold=True, color='003087')
    fonte_header = Font(name='Arial', size=9,  bold=True, color='FFFFFF')
    fonte_normal = Font(name='Arial', size=9)
    borda = Border(
        left=Side(style='thin',  color='eef0f5'),
        right=Side(style='thin', color='eef0f5'),
        top=Side(style='thin',   color='eef0f5'),
        bottom=Side(style='thin',color='eef0f5'),
    )
    centro   = Alignment(horizontal='center', vertical='center')
    esquerda = Alignment(horizontal='left',   vertical='center')
    direita  = Alignment(horizontal='right',  vertical='center')

    cols_w = [14, 36, 14, 18, 12, 12, 12]
    for i, w in enumerate(cols_w, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.merge_cells('A1:G1')
    ws['A1'] = 'Lista de Contratos — Vale S.A.'
    ws['A1'].font = fonte_titulo
    ws.row_dimensions[1].height = 28

    ws.merge_cells('A2:G2')
    ws['A2'] = (f'Total: {len(contratos)} contrato(s)  ·  '
                f'Emitido em {date.today().strftime("%d/%m/%Y")}')
    ws['A2'].font = Font(name='Arial', size=9, color='6b7280')
    ws.row_dimensions[2].height = 16

    headers = ['Nº SAP', 'Empresa', 'Área', 'Valor Atual (R$)',
               'Início', 'Término', 'Status']
    for col, h in enumerate(headers, 1):
        c = ws.cell(3, col, h)
        c.font  = fonte_header
        c.fill  = azul_fill
        c.border = borda
        c.alignment = centro
    ws.row_dimensions[3].height = 20

    status_fill = {
        'vigente':   verde_fill,
        'suspenso':  amar_fill,
        'encerrado': cinza2,
    }
    for r, contrato in enumerate(contratos, start=4):
        vals = [
            contrato.numero_sap,
            contrato.empresa.razao_social,
            contrato.get_area_display(),
            contrato.valor_atual,
            contrato.data_inicio.strftime('%d/%m/%Y'),
            contrato.data_termino_atual.strftime('%d/%m/%Y'),
            contrato.get_status_display(),
        ]
        for col, val in enumerate(vals, 1):
            c = ws.cell(r, col, val)
            c.font   = fonte_normal
            c.border = borda
            c.alignment = direita if col == 4 else esquerda
            if col == 4 and isinstance(val, (int, float)):
                c.number_format = '#,##0.00'
            if col == 7:
                c.fill = status_fill.get(contrato.status, cinza_fill)
                c.alignment = centro
            elif r % 2 == 0:
                c.fill = cinza_fill
        ws.row_dimensions[r].height = 16

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf