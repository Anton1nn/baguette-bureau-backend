from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional
from services.venom_bot_service import create_whatsapp_session
from services.user_service import create_user, authenticate_user, get_user_by_token


# Supposons que ces fonctions/classes existent dans votre projet
from services.user_service import create_user, authenticate_user, get_user_by_token

router = APIRouter()

class UserRegister(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None

def get_current_user(token: str = Depends(...)):
    """
    À compléter selon votre logique d'authentification.
    """
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non authentifié"
        )
    return user

@router.post("/register", response_model=UserOut)
async def register(user: UserRegister):
    # Vérifier si l'utilisateur existe déjà
    existing = create_user.get_by_email(user.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email déjà utilisé"
        )
    # Créer l'utilisateur
    new_user = create_user(
        email=user.email,
        password=user.password,
        full_name=user.full_name
    )
    # Initialiser la session WhatsApp pour ce nouvel utilisateur
    create_whatsapp_session(new_user.id)
    return UserOut(
        id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name
    )

@router.post("/login")
async def login(user: UserLogin):
    # À compléter selon votre logique d'authentification
    authenticated_user = authenticate_user(user.email, user.password)
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides"
        )
    # Retourner un token ou autre selon votre logique
    return {"token": "votre_token_ici"}