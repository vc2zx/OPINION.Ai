from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np

from db import execute, query_one

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"


@lru_cache(maxsize=1)
def load_models():
    category_model_path = MODEL_DIR / "category_model.joblib"
    labels_path = MODEL_DIR / "category_labels.joblib"
    opinion_model_path = MODEL_DIR / "opinion_model.joblib"

    required_paths = [category_model_path, labels_path, opinion_model_path]
    missing_files = [path.name for path in required_paths if not path.exists()]

    if missing_files:
        missing = ", ".join(missing_files)
        raise RuntimeError(f"Models are missing: {missing}. Run: python train_models.py")

    category_model = joblib.load(category_model_path)
    labels = joblib.load(labels_path)
    opinion_model = joblib.load(opinion_model_path)

    if not hasattr(category_model, "named_steps"):
        raise RuntimeError("Category model must be a scikit-learn Pipeline.")

    if "tfidf" not in category_model.named_steps or "clf" not in category_model.named_steps:
        raise RuntimeError("Category model pipeline must contain 'tfidf' and 'clf' steps.")

    if not hasattr(opinion_model, "named_steps"):
        raise RuntimeError("Opinion model must be a scikit-learn Pipeline.")

    return category_model, labels, opinion_model


def predict_categories(text, threshold=0.35):
    category_model, labels, _ = load_models()

    tfidf = category_model.named_steps["tfidf"]
    clf = category_model.named_steps["clf"]

    if not hasattr(clf, "predict_proba"):
        raise RuntimeError("Category classifier must support predict_proba.")

    X = tfidf.transform([text])
    probabilities = clf.predict_proba(X)[0]

    selected = []
    for label, probability in zip(labels.classes_, probabilities):
        if probability >= threshold:
            selected.append((label, float(probability)))

    if not selected:
        best_index = int(np.argmax(probabilities))
        selected.append((labels.classes_[best_index], float(probabilities[best_index])))

    return selected


def predict_opinion(text, category):
    _, _, opinion_model = load_models()

    input_text = f"{category}: {text}"
    opinion = opinion_model.predict([input_text])[0]

    confidence = 0.0
    clf = opinion_model.named_steps["clf"] if "clf" in opinion_model.named_steps else None

    if clf is not None and hasattr(clf, "predict_proba"):
        probabilities = opinion_model.predict_proba([input_text])[0]
        confidence = float(max(probabilities))

    return opinion, confidence


def get_category_id(name):
    row = query_one("SELECT id FROM categories WHERE name = ?", (name,))

    if row:
        return row["id"]

    return execute("INSERT INTO categories (name) VALUES (?)", (name,))


def analyze_and_save(review_id, text):
    results = []

    try:
        predicted_categories = predict_categories(text)

        # Remove previous analysis results before saving the latest analysis.
        execute("DELETE FROM review_analysis WHERE review_id = ?", (review_id,))

        for category, category_confidence in predicted_categories:
            opinion, opinion_confidence = predict_opinion(text, category)
            category_id = get_category_id(category)

            # Approximate dashboard score, not a calibrated scientific probability.
            final_confidence = round((category_confidence + opinion_confidence) / 2, 3)

            execute(
                """
                INSERT INTO review_analysis
                (review_id, category_id, opinion, confidence)
                VALUES (?, ?, ?, ?)
                """,
                (review_id, category_id, opinion, final_confidence),
            )

            results.append(
                {
                    "category": category,
                    "opinion": opinion,
                    "confidence": final_confidence,
                }
            )

        execute("UPDATE reviews SET status = 'processed' WHERE id = ?", (review_id,))
        return results

    except Exception:
        execute("UPDATE reviews SET status = 'failed' WHERE id = ?", (review_id,))
        raise
