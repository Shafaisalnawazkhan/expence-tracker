from pathlib import Path
import json
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

BASE = Path(__file__).parent
DATA_PATH = BASE / "data" / "bootstrap_transactions.csv"
MODEL_PATH = BASE / "models" / "categorizer.joblib"
METRICS_PATH = BASE / "models" / "categorizer_metrics.json"


def amount_bucket(amount):
    amount = float(amount)
    return "small" if amount < 500 else "medium" if amount < 3000 else "large"


def train(csv_path: str | None = None, correction_records: list[dict] | None = None):
    df = pd.read_csv(csv_path or DATA_PATH)
    if "amount_bucket" not in df: df["amount_bucket"] = df.amount.map(amount_bucket)
    if correction_records:
        corrected = pd.DataFrame(correction_records)
        corrected["amount_bucket"] = corrected.amount.map(amount_bucket)
        df = pd.concat([df, corrected], ignore_index=True)
    df["weekday"] = df.weekday.astype(str)
    x = df[["description", "amount_bucket", "weekday"]]
    x_train, x_test, y_train, y_test = train_test_split(x, df.category, test_size=.25, stratify=df.category, random_state=42)
    features = ColumnTransformer([("text", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1), "description"), ("meta", OneHotEncoder(handle_unknown="ignore"), ["amount_bucket", "weekday"])])
    model = Pipeline([("features", features), ("classifier", RandomForestClassifier(n_estimators=400, class_weight="balanced", max_features="sqrt", random_state=42))])
    model.fit(x_train, y_train); predicted = model.predict(x_test)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, predicted, average="weighted", zero_division=0)
    metrics = {"dataset_rows": len(df), "test_rows": len(x_test), "accuracy": round(accuracy_score(y_test, predicted), 4), "precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4)}
    MODEL_PATH.parent.mkdir(exist_ok=True); joblib.dump(model, MODEL_PATH); METRICS_PATH.write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2)); return metrics


if __name__ == "__main__": train()
