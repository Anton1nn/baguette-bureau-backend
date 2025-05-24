import os
from typing import List, Dict
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

def generate_order_pdf(client_name: str, items: List[Dict], delivery_date: str, order_id: int) -> str:
    # Crée le dossier generated_pdfs s'il n'existe pas
    output_dir = os.path.abspath("generated_pdfs")
    os.makedirs(output_dir, exist_ok=True)

    filename = f"commande_{order_id}.pdf"
    filepath = os.path.join(output_dir, filename)

    # Création document PDF
    doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)

    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]
    heading_style = styles["Heading1"]
    heading_style.alignment = 1  # centré

    elements = []

    # Titre
    elements.append(Paragraph(f"Commande N° {order_id}", heading_style))
    elements.append(Spacer(1, 12))

    # Infos client et date livraison
    info_style = ParagraphStyle(name="InfoStyle", parent=normal_style, fontSize=12, leading=15)
    elements.append(Paragraph(f"<b>Client :</b> {client_name}", info_style))
    elements.append(Paragraph(f"<b>Date de livraison :</b> {delivery_date}", info_style))
    elements.append(Spacer(1, 20))

    # Tableau des articles
    data = [["Produit", "Quantité"]]
    for item in items:
        name = item.get("name", "")
        qty = item.get("quantity", 0)
        data.append([name, str(qty)])

    table = Table(data, colWidths=[120*mm, 40*mm], hAlign='LEFT')
    table_style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#ef9100")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 13),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),

        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#fff5d5")),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ])
    table.setStyle(table_style)

    elements.append(table)

    # Générer le pdf
    doc.build(elements)

    return filepath