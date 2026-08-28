from datetime import date
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models import BankAccount, Transaction, User
from app.modules.categorization.service import categorizer, CATEGORIES

router = APIRouter(prefix="/transactions", tags=["transactions"])


class TransactionIn(BaseModel):
    kind: Literal["income", "expense"]
    amount: float = Field(gt=0)
    description: str = Field(default="", max_length=255)
    category: str | None = None
    occurred_on: date = Field(default_factory=date.today)
    is_recurring: bool = False
    currency: str = Field(default="INR", pattern=r"^[A-Z]{3}$")
    bank_account_id: int | None = None


def serialize(item: Transaction):
    prediction = categorizer.predict(item.description, item.amount, item.occurred_on.weekday()) if item.kind == "expense" else {"confidence": 1, "source": "user", "explanation": "Income is categorized explicitly."}
    return {"id": item.id, "kind": item.kind, "amount": item.amount, "description": item.description, "category": item.category, "predicted_category": item.predicted_category, "category_overridden": item.category_overridden, "occurred_on": item.occurred_on, "is_recurring": item.is_recurring, "currency": item.currency, "bank_account_id": item.bank_account_id, "confidence": prediction["confidence"], "categorization_source": prediction["source"], "explanation": prediction["explanation"]}


@router.get("")
def list_transactions(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = db.scalars(select(Transaction).where(Transaction.user_id == user.id).order_by(Transaction.occurred_on.desc(), Transaction.id.desc())).all()
    return [serialize(item) for item in items]


@router.post("", status_code=201)
def create_transaction(data: TransactionIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    description = data.description.strip() or (data.category or data.kind.title())
    prediction = categorizer.predict(description, data.amount, data.occurred_on.weekday()) if data.kind == "expense" else {"category": "Income"}
    category = data.category or prediction["category"]
    if data.kind == "expense" and category not in CATEGORIES: raise HTTPException(422, "Unsupported category")
    account = None
    if data.bank_account_id:
        account = db.scalar(select(BankAccount).where(BankAccount.id == data.bank_account_id, BankAccount.user_id == user.id))
        if not account: raise HTTPException(404, "Bank account not found")
        if data.kind == "expense" and account.balance < data.amount: raise HTTPException(422, "Insufficient account balance")
    values = data.model_dump(exclude={"category", "description"})
    item = Transaction(user_id=user.id, **values, description=description, category=category, predicted_category=prediction["category"], category_overridden=bool(data.category and data.category != prediction["category"]))
    db.add(item)
    if account: account.balance += data.amount if data.kind == "income" else -data.amount
    db.commit(); db.refresh(item)
    return serialize(item)


@router.put("/{transaction_id}")
def update_transaction(transaction_id: int, data: TransactionIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.scalar(select(Transaction).where(Transaction.id == transaction_id, Transaction.user_id == user.id))
    if not item: raise HTTPException(404, "Transaction not found")
    for key, value in data.model_dump(exclude={"category"}).items(): setattr(item, key, value)
    if data.category: item.category = data.category; item.category_overridden = data.category != item.predicted_category
    db.commit(); db.refresh(item); return serialize(item)


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.scalar(select(Transaction).where(Transaction.id == transaction_id, Transaction.user_id == user.id))
    if not item: raise HTTPException(404, "Transaction not found")
    if item.bank_account_id:
        account = db.scalar(select(BankAccount).where(BankAccount.id == item.bank_account_id, BankAccount.user_id == user.id))
        if account: account.balance += item.amount if item.kind == "expense" else -item.amount
    db.delete(item); db.commit(); return Response(status_code=204)
