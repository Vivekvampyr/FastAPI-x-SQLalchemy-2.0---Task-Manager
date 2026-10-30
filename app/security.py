from datetime import datetime, timezone, timedelta
from typing import Optional, Any
import bcrypt
import jwt

SECRET_KEY = "jigh13uigj31unv1350gbiurn432v492yvbin132079gb1vn37"
ALGORITHM = "HS256"

def hash_password(password: str):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed_bytes = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    try:
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    except ValueError:
        return False

def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str: 
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)