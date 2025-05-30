from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from database import get_db
from models.client import Client
from models.user import User
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from dotenv import load_dotenv
import os

# Charger les variables d'environnement pour décoder le JWT
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Dépendance pour récupérer l'utilisateur courant
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les identifiants.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))  # "sub" correspond à notre User.id
        if user_id is None:
            raise credentials_exception
    except (JWTError, ValueError):
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise credentials_exception
    return user

# === SCHEMAS ===
class ClientBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class ClientOut(ClientBase):
    id: int
    created_at: str

    class Config:
        from_attributes = True  # Pydantic v2

# === ROUTES CRUD ===
@router.post("/clients/", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
def create_client(client: ClientCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db_client = Client(**client.dict(), owner_id=user.id)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

@router.get("/clients/", response_model=List[ClientOut])
def get_clients(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Client).filter(Client.owner_id == user.id).order_by(Client.created_at.desc()).all()

@router.put("/clients/{client_id}", response_model=ClientOut)
def update_client(
    client_id: int = Path(..., gt=0),
    client: ClientUpdate = Depends(),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    db_client = db.query(Client).filter(Client.id == client_id, Client.owner_id == user.id).first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    for key, value in client.dict(exclude_unset=True).items():
        setattr(db_client, key, value)
    db.commit()
    db.refresh(db_client)
    return db_client

@router.delete("/clients/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    db_client = db.query(Client).filter(Client.id == client_id, Client.owner_id == user.id).first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    db.delete(db_client)
    db.commit()
    return None
