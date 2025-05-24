# routers/webhook.py

from fastapi import APIRouter, Request, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any
from fastapi.responses import JSONResponse

# Placeholder pour l'import futur de process_whatsapp_message
# from services.message_handler import process_whatsapp_message

router = APIRouter()

class WhatsAppWebhook(BaseModel):
    """
    Schéma Pydantic pour valider le corps du webhook WhatsApp.
    """
    from_: str = Field(..., alias='from', description="Numéro de l'expéditeur (ex: '+33612345678')")
    message: str = Field(..., description="Texte du message WhatsApp")

@router.post("/webhook/whatsapp", summary="Webhook WhatsApp : message entrant")
async def whatsapp_webhook(payload: WhatsAppWebhook):
    """
    Webhook appelé par UltraMsg ou Z-API à chaque message WhatsApp entrant.
    Vérifie la présence des champs nécessaires, puis transmet le message 
    à la logique de traitement (handlers externes).
    """
    sender_number = payload.from_
    message_text = payload.message

    # Vérification robuste des champs (Pydantic l'assure déjà, mais on peut ajouter des gardes si besoin)
    if not sender_number or not message_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le champ 'from' et 'message' sont obligatoires."
        )

    # Appel de la fonction (à décommenter quand elle sera disponible)
    # process_whatsapp_message(sender_number, message_text)

    # Réponse adaptée, conforme aux attentes des providers webhook
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "received",
            "from": sender_number,
            "message": message_text
        }
    )