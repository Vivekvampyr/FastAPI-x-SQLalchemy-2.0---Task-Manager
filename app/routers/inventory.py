from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Item, StockTransaction, TransactionTypeEnum, RoleEnum, User
from app.schemas import StockTransactionCreate, StockTransactionOut
from app.dependencies import get_current_user, RequireRoles

router = APIRouter(prefix="/api/inventory", tags=["Inventory Adjustement"])

@router.post("/transactions", response_model=StockTransactionOut, status_code=status.HTTP_201_CREATED)
def record_stock_transaction(
    trans_in: StockTransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
        item = db.get(Item, trans_in.item_id)
        if not item:
                raise HTTPException(status_code=404, detail="Item not found")
        if trans_in.type == TransactionTypeEnum.ADJUSTMENT and current_user.role not in [RoleEnum.ADMIN, RoleEnum.MANAGER]:
            raise HTTPException(status_code=403, detail="Only Managers and Admins can perform manual stock reconciliations")
        
        # Update on-hand inventory levels atomically
        if trans_in.type == TransactionTypeEnum.INBOUND:
            item.quantity_on_hand += trans_in.quantity
        elif trans_in.type == TransactionTypeEnum.OUTBOUND:
            if item.quantity_on_hand < trans_in.quantity:
                raise HTTPException(status_code=400, detail=f"Insufficient inventory. Available: {item.quantity_on_hand}")
            item.quantity_on_hand -= trans_in.quantity
        elif trans_in.type == TransactionTypeEnum.ADJUSTMENT:
            item.quantity_on_hand = trans_in.quantity
        transaction = StockTransaction(
            item_id=trans_in.item_id,
            user_id=current_user.id,
            quantity=trans_in.quantity,
            type=trans_in.type,
            notes=trans_in.notes
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction

