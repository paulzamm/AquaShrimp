from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# Fix passlib 1.7.4 compatibility with bcrypt >= 4.0.0
_orig_hashpw = bcrypt.hashpw
bcrypt.hashpw = lambda p, s: _orig_hashpw(p[:72], s)
if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = type("about", (), {"__version__": getattr(bcrypt, "__version__", "4.0.0")})

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hashed version."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate bcrypt hash of a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token encoding the input data dictionary."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt
