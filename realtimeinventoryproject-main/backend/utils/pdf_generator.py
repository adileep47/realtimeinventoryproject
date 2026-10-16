import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

def generate_pdf_report(report_type, data):
    """
    Generates downloadable PDF files using ReportLab.
    report_type: 'products' | 'stock' | 'low_stock'
    data: list of dicts or records
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=15
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        fontName='Helvetica-Bold',
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#334155')
    )

    alert_cell_style = ParagraphStyle(
        'AlertCell',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#dc2626')
    )

    elements = []
    generated_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

    if report_type == 'products':
        title_text = "Master Product Inventory Report"
        subtitle_text = f"Generated on {generated_at} | Total Products: {len(data)}"
        headers = ["SKU", "Product Name", "Category", "Supplier", "Price ($)", "Qty", "Reorder"]
        col_widths = [80, 150, 80, 80, 50, 40, 45]
        
        table_data = [[Paragraph(h, table_header_style) for h in headers]]
        for p in data:
            row = [
                Paragraph(str(p.get('sku', '')), table_cell_style),
                Paragraph(str(p.get('name', '')), table_cell_style),
                Paragraph(str(p.get('category_name', '')), table_cell_style),
                Paragraph(str(p.get('supplier_name', '')), table_cell_style),
                Paragraph(f"{p.get('price', 0):.2f}", table_cell_style),
                Paragraph(str(p.get('quantity', 0)), alert_cell_style if p.get('is_low_stock') else table_cell_style),
                Paragraph(str(p.get('reorder_level', 0)), table_cell_style),
            ]
            table_data.append(row)

    elif report_type == 'low_stock':
        title_text = "Low Stock Warning Report"
        subtitle_text = f"Generated on {generated_at} | Items requiring immediate reorder: {len(data)}"
        headers = ["SKU", "Product Name", "Category", "Supplier", "Current Stock", "Reorder Level", "Deficit"]
        col_widths = [80, 160, 85, 85, 55, 60, 45]
        
        table_data = [[Paragraph(h, table_header_style) for h in headers]]
        for p in data:
            deficit = max(0, p.get('reorder_level', 0) - p.get('quantity', 0))
            row = [
                Paragraph(str(p.get('sku', '')), table_cell_style),
                Paragraph(str(p.get('name', '')), table_cell_style),
                Paragraph(str(p.get('category_name', '')), table_cell_style),
                Paragraph(str(p.get('supplier_name', '')), table_cell_style),
                Paragraph(str(p.get('quantity', 0)), alert_cell_style),
                Paragraph(str(p.get('reorder_level', 0)), table_cell_style),
                Paragraph(str(deficit), alert_cell_style),
            ]
            table_data.append(row)

    elif report_type == 'stock':
        title_text = "Stock Movement History Report"
        subtitle_text = f"Generated on {generated_at} | Logged Movements: {len(data)}"
        headers = ["Date & Time", "SKU", "Product Name", "Type", "Qty", "Reason", "Logged By"]
        col_widths = [95, 75, 125, 40, 35, 105, 50]
        
        table_data = [[Paragraph(h, table_header_style) for h in headers]]
        for m in data:
            m_type = m.get('type', '')
            type_style = alert_cell_style if m_type == 'OUT' else table_cell_style
            row = [
                Paragraph(str(m.get('timestamp', '')[:16].replace('T', ' ')), table_cell_style),
                Paragraph(str(m.get('product_sku', '')), table_cell_style),
                Paragraph(str(m.get('product_name', '')), table_cell_style),
                Paragraph(m_type, type_style),
                Paragraph(str(m.get('quantity', 0)), table_cell_style),
                Paragraph(str(m.get('reason', '')), table_cell_style),
                Paragraph(str(m.get('username', '')), table_cell_style),
            ]
            table_data.append(row)
    else:
        title_text = "Inventory Report"
        subtitle_text = f"Generated on {generated_at}"
        table_data = [[Paragraph("No data", table_cell_style)]]
        col_widths = [500]

    elements.append(Paragraph(title_text, title_style))
    elements.append(Paragraph(subtitle_text, subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceAfter=15))

    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    
    elements.append(t)
    doc.build(elements)
    
    buffer.seek(0)
    return buffer
