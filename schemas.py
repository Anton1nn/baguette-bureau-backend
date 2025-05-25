from typing import Optional
from pydantic import BaseModel, EmailStr, constr

# Schéma pour la création d'utilisateur (inscription)
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: constr(min_length=6)

# Schéma utilisé à la connexion (login)
class UserLogin(BaseModel):
    email: EmailStr
    password: constr(min_length=6)

# Schéma de sortie d'utilisateur complet (ex: dans un token ou une réponse API)
class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True  # Pydantic v2 syntaxe

# Schéma simplifié pour la sortie utilisateur
class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None

    class Config:
        from_attributes = True
