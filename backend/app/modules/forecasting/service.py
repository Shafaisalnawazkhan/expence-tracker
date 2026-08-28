from collections import defaultdict
from datetime import datetime
import math
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, root_mean_squared_error


def _next_month(month_key: str) -> int:
    month = datetime.strptime(month_key, "%Y-%m").month
    return 1 if month == 12 else month + 1


def _features(values, month_numbers, next_month_number=None):
    rows = []
    limit = len(values) + (1 if next_month_number else 0)
    for index in range(limit):
        month = next_month_number if index == len(values) else month_numbers[index]
        history = values[max(0, index - 3):index]
        rolling = float(np.mean(history)) if history else float(values[0])
        rows.append([index, rolling, math.sin(2 * math.pi * month / 12), math.cos(2 * math.pi * month / 12)])
    return np.asarray(rows)


def forecast(transactions) -> dict:
    monthly = defaultdict(float); categories = defaultdict(lambda: defaultdict(float)); recurring = {}
    for item in transactions:
        if item.kind != "expense": continue
        key = item.occurred_on.strftime("%Y-%m"); monthly[key] += item.amount; categories[item.category][key] += item.amount
        if getattr(item, "is_recurring", False): recurring[(item.category, item.description.lower())] = item.amount
    months = sorted(monthly)
    if len(months) < 4:
        return {"status": "insufficient_data", "required_months": 4, "available_months": len(months), "next_month_total": None, "by_category": {}, "recurring_floor": round(sum(recurring.values()), 2)}
    month_numbers = [int(month.split("-")[1]) for month in months]; next_number = _next_month(months[-1])

    def fit(values, recurring_floor=0):
        x_all = _features(values, month_numbers, next_number); x, next_x = x_all[:-1], x_all[-1:]
        model = LinearRegression().fit(x, values); fitted = model.predict(x)
        prediction = max(float(model.predict(next_x)[0]), recurring_floor, 0)
        metrics = {"mae": float(mean_absolute_error(values, fitted)), "rmse": float(root_mean_squared_error(values, fitted))}
        return round(prediction, 2), {key: round(value, 2) for key, value in metrics.items()}, [round(max(0, float(value)), 2) for value in fitted]

    recurring_total = sum(recurring.values()); total, metrics, fitted = fit([monthly[month] for month in months], recurring_total)
    recurring_by_category = defaultdict(float)
    for (category, _), amount in recurring.items(): recurring_by_category[category] += amount
    by_category = {category: fit([values.get(month, 0) for month in months], recurring_by_category[category])[0] for category, values in categories.items()}
    return {"status": "ready", "next_month_total": total, "by_category": by_category, "recurring_floor": round(recurring_total, 2), "features": ["month_index", "rolling_3_month_average", "seasonality_sin", "seasonality_cos", "recurring_floor"], "metrics": metrics, "history": [{"month": month, "actual": round(monthly[month], 2), "predicted": fitted[index]} for index, month in enumerate(months)]}
