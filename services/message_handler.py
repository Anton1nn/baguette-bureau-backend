# services/message_handler.py

import os
import openai
import json
from sqlalchemy.orm import Session
from database import SessionLocal
from models.client import Client
from models.product import Product
from models.processed_order import ProcessedOrder
from models.message_log import MessageLog  # Import du modèle MessageLog
from typing import Optional, Dict, Any, List
from utils.gpt_prompt import generate_prompt
from dotenv import load_dotenv

# Charger la clé API OpenAI depuis le .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def process_whatsapp_message(sender_number: str, message_text: str) -> Optional[Dict[str, Any]]:
    """
    Analyse un message WhatsApp envoyé par un client professionnel :
    - Recherche le client par numéro de téléphone.
    - Récupère la liste personnalisée de ses produits.
    - Génère un prompt pour GPT adapté à ce client.
    - Appelle l'API OpenAI pour structurer le message.
    - Archive la commande dans la base via ProcessedOrder (si commande).
    - Enregistre un log de message dans MessageLog à chaque appel.
    - Retourne le JSON structuré attendu, ou None si client non trouvé.

    :param sender_number: Numéro WhatsApp de l'expéditeur (+336xxxxxxxx)
    :param message_text: Message WhatsApp reçu
    :return: dict structuré ou None si client non trouvé ou erreur API/parsing
    """
    db: Session = SessionLocal()
    try:
        # 1. Recherche du client par numéro
        client: Optional[Client] = db.query(Client).filter(Client.phone == sender_number).first()

        # 2. Si client inexistant, on peut continuer (client_id = None)
        client_id = client.id if client else None
        
        # 3. Récupération liste produits si client connu
        product_list: List[str] = []
        if client:
            products_qs = db.query(Product).filter(Product.client_id == client.id).all()
            product_list = [p.name for p in products_qs]

        # 4. Génération prompt système
        prompt = generate_prompt(client.name if client else "client inconnu", product_list)

        # 5. Appel API OpenAI GPT
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                temperature=0.2,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": message_text}
                ]
            )
            gpt_reply = completion['choices'][0]['message']['content'].strip()

            # 6. Parsing réponse JSON
            try:
                parsed = json.loads(gpt_reply)
                if not isinstance(parsed, dict) or "is_order" not in parsed:
                    raise ValueError("Format de réponse attendu incorrect")

                # Détermine status du message selon analyse GPT
                status_val = "commande détectée" if parsed.get("is_order") else "pas une commande"

                # Sauvegarde MessageLog
                log_entry = MessageLog(
                    sender_number=sender_number,
                    message_text=message_text,
                    status=status_val,
                    client_id=client_id,
                    processed_content=json.dumps(parsed, ensure_ascii=False)
                )
                db.add(log_entry)

                # --- Archivage ProcessedOrder si commande ---
                if parsed.get("is_order"):
                    items_json = json.dumps(parsed.get("items", []), ensure_ascii=False)
                    processed_order = ProcessedOrder(
                        client_id=client_id,
                        owner_id=client.owner_id if client else None,
                        delivery_date=parsed.get("delivery_date"),
                        items=items_json,
                        pdf_path="N/A",
                        status="envoyé"
                    )
                    db.add(processed_order)

                db.commit()
                return parsed

            except Exception as parse_err:
                # Parsing JSON raté
                log_entry = MessageLog(
                    sender_number=sender_number,
                    message_text=message_text,
                    status="erreur GPT",
                    client_id=client_id,
                    processed_content=f"Parsing error: {str(parse_err)}; raw reply: {gpt_reply}"
                )
                db.add(log_entry)
                db.commit()
                return {
                    "is_order": False,
                    "error": "Réponse inattendue de GPT (voir logs)."
                }
        except Exception as api_err:
            # Erreur appel API OpenAI
            log_entry = MessageLog(
                sender_number=sender_number,
                message_text=message_text,
                status="erreur GPT",
                client_id=client_id,
                processed_content=f"API error: {str(api_err)}"
            )
            db.add(log_entry)
            db.commit()
            return {
                "is_order": False,
                "error": "Erreur d'appel à l'API OpenAI."
            }
    finally:
        db.close()

# Exemple pour test local
if __name__ == "__main__":
    res = process_whatsapp_message("+33612345678", "Je voudrais 12 baguettes pour mercredi prochain")
    print(res)