from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_async_session
from models.user import User  # modèle ORM
from schemas import UserOut, UserCreate, UserLogin  # les bons schémas Pydantic

router = APIRouter()

SECRET_KEY = "VOTRE_CLE_SECRETE"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# === Fonction pour obtenir l'utilisateur courant via JWT ===
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_session)
):
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


# === Route pour l'inscription ===
@router.post("/register", response_model=UserOut)
async def register(user: UserCreate, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    new_user = User(name=user.name, email=user.email, password=user.password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return UserOut(id=new_user.id, name=new_user.name, email=new_user.email)


# === Route pour le login ===
@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(User).where(User.email == user.email))
    db_user = result.scalar_one_or_none()
    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=401, detail="Identifiants invalides")

    token = jwt.encode({"sub": str(db_user.id)}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}
