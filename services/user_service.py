import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from jose import jwt, JWTError

from models.user import User
from schemas import UserCreate, User as UserSchema

# 1. Créer un utilisateur
async def create_user(db: AsyncSession, user: UserCreate) -> UserSchema:
    # Vérifier si l'email existe déjà
    result = await db.execute(select(UserModel).where(UserModel.email == user.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise ValueError("Email déjà utilisé")
    # Hasher le mot de passe
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    # Créer le nouvel utilisateur
    db_user = UserModel(
        email=user.email,
        hashed_password=hashed_password.decode('utf-8'),
        full_name=user.full_name
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return UserSchema.from_orm(db_user)

# 2. Authentifier un utilisateur
async def authenticate_user(db: AsyncSession, email: str, password: str):
    result = await db.execute(select(UserModel).where(UserModel.email == email))
    user = result.scalar_one_or_none()
    if not user:
        return None
    if not bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8')):
        return None
    return user

# 3. Récupérer un utilisateur via un token JWT
async def get_user_by_token(db: AsyncSession, token: str, secret_key: str, algorithm: str):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        user_id = payload.get("user_id")
        if user_id is None:
            return None
    except JWTError:
        return None
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    return user