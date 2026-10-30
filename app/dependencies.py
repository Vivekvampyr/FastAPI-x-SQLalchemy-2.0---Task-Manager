from typing import List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.config import settings
from app.database import get_db
from app.models import User, RoleEnum
from app.schemas import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        role_str: str = payload.get("role")
        if username is None or role_str is None:
            raise credentials_exception
        token_data = TokenData(username=username, role=RoleEnum(role_str))
    except (jwt.PyJWTError, ValueError):
        raise credentials_exception
    stmt = select(User).where(User.username == token_data.username)
    user = db.scalar(stmt)
    if user is None or not user.is_active:
        raise credentials_exception
    return user

class RequireRoles:
    """Reusable RBAC dependency checking authorized user role"""
    def __init__(self, allowed_roles: List[RoleEnum]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Access Denied: Requires one of the role {[r.value for r in self.allowed_roles]}")
        return current_user