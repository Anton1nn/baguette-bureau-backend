from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from models.processed_order import ProcessedOrder
from models.user import User
from routers.auth import get_current_user

router = APIRouter()

class ProcessedOrderOut(BaseModel):
    id: int
    client_name: Optional[str] = None
    delivery_date: Optional[datetime] = None
    status: str
    pdf_path: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True

@router.get(
    "/orders/processed",
    response_model=List[ProcessedOrderOut],
    status_code=status.HTTP_200_OK,
    summary="Récupérer les commandes archivées de l'utilisateur connecté",
    tags=["Commandes archivées"]
)
def get_processed_orders(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    orders = (
        db.query(ProcessedOrder)
        .filter(ProcessedOrder.owner_id == user.id)
        .order_by(ProcessedOrder.created_at.desc())
        .all()
    )

    results = []
    for order in orders:
        client_name = order.client.name if order.client else None
        results.append(
            ProcessedOrderOut(
                id=order.id,
                client_name=client_name,
                delivery_date=order.delivery_date,
                status=order.status,
                pdf_path=order.pdf_path,
                created_at=order.created_at
            )
        )
    return results
