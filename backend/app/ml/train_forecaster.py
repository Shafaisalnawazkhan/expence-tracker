"""Evaluate the interpretable monthly Linear Regression baseline offline."""
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, root_mean_squared_error


def evaluate(monthly_totals: list[float]):
    if len(monthly_totals) < 4:
        raise ValueError("At least four months are required")
    split = len(monthly_totals) - 1
    x_train = np.arange(split).reshape(-1, 1)
    model = LinearRegression().fit(x_train, monthly_totals[:split])
    actual = monthly_totals[split:]
    predicted = model.predict(np.arange(split, len(monthly_totals)).reshape(-1, 1))
    metrics = {"mae": mean_absolute_error(actual, predicted), "rmse": root_mean_squared_error(actual, predicted)}
    print({key: round(float(value), 2) for key, value in metrics.items()})


if __name__ == "__main__":
    evaluate([12500, 13200, 12900, 14100, 14500, 14900])
