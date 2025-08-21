"""Security module for handling JWT token creation."""
from datetime import datetime, timedelta, timezone
from jose import jwt

from app.core.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3000


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create a JWT access token with an expiration time."""
    to_encode = data.copy()
    expire = datetime\
                 .now(timezone.utc) + \
             (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
