from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models import Transaction, User
from app.modules.forecasting.service import forecast

router = APIRouter(prefix="/forecasting", tags=["forecasting"])


@router.get("/next-month")
def next_month(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return forecast(db.scalars(select(Transaction).where(Transaction.user_id == user.id)).all())

