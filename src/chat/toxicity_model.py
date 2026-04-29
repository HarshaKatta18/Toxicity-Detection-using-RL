import os
import re
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Path to store trained models
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "models")
MODELS_DIR = os.path.abspath(MODELS_DIR)
TFIDF_PATH = os.path.join(MODELS_DIR, "tfidf_vectorizer.pkl")
LOGREG_PATH = os.path.join(MODELS_DIR, "toxicity_logreg.pkl")

def _clean_text(text: str) -> str:
    """Basic cleaning for text input, including leetspeak normalization."""
    text = text.lower()
    # Normalize common numeric obfuscations so 'idi0t' becomes 'idiot'.
    text = text.translate(str.maketrans({
        "0": "o",
        "1": "i",
        "3": "e",
        "4": "a",
        "5": "s",
        "7": "t",
    }))
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

class ToxicityModel:
    def __init__(self):
        self.vectorizer = None
        self.model = None
        self._try_load()

    def _try_load(self):
        """Try to load saved model files."""
        if os.path.exists(TFIDF_PATH) and os.path.exists(LOGREG_PATH):
            self.vectorizer = joblib.load(TFIDF_PATH)
            self.model = joblib.load(LOGREG_PATH)

    def is_ready(self):
        return self.vectorizer is not None and self.model is not None

    def fit(self, texts, labels):
        """Train the model (used when preparing dataset)."""
        self.vectorizer = TfidfVectorizer(max_features=20000, ngram_range=(1, 2))
        X = self.vectorizer.fit_transform([_clean_text(t) for t in texts])
        self.model = LogisticRegression(max_iter=200)
        self.model.fit(X, labels)

        os.makedirs(MODELS_DIR, exist_ok=True)
        joblib.dump(self.vectorizer, TFIDF_PATH)
        joblib.dump(self.model, LOGREG_PATH)

    def score_proba(self, text: str) -> float:
        """Return the toxicity probability of a message."""
        if not self.is_ready():
            # simple rule fallback
            toxic_words = {"idiot", "idi0t", "stupid", "noob", "n0ob", "trash", "hate", "kill", "dumb"}
            words = set(_clean_text(text).split())
            return 0.9 if len(toxic_words & words) > 0 else 0.1

        X = self.vectorizer.transform([_clean_text(text)])
        return float(self.model.predict_proba(X)[0, 1])
