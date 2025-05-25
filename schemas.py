from typing import Optional
from pydantic import BaseModel, EmailStr

# Schéma pour la création d'utilisateur (inscription)
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

# Schéma de sortie d'utilisateur complet (par exemple dans le token ou la réponse API)
class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True  # nouvelle syntaxe Pydantic v2

# Schéma de sortie simplifié, utilisé dans les routes (ex: /register)
class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None

    class Config:
        from_attributes = True
