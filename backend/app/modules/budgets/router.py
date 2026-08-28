from calendar import monthrange
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models import Budget, Transaction, User
from app.modules.forecasting.service import forecast

router = APIRouter(prefix="/budgets", tags=["budgets"])


class BudgetIn(BaseModel):
    category: str
    amount: float = Field(gt=0)
    month: date
    @field_validator("month")
    @classmethod
    def first_day(cls, value): return value.replace(day=1)


def status_for(budget, spent, predicted=None, largest_transaction=0):
    ratio = spent / budget.amount
    alerts = []
    if ratio >= 1: alerts.append({"level": "danger", "message": f"{budget.category} budget exceeded"})
    elif ratio >= .8: alerts.append({"level": "warning", "message": f"{budget.category} budget is {ratio:.0%} used"})
    if predicted is not None and predicted > budget.amount: alerts.append({"level": "warning", "message": f"Predicted {budget.category} spend may exceed budget"})
    remaining_before = max(0, budget.amount - spent + largest_transaction)
    if remaining_before and largest_transaction >= remaining_before * .5: alerts.append({"level": "warning", "message": f"A single {budget.category} transaction used at least 50% of the remaining budget"})
    return {"id": budget.id, "category": budget.category, "amount": budget.amount, "month": budget.month, "spent": round(spent, 2), "remaining": round(budget.amount-spent, 2), "percent_used": round(ratio*100, 1), "alerts": alerts}


@router.get("")
def list_budgets(month: date | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    month = (month or date.today()).replace(day=1); end = date(month.year, month.month, monthrange(month.year, month.month)[1])
    budgets = db.scalars(select(Budget).where(Budget.user_id == user.id, Budget.month == month)).all()
    expenses = db.scalars(select(Transaction).where(Transaction.user_id == user.id, Transaction.kind == "expense", Transaction.occurred_on.between(month, end))).all()
    totals = {}; largest = {}
    for transaction in expenses:
        totals[transaction.category] = totals.get(transaction.category, 0) + transaction.amount
        largest[transaction.category] = max(largest.get(transaction.category, 0), transaction.amount)
    predicted = forecast(db.scalars(select(Transaction).where(Transaction.user_id == user.id)).all()).get("by_category", {})
    return [status_for(b, totals.get(b.category, 0), predicted.get(b.category), largest.get(b.category, 0)) for b in budgets]


@router.post("", status_code=201)
def upsert_budget(data: BudgetIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.scalar(select(Budget).where(Budget.user_id == user.id, Budget.category == data.category, Budget.month == data.month))
    if item: item.amount = data.amount
    else: item = Budget(user_id=user.id, **data.model_dump()); db.add(item)
    db.commit(); db.refresh(item); return {"id": item.id, **data.model_dump()}


@router.delete("/{budget_id}", status_code=204)
def delete_budget(budget_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.scalar(select(Budget).where(Budget.id == budget_id, Budget.user_id == user.id))
    if not item: raise HTTPException(404, "Budget not found")
    db.delete(item); db.commit()
