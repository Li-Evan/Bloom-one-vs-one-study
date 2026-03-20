from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, CreditTransaction
from app.auth import get_current_user
from app.schemas import CreditBalanceResponse, CreditTransactionResponse

router = APIRouter(prefix="/api/credits", tags=["credits"])


def deduct_credits(db: Session, user: User, amount: float, description: str) -> CreditTransaction:
    if user.credits < amount:
        raise HTTPException(status_code=402, detail=f"积分不足，当前余额 {user.credits}，需要 {amount}")

    user.credits -= amount
    tx = CreditTransaction(
        user_id=user.id,
        amount=-amount,
        balance_after=user.credits,
        type="chat_deduction",
        description=description,
    )
    db.add(tx)
    return tx


@router.get("/balance", response_model=CreditBalanceResponse)
def get_balance(user: User = Depends(get_current_user)):
    return CreditBalanceResponse(credits=user.credits)


@router.get("/history", response_model=list[CreditTransactionResponse])
def get_history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    txs = (
        db.query(CreditTransaction)
        .filter(CreditTransaction.user_id == user.id)
        .order_by(CreditTransaction.created_at.desc())
        .limit(50)
        .all()
    )
    return txs
