from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserOut, Token
from app.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.username == user_in.username)):
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.scalar(select(User).where(User.email == user_in.email)):
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(username=user_in.username,email=user_in.email,hashed_password=hash_password(user_in.password),role=user_in.role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == form_data.username))
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    token = create_access_token(data={"sub": user.username, "role": user.role.value})
    return {"access_token": token, "token_type": "bearer"}
