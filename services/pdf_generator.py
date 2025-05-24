# services/pdf_generator.py

from typing import List, Dict, Any
from weasyprint import HTML, CSS

def generate_order_pdf(client_name: str, delivery_date: str, items: List[Dict[str, Any]]) -> bytes:
    """
    Génère un PDF représentant le bon de commande d'un client professionnel.

    Args:
        client_name (str): Nom du client professionnel.
        delivery_date (str): Date de livraison souhaitée (YYYY-MM-DD).
        items (List[Dict[str, Any]]): Liste des produits, chaque item = {"name": str, "quantity": int}

    Returns:
        bytes: Le contenu du PDF sous forme de bytes, prêt à être envoyé par mail.
    """
    # Génère le corps du tableau des produits
    table_rows = "\n".join(
        f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{item['name']}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align:center;">{item['quantity']}</td>
        </tr>
        """ for item in items
    )

    # Prépare le HTML du bon de commande
    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: "Arial", sans-serif;
                margin: 40px;
            }}
            h1 {{
                text-align: center;
                font-size: 2em;
                color: #444;
            }}
            .section {{
                margin-bottom: 24px;
            }}
            .label {{
                color: #666;
                font-size: 0.95em;
            }}
            .client-info {{
                margin-bottom: 8px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 16px;
            }}
            th, td {{
                font-size: 1em;
            }}
            th {{
                background-color: #f4f4f4;
                padding: 10px 8px;
                text-align: left;
                border-bottom: 2px solid #999;
            }}
        </style>
    </head>
    <body>
        <h1>Bon de commande</h1>
        <div class="section client-info">
            <div><span class="label">Client :</span> <strong>{client_name}</strong></div>
            <div><span class="label">Date de livraison :</span> <strong>{delivery_date}</strong></div>
        </div>
        <div class="section">
            <table>
                <thead>
                    <tr>
                        <th>Produit</th>
                        <th>Quantité</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

    # Génére le PDF en mémoire
    html = HTML(string=html_content)
    pdf_bytes = html.write_pdf()

    return pdf_bytes

# Exemple d'appel pour test
if __name__ == "__main__":
    test_items = [
        {"name": "Baguette", "quantity": 15},
        {"name": "Croissant", "quantity": 6},
        {"name": "Pain au chocolat", "quantity": 4}
    ]
    pdf_data = generate_order_pdf("Restaurant Le Soleil", "2024-07-01", test_items)
    # Pour test, écrire le fichier localement (à ne pas faire en prod)
    with open("bon_de_commande_test.pdf", "wb") as f:
        f.write(pdf_data)