from datetime import date, datetime, timedelta
from random import randint
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models import BankAccount, Transaction, User
from app.modules.categorization.service import categorizer

router = APIRouter(prefix="/bank-accounts", tags=["bank integration"])

class ConnectIn(BaseModel):
    bank_name: str = Field(min_length=2, max_length=100)
    account_name: str = Field(default="Primary account", max_length=100)
    account_type: str = Field(default="Savings", pattern="^(Savings|Current|Credit Card)$")
    opening_balance: float = Field(default=25000, ge=0)
    currency: str = Field(default="INR", pattern=r"^[A-Z]{3}$")

def output(account):
    return {"id":account.id,"provider":account.provider,"bank_name":account.bank_name,"account_name":account.account_name,"account_type":account.account_type,"account_mask":account.account_mask,"balance":account.balance,"currency":account.currency,"status":account.status,"last_synced_at":account.last_synced_at}

@router.get("")
def list_accounts(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    return [output(account) for account in db.scalars(select(BankAccount).where(BankAccount.user_id==user.id)).all()]

@router.post("",status_code=201)
def connect(data:ConnectIn,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    account=BankAccount(user_id=user.id,provider="demo",bank_name=data.bank_name,account_name=data.account_name,account_type=data.account_type,account_mask=str(randint(1000,9999)),balance=data.opening_balance,currency=data.currency,status="connected")
    db.add(account);db.commit();db.refresh(account);return output(account)

@router.post("/{account_id}/sync")
def sync(account_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    account=db.scalar(select(BankAccount).where(BankAccount.id==account_id,BankAccount.user_id==user.id))
    if not account:raise HTTPException(404,"Bank account not found")
    samples=[("Salary credit",45000,"income",0),("Grocery supermarket",1850,"expense",2),("Metro recharge",600,"expense",5),("Electricity bill",2100,"expense",9)]
    imported=0
    for description,amount,kind,days in samples:
        external=f"demo-{account.id}-{description.lower().replace(' ','-')}"
        if db.scalar(select(Transaction).where(Transaction.external_id==external)):continue
        occurred=date.today()-timedelta(days=days);prediction=categorizer.predict(description,amount,occurred.weekday()) if kind=="expense" else {"category":"Income"}
        db.add(Transaction(user_id=user.id,kind=kind,amount=amount,description=description,category=prediction["category"],predicted_category=prediction["category"],category_overridden=False,is_recurring=description=="Salary credit",currency=account.currency,occurred_on=occurred,bank_account_id=account.id,external_id=external));imported+=1
    account.last_synced_at=datetime.utcnow();db.commit();return {"imported":imported,"account":output(account)}

@router.delete("/{account_id}")
def disconnect(account_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    account=db.scalar(select(BankAccount).where(BankAccount.id==account_id,BankAccount.user_id==user.id))
    if not account:raise HTTPException(404,"Bank account not found")
    db.delete(account);db.commit();return {"disconnected":True}
