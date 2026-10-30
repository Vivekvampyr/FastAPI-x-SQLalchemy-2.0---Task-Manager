import enum
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import String, Integer, Numeric, DateTime, ForeignKey, Enum, Text, Boolean, true
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class RoleEnum(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"

class TransactionTypeEnum(str, enum.Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True,index=True,nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true(), nullable=False)
    role: Mapped[RoleEnum] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default= lambda: datetime.now(timezone.utc))
    transactions: Mapped[List["StockTransaction"]] = relationship(back_populates="user")

class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    sku: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity_on_hand: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reorder_point: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    transactions: Mapped[List["StockTransaction"]] = relationship(back_populates="item", cascade="all, delete-orphan")

class StockTransaction(Base):
    __tablename__ = "stock_transactions"

    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[TransactionTypeEnum] = mapped_column(Enum(TransactionTypeEnum), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    item: Mapped["Item"] = relationship(back_populates="transactions")
    user: Mapped["User"] = relationship(back_populates="transactions")
