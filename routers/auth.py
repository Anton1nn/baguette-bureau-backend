from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from models.user import User
from sqlalchemy.future import select

SECRET_KEY = "VOTRE_CLE_SECRETE"
ALGORITHM = "HS256"

async def get_current_user(token: str = Depends(...), db: AsyncSession = Depends(get_async_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les identifiants",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
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
