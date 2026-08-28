from types import SimpleNamespace
from datetime import date
from app.modules.categorization.service import Categorizer
from app.modules.forecasting.service import forecast


def test_keyword_fallback():
    service = Categorizer(); service.model = None
    result = service.predict("Uber ride home", 250, 2)
    assert result["category"] == "Transport"
    assert result["source"] == "keyword_fallback"


def test_serialized_categorizer_accepts_request_record():
    result = Categorizer().predict("monthly music subscription", 499, 2)
    assert result["category"]
    assert 0 <= result["confidence"] <= 1


def test_forecast_requires_four_months():
    rows = [SimpleNamespace(kind="expense", amount=100, category="Food", occurred_on=date(2026, month, 1)) for month in range(1, 4)]
    assert forecast(rows)["status"] == "insufficient_data"


def test_forecast_ready():
    rows = [SimpleNamespace(kind="expense", amount=month*100, category="Food", occurred_on=date(2026, month, 1)) for month in range(1, 5)]
    result = forecast(rows)
    assert result["status"] == "ready"
    assert 450 <= result["next_month_total"] <= 550
    assert "rolling_3_month_average" in result["features"]
