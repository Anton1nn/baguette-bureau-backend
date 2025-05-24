# utils.py

import os
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Configuration du contexte pour le hash des mots de passe avec bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash un mot de passe en utilisant bcrypt.
    :param password: Mot de passe en clair
    :return: Mot de passe hashé
    """
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """
    Vérifie qu'un mot de passe correspond à son hash.
    :param password: Mot de passe en clair
    :param hashed_password: Mot de passe hashé (récupéré de la base)
    :return: True si correspond, False sinon
    """
    return pwd_context.verify(password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Génère un JWT signé contenant les données souhaitées et une expiration.
    :param data: Données à inclure dans le JWT (claim)
    :param expires_delta: Durée avant expiration (timedelta)
    :return: JWT encodé en string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt