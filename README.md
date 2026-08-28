# Smart Finance Tracker

A modular final-year project combining a FastAPI finance application with an explainable Random Forest categorizer, a Linear Regression spending forecast, and auditable rule-based budget alerts.

## Quick start

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m app.ml.train_categorizer
uvicorn app.main:app --reload
```

The API is at `http://localhost:8000`, with Swagger docs at `/docs`. SQLite is the default; set `DATABASE_URL` to a PostgreSQL SQLAlchemy URL for production.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

The UI runs at `http://localhost:5173`. Register a user, add transactions, then create category budgets. The demo works even before model training because the categorizer has an explainable keyword fallback.

### Tests

```powershell
cd backend
pytest
```

## Architecture

Each backend feature owns its router and business rules under `app/modules`. Authentication is injected as a dependency. ML artifacts are trained offline and loaded once; normal prediction requests never retrain models. User category overrides are retained via `predicted_category` and `category_overridden`. The explicit retraining endpoint incorporates those confirmed corrections and reloads the saved artifact.

The forecast deliberately reports `insufficient_data` until a user has at least four distinct months of expense history. Budget alerts remain deterministic because financial thresholds should be transparent and auditable.

## Evaluation story

- Categorizer: TF-IDF description features plus amount bucket and weekday, evaluated with precision/recall/F1 by the training script.
- Forecast: interpretable linear regression over monthly time index, reporting MAE/RMSE when enough history exists.
- Alerts: explicit 80%, 100%, large-transaction, and predicted-overrun rules.
- Extensibility: new modules expose an `APIRouter` and are registered in `app/main.py`; bank ingestion, investments, voice, and i18n do not require modifying the core modules.

## Model evaluation

The included bootstrap dataset lives at `backend/app/ml/data/bootstrap_transactions.csv`. It provides a reproducible demonstration baseline; for a formal report, replace or expand it with a properly licensed public personal-finance dataset mapped to the same four columns.

```powershell
cd backend
python -m app.ml.train_categorizer
python -m app.ml.train_forecaster
```

Categorizer results are saved to `app/ml/models/categorizer_metrics.json`. Forecast MAE and RMSE appear on the dashboard once the account has at least four months of expense history.

## Docker deployment

```powershell
docker compose up --build
```

Open `http://localhost:8080`. This runs PostgreSQL, FastAPI, and the React/Nginx frontend. Change the sample database credentials and `SECRET_KEY` before deploying publicly.
