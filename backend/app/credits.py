from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, CreditTransaction
from app.auth import get_current_user
from app.schemas import CreditBalanceResponse, CreditTransactionResponse

router = APIRouter(prefix="/api/credits", tags=["credits"])


def deduct_credits(db: Session, user_id: int, amount: int, description: str) -> bool:
    """Atomically deduct credits. Returns True on success, False if insufficient."""
    result = db.execute(
        update(User)
        .where(User.id == user_id, User.credits >= amount)
        .values(credits=User.credits - amount)
    )
    if result.rowcount == 0:
        return False

    # Read back new balance for the transaction record
    new_balance = db.query(User.credits).filter(User.id == user_id).scalar()
    tx = CreditTransaction(
        user_id=user_id,
        amount=-amount,
        balance_after=new_balance,
        type="chat_deduction",
        description=description,
    )
    db.add(tx)
    return True


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
