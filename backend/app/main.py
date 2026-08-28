from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine
from app.modules.auth.router import router as auth_router
from app.modules.budgets.router import router as budgets_router
from app.modules.categorization.router import router as categorization_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.forecasting.router import router as forecasting_router
from app.modules.insights.router import router as insights_router
from app.modules.transactions.router import router as transactions_router
from app.modules.bank_integration.router import router as bank_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
allowed_origins = list({settings.frontend_origin, "http://localhost:5173", "http://127.0.0.1:5173"})
app.add_middleware(CORSMiddleware, allow_origins=allowed_origins, allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(1[6-9]|2\d|3[01])\.\d+\.\d+):\d+$", allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
# Vercel Services removes the /api route prefix before forwarding a request.
# Local development still exposes the API at /api as before.
api_prefix = "" if os.getenv("VERCEL") else "/api"
for router in (auth_router, transactions_router, budgets_router, categorization_router, forecasting_router, insights_router, dashboard_router, bank_router): app.include_router(router, prefix=api_prefix)


@app.get("/health")
def health(): return {"status": "ok"}
