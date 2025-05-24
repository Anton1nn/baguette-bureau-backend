# services/email_sender.py

import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Charger les variables d'environnement SMTP
load_dotenv()
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL")

def send_order_email(to_email: str, client_name: str, delivery_date: str, pdf_bytes: bytes):
    """
    Envoie par email un bon de commande PDF en pièce jointe à l'adresse spécifiée.

    Args:
        to_email (str): Adresse e-mail du destinataire (boulangère ou client).
        client_name (str): Nom du client professionnel.
        delivery_date (str): Date de livraison (format YYYY-MM-DD).
        pdf_bytes (bytes): PDF du bon de commande à joindre.

    Returns:
        None
    """
    # Créer le nom du fichier joint proprement (sans espaces/accents)
    safe_client = "".join(c for c in client_name if c.isalnum() or c in (' ', '_')).replace(" ", "_")
    filename = f"bon_commande_{safe_client}_{delivery_date}.pdf"
    
    # Créer le mail
    subject = f"Nouvelle commande de {client_name}"
    body = (
        f"Bonjour,\n\n"
        f"Vous venez de recevoir une nouvelle commande de la part de \"{client_name}\".\n"
        f"Date de livraison prévue : {delivery_date}\n\n"
        f"Veuillez trouver le bon de commande en pièce jointe.\n\n"
        f"Bonne journée,\nL'équipe Baguette & Bureau"
    )

    msg = EmailMessage()
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    # Ajouter la pièce jointe PDF
    msg.add_attachment(
        pdf_bytes,
        maintype="application",
        subtype="pdf",
        filename=filename
    )

    # Envoyer le mail via SMTP (STARTTLS)
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        # Logging pro à mettre ici selon la stack, pour l'instant on lève l'erreur
        raise RuntimeError(f"Erreur lors de l'envoi du mail : {e}")

# Exemple d'appel (à commenter/supprimer en prod)
if __name__ == "__main__":
    with open("example.pdf", "rb") as f:
        pdf_bytes = f.read()
    send_order_email(
        to_email="boulangerie@example.com",
        client_name="Restaurant Le Soleil",
        delivery_date="2024-07-01",
        pdf_bytes=pdf_bytes
    )