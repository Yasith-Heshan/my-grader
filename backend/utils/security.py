from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from typing import Optional
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from settings import settings
import hashlib

# Password hashing
# Use PBKDF2 (pbkdf2_sha256) to avoid bcrypt C-extension issues and the 72-byte limit.
# Support both pbkdf2_sha256 (default for new hashes) and bcrypt (existing hashes)
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-SHA256."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


# JWT helpers
ALGORITHM = "HS256"


def create_access_token(subject: str, role: str, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.jwt_expiration_minutes)
    expire = datetime.utcnow() + expires_delta
    to_encode = {"sub": subject, "role": role, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
