import os
import smtplib
from email.message import EmailMessage
from email.utils import make_msgid
from email.mime.application import MIMEApplication
from dotenv import load_dotenv

load_dotenv()  # charge les variables d'environnement du fichier .env

def send_order_email(to_email: str, pdf_path: str, client_name: str, delivery_date: str):
    """
    Envoie un email avec un PDF en pièce jointe via SMTP.

    Args:
        to_email (str): Adresse email du destinataire
        pdf_path (str): Chemin local vers le fichier PDF à joindre
        client_name (str): Nom du client (pour personnalisation titre + corps)
        delivery_date (str): Date de livraison format texte
    """
    # Récupération variables SMTP dans l'environnement
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = os.getenv("SMTP_PORT")
    SMTP_USERNAME = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    SMTP_FROM = os.getenv("SMTP_FROM")

    if not all([SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM]):
        raise RuntimeError("Veuillez définir toutes les variables SMTP dans le fichier .env")

    # Construction de l'email
    msg = EmailMessage()
    msg["Subject"] = f"Nouvelle commande - {client_name} pour {delivery_date}"
    msg["From"] = SMTP_FROM
    msg["To"] = to_email

    body = (
        f"Bonjour,\n\n"
        f"Veuillez trouver ci-joint le bon de commande de {client_name} "
        f"pour une livraison le {delivery_date}.\n\n"
        f"Cordialement,\n"
        f"L'équipe Baguette & Bureau"
    )
    msg.set_content(body)

    # Lecture et ajout de la pièce jointe
    try:
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()
        filename = os.path.basename(pdf_path)
        part = MIMEApplication(pdf_data, _subtype="pdf")
        part.add_header("Content-Disposition", f"attachment; filename={filename}")
        msg.attach(part)
    except FileNotFoundError:
        raise RuntimeError(f"Fichier PDF introuvable: {pdf_path}")
    except Exception as e:
        raise RuntimeError(f"Erreur lors de la lecture du PDF: {e}")

    # Envoi SMTP (TLS)
    try:
        port = int(SMTP_PORT)
        with smtplib.SMTP(SMTP_SERVER, port) as server:
            server.starttls()  # sécuriser la connexion
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
    except smtplib.SMTPException as e:
        raise RuntimeError(f"Erreur SMTP lors de l'envoi : {e}")
    except Exception as e:
        raise RuntimeError(f"Erreur inattendue lors de l'envoi : {e}")