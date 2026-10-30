from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.models import Item, RoleEnum, User
from app.schemas import ItemCreate, ItemUpdate, ItemOut
from app.dependencies import get_current_user, RequireRoles

router = APIRouter(prefix="/api/items", tags=["Items"])

@router.get("/", response_model=List[ItemOut])
def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    low_stock: Optional[bool] = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
        stmt = select(Item)
        if low_stock:
            stmt = stmt.where(Item.quantity_on_hand <= Item.reorder_point)
        return db.scalars(stmt.offset(skip).limit(limit)).all()

@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(
    item_in: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRoles([RoleEnum.ADMIN, RoleEnum.MANAGER]))):
        if db.scalar(select(Item).where(Item.sku == item_in.sku)):
            raise HTTPException(status_code=400, detail="SKU already exists")
        item = Item(**item_in.model_dump())
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

@router.patch("/{item_id}",response_model=ItemOut)
def update_item(
    item_id: int,
    item_in: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRoles([RoleEnum.ADMIN, RoleEnum.MANAGER]))):
        item = db.get(Item, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        update_data = item_in.model_dump(exclude_unset=True)
        for field, val in update_data.items():
            setattr(item, field, val)
        db.commit()
        db.refresh(item)
        return item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRoles([RoleEnum.ADMIN]))):
        item = db.get(Item, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        db.delete(item)
        db.commit()
        return None