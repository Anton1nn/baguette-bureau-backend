# routers/orders.py

from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from database import get_db
from models.order import Order, OrderStatusEnum
from models.client import Client
from models.user import User

from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

# Charger les variables d'environnement pour JWT
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
router = APIRouter()

# --------------------------------------
# Dépendance pour obtenir l'utilisateur courant via le JWT
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les identifiants.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise credentials_exception
    return user

# --------------------------------------
# Schémas Pydantic
class OrderBase(BaseModel):
    content: str = Field(..., example="10 baguettes, 5 croissants")
    delivery_date: datetime = Field(..., example="2024-07-01T08:00:00")
    status: Optional[OrderStatusEnum] = Field(default=OrderStatusEnum.en_attente)

class OrderCreate(OrderBase):
    client_id: int = Field(..., example=1)

class OrderUpdate(BaseModel):
    content: Optional[str] = None
    delivery_date: Optional[datetime] = None
    status: Optional[OrderStatusEnum] = None

class OrderOut(OrderBase):
    id: int
    client_id: int
    owner_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# --------------------------------------
# ROUTES CRUD

@router.post("/orders/", response_model=OrderOut, status_code=status.HTTP_201_CREATED, summary="Créer une commande")
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Créer une commande liée à un client existant (doit appartenir à l'utilisateur connecté).
    """
    client = db.query(Client).filter(Client.id == order.client_id, Client.owner_id == user.id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé ou non accessible")
    db_order = Order(
        content=order.content,
        delivery_date=order.delivery_date,
        status=order.status or OrderStatusEnum.en_attente,
        client_id=order.client_id,
        owner_id=user.id
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/orders/", response_model=List[OrderOut], summary="Lister toutes les commandes utilisateur")
def list_orders(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Lister toutes les commandes de l'utilisateur connecté.
    """
    orders = db.query(Order).filter(Order.owner_id == user.id).order_by(Order.delivery_date.desc()).all()
    return orders

@router.get("/orders/{order_id}", response_model=OrderOut, summary="Récupérer une commande par ID")
def get_order(
    order_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Récupérer une commande par son ID (seulement pour l'utilisateur propriétaire).
    """
    db_order = db.query(Order).filter(Order.id == order_id, Order.owner_id == user.id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    return db_order

@router.put("/orders/{order_id}", response_model=OrderOut, summary="Mettre à jour une commande")
def update_order(
    order_id: int = Path(..., gt=0),
    order_update: OrderUpdate = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Modifier une commande (seul l'utilisateur propriétaire peut modifier).
    """
    db_order = db.query(Order).filter(Order.id == order_id, Order.owner_id == user.id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    update_data = order_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_order, key, value)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Supprimer une commande")
def delete_order(
    order_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Supprimer une commande (seul l'utilisateur propriétaire peut supprimer).
    """
    db_order = db.query(Order).filter(Order.id == order_id, Order.owner_id == user.id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    db.delete(db_order)
    db.commit()
    return None