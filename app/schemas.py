from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from .models import RoleEnum, TransactionTypeEnum

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: RoleEnum = RoleEnum.STAFF

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[RoleEnum] = None

# Inventory Schema
class ItemBase(BaseModel):
    sku: str = Field(..., min_length=3, max_length=64)
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    quantity_on_hand: int = Field(default=0, ge=0)
    reorder_point: int = Field(default=10, ge=0)

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    reorder_point: Optional[int] = Field(None, ge=0)

class ItemOut(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class StockTransactionCreate(BaseModel):
    item_id: int
    quantity: int = Field(..., gt=0, description="Quantity delta to add, subtract, or reconcile")
    type: TransactionTypeEnum
    notes: Optional[str] = None

class StockTransactionOut(BaseModel):
    id: int
    item_id: int
    user_id: int
    quantity: int
    type: TransactionTypeEnum
    notes: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True