# models/user.py

from sqlalchemy import Column, Integer, String, DateTime, func
from database import Base

class User(Base):
    """
    Modèle SQLAlchemy pour représenter un utilisateur (boulanger) dans l'application.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"
        
from pydantic import BaseModel
from typing import Optional

class UserOut(BaseModel):
    id: int
    email: str
    name: Optional[str] = None

    class Config:
        from_attributes = True  # pour Pydantic v2
