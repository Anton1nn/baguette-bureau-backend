# routers/processed_orders.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from database import get_async_session
from models.processed_order import ProcessedOrder
from models.client import Client
from routers.auth import get_current_user
from models.user import User

router = APIRouter()

class ProcessedOrderOut(BaseModel):
    id: int
    client_name: Optional[str]
    delivery_date: Optional[datetime]
    status: str
    pdf_path: Optional[str]
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
async def get_processed_orders(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(ProcessedOrder).where(ProcessedOrder.owner_id == user.id).order_by(ProcessedOrder.created_at.desc())
    )
    orders = result.scalars().all()

    return [
        ProcessedOrderOut(
            id=order.id,
            client_name=order.client.name if order.client else None,
            delivery_date=order.delivery_date,
            status=order.status,
            pdf_path=order.pdf_path,
            created_at=order.created_at
        )
        for order in orders
    ]
