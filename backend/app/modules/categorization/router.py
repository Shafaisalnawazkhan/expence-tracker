from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Transaction, User
from app.ml.train_categorizer import train
from pydantic import BaseModel, Field
from app.dependencies import get_current_user
from app.modules.categorization.service import categorizer

router = APIRouter(prefix="/categorization", tags=["categorization"])


class PredictionIn(BaseModel):
    description: str = Field(min_length=1)
    amount: float = Field(gt=0)
    weekday: int = Field(ge=0, le=6)


@router.post("/predict")
def predict(data: PredictionIn, _=Depends(get_current_user)):
    return categorizer.predict(data.description, data.amount, data.weekday)


@router.post("/retrain")
def retrain(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    corrections = db.scalars(select(Transaction).where(Transaction.category_overridden.is_(True))).all()
    records = [{"description": item.description, "amount": item.amount, "weekday": item.occurred_on.weekday(), "category": item.category} for item in corrections]
    metrics = train(correction_records=records)
    categorizer.reload()
    return {"message": "Categorizer retrained", "corrections_used": len(records), "metrics": metrics}
