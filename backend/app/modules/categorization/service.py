from pathlib import Path
import joblib
import pandas as pd

CATEGORIES = ["Food", "Transport", "Housing", "Utilities", "Shopping", "Health", "Entertainment", "Education", "Other"]
KEYWORDS = {
    "Food": ("restaurant", "cafe", "grocery", "swiggy", "zomato", "food"),
    "Transport": ("uber", "ola", "fuel", "petrol", "metro", "bus"),
    "Housing": ("rent", "mortgage", "maintenance"),
    "Utilities": ("electric", "water", "internet", "phone", "recharge"),
    "Shopping": ("amazon", "flipkart", "mall", "clothes"),
    "Health": ("hospital", "doctor", "pharmacy", "medicine"),
    "Entertainment": ("netflix", "movie", "spotify", "game"),
    "Education": ("course", "book", "tuition", "college"),
}
MODEL_PATH = Path(__file__).parents[2] / "ml" / "models" / "categorizer.joblib"


class Categorizer:
    def __init__(self):
        self.model = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None

    def predict(self, description: str, amount: float, weekday: int) -> dict:
        text = description.lower()
        match = next(((category, word) for category, words in KEYWORDS.items() for word in words if word in text), None)
        rule = match[0] if match else None
        if self.model:
            row = {"description": description, "amount_bucket": self._bucket(amount), "weekday": str(weekday)}
            probabilities = self.model.predict_proba(pd.DataFrame([row]))[0]
            index = int(probabilities.argmax())
            category, confidence = self.model.classes_[index], float(probabilities[index])
            if confidence >= 0.55:
                return {"category": category, "confidence": round(confidence, 3), "source": "random_forest", "explanation": f"The trained model matched patterns in '{description}'."}
        explanation = f"Matched the keyword '{match[1]}'." if match else "No strong pattern was found, so this was placed in Other."
        return {"category": rule or "Other", "confidence": 0.75 if rule else 0.3, "source": "keyword_fallback", "explanation": explanation}

    def reload(self):
        self.model = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None

    @staticmethod
    def _bucket(amount: float) -> str:
        return "small" if amount < 500 else "medium" if amount < 3000 else "large"


categorizer = Categorizer()
