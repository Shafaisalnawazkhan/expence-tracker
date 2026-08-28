from collections import defaultdict
from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models import Transaction, User

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("")
def insights(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = db.scalars(select(Transaction).where(Transaction.user_id == user.id, Transaction.kind == "expense")).all()
    by_month = defaultdict(float); by_category = defaultdict(float); current = date.today().strftime("%Y-%m")
    for item in items: by_month[item.occurred_on.strftime("%Y-%m")] += item.amount; by_category[item.category] += item.amount
    messages = []
    for category in by_category:
        current_total = sum(i.amount for i in items if i.category == category and i.occurred_on.strftime("%Y-%m") == current)
        past = defaultdict(float)
        for i in items:
            if i.category == category and i.occurred_on.strftime("%Y-%m") != current: past[i.occurred_on.strftime("%Y-%m")] += i.amount
        if past:
            avg = sum(past.values()) / len(past)
            if avg and abs(current_total-avg)/avg >= .15: messages.append(f"You spent {abs(current_total/avg-1):.0%} {'more' if current_total > avg else 'less'} on {category} this month than your historical monthly average.")
    top = max(by_category, key=by_category.get) if by_category else None
    if top: messages.insert(0, f"{top} is your top spending category overall.")
    return {"messages": messages or ["Add more transactions to unlock personalized insights."], "by_category": [{"name": k, "value": round(v, 2)} for k, v in by_category.items()], "trend": [{"month": k, "expense": round(by_month[k], 2)} for k in sorted(by_month)]}

