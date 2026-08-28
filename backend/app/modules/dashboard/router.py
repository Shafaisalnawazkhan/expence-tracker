from calendar import monthrange
from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models import BankAccount, Budget, Transaction, User
from app.modules.budgets.router import status_for
from app.modules.forecasting.service import forecast

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("")
def dashboard(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    start=date.today().replace(day=1);end=date(start.year,start.month,monthrange(start.year,start.month)[1])
    all_items=db.scalars(select(Transaction).where(Transaction.user_id==user.id)).all();items=[i for i in all_items if start<=i.occurred_on<=end]
    income=sum(i.amount for i in items if i.kind=="income");expense=sum(i.amount for i in items if i.kind=="expense")
    accounts=db.scalars(select(BankAccount).where(BankAccount.user_id==user.id)).all()
    unlinked_adjustment=sum(i.amount if i.kind=="income" else -i.amount for i in all_items if i.bank_account_id is None)
    available=sum(a.balance for a in accounts)+unlinked_adjustment if accounts else income-expense
    categories={};monthly={}
    for item in all_items:
        key=item.occurred_on.strftime("%Y-%m");monthly.setdefault(key,{"month":key,"income":0,"expense":0});monthly[key][item.kind]+=item.amount
    for item in items:
        if item.kind=="expense":categories[item.category]=categories.get(item.category,0)+item.amount
    prediction=forecast(all_items);budgets=db.scalars(select(Budget).where(Budget.user_id==user.id,Budget.month==start)).all();alerts=[]
    for budget in budgets:
        category_items=[i for i in items if i.kind=="expense" and i.category==budget.category]
        state=status_for(budget,sum(i.amount for i in category_items),prediction.get("by_category",{}).get(budget.category),max((i.amount for i in category_items),default=0));alerts.extend(state["alerts"])
    return {"month":start.strftime("%B %Y"),"total_income":round(income,2),"total_expenses":round(expense,2),"balance":round(available,2),"cashflow_balance":round(income-expense,2),"linked_accounts":len(accounts),"savings_rate":round((income-expense)/income*100,1) if income else 0,"by_category":[{"name":k,"value":round(v,2)} for k,v in categories.items()],"cashflow_trend":[monthly[key] for key in sorted(monthly)[-12:]],"forecast":prediction,"alerts":alerts[:6]}
