import os
import jwt
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from dotenv import load_dotenv

from sqlalchemy.orm import Session
from base import get_db
from models.models import User

# --- КОНФІГУРАЦІЯ ---
# load_dotenv()
#
# SECRET_KEY = os.getenv("JWT_SECRET_KEY")
# ALGORITHM = [os.getenv("JWT_ALGORITHM", "HS512")]
# ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
#
# if not SECRET_KEY:
#     raise ValueError("JWT_SECRET_KEY не встановлений")

SECRET_KEY = "12345678"
ALGORITHM = ['HS512']
ACCESS_TOKEN_EXPIRE_MINUTES = 15


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


# --- МОДЕЛІ ---

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


# --- ФУНКЦІЇ JWT ---

def generate_jwt(payload: dict, secret: str, algorithm: str = 'HS512') -> str:
    '''
    Створює JWT
    '''
    return jwt.encode(
        headers={
            "alg": algorithm,
            "typ": "JWT"
        },
        payload=payload,
        key=secret,
        algorithm=algorithm
    )


def decode_jwt(token: str, secret: str, algorithms: list = ['HS512']) -> dict:
    '''
    Декодує JWT.
    '''
    return jwt.decode(
            jwt=token,
            key=secret,
            algorithms=algorithms
    )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Створює токен із часом життя """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    return generate_jwt(to_encode, secret=SECRET_KEY, algorithm=ALGORITHM[0])


# --- ЗАЛЕЖНІСТЬ ---

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    """
    Верифікує токен, витягує ім'я користувача та знаходить його в БД.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Недійсні або прострочені дані",
        headers={"WWW-Authenticate": "Bearer"},
    )

    from app import get_user_by_username

    payload = decode_jwt(token=token)

    if payload is None:
        raise credentials_exception

    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    user = get_user_by_username(db, username)

    if user is None:
        raise credentials_exception
