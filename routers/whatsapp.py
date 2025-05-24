from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
from services.venom_bot_service import get_qr_code, get_whatsapp_status

# Configuration du logger
logger = logging.getLogger(__name__)

# Création du routeur FastAPI
router = APIRouter()

@router.get("/whatsapp/qrcode")
async def get_whatsapp_qrcode(session_id: int) -> Dict[str, Any]:
    """
    Récupère le QR code pour une session WhatsApp donnée.
    
    Args:
        session_id (int): Identifiant de la session WhatsApp
        
    Returns:
        Dict[str, Any]: Dictionnaire contenant la clé "qr" avec le QR code
        
    Raises:
        HTTPException: En cas d'erreur lors de la récupération du QR code
    """
    try:
        logger.info(f"Récupération du QR code pour la session {session_id}")
        qr_code = await get_qr_code(session_id)
        
        if qr_code is None:
            logger.warning(f"Aucun QR code disponible pour la session {session_id}")
            raise HTTPException(
                status_code=404, 
                detail=f"QR code non disponible pour la session {session_id}"
            )
        
        logger.info(f"QR code récupéré avec succès pour la session {session_id}")
        return {"qr": qr_code}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du QR code pour la session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur interne lors de la récupération du QR code: {str(e)}"
        )

@router.get("/whatsapp/status")
async def get_whatsapp_session_status(session_id: int) -> Dict[str, Any]:
    """
    Récupère le statut d'une session WhatsApp donnée.
    
    Args:
        session_id (int): Identifiant de la session WhatsApp
        
    Returns:
        Dict[str, Any]: Dictionnaire contenant la clé "status" avec le statut de la session
        
    Raises:
        HTTPException: En cas d'erreur lors de la récupération du statut
    """
    try:
        logger.info(f"Récupération du statut pour la session {session_id}")
        status = await get_whatsapp_status(session_id)
        
        if status is None:
            logger.warning(f"Aucun statut disponible pour la session {session_id}")
            raise HTTPException(
                status_code=404, 
                detail=f"Statut non disponible pour la session {session_id}"
            )
        
        logger.info(f"Statut récupéré avec succès pour la session {session_id}: {status}")
        return {"status": status}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du statut pour la session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur interne lors de la récupération du statut: {str(e)}"
        )
