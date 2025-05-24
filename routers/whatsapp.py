from fastapi import APIRouter, Depends, HTTPException, status
from routers.auth import get_current_user
from services.venom_bot_service import get_qr_code, get_whatsapp_status

router = APIRouter()

@router.get("/whatsapp/qrcode")
async def whatsapp_qrcode(current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non authentifié"
        )
    try:
        qr = get_qr_code(user_id)
        if not qr:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="QR code non disponible"
            )
        return {"qr": qr}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/whatsapp/status")
async def whatsapp_status(current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non authentifié"
        )
    try:
        status_str = get_whatsapp_status(user_id)
        return {"status": status_str}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )