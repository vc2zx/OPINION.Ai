from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MultiLabelBinarizer

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)


# Small controlled training data for a graduation project prototype.
# One review can belong to multiple categories.
CATEGORY_SAMPLES = [
    ("The food was delicious and fresh", ["Food Quality"]),
    ("Amazing burger and tasty fries", ["Food Quality"]),
    ("The chicken was cold and tasteless", ["Food Quality"]),
    ("The rice was undercooked and bad", ["Food Quality"]),
    ("The restaurant was clean and neat", ["Cleanliness"]),
    ("The tables were dirty and the place smelled bad", ["Cleanliness"]),
    ("The floor was messy and unclean", ["Cleanliness"]),
    ("The staff were friendly and helpful", ["Staff Behavior"]),
    ("The waiter was rude and ignored us", ["Staff Behavior"]),
    ("Service was fast and staff were polite", ["Staff Behavior"]),
    ("The prices were reasonable and affordable", ["Price"]),
    ("The meal was overpriced and too expensive", ["Price"]),
    ("Great food but the place was dirty", ["Food Quality", "Cleanliness"]),
    ("Food was tasty but staff were rude", ["Food Quality", "Staff Behavior"]),
    ("Clean place with affordable prices", ["Cleanliness", "Price"]),
    ("Bad service and expensive menu", ["Staff Behavior", "Price"]),
    ("Fresh food, clean place, and friendly staff", ["Food Quality", "Cleanliness", "Staff Behavior"]),
    ("Overpriced food and rude staff", ["Food Quality", "Price", "Staff Behavior"]),
    ("Good food but slow service", ["Food Quality", "Staff Behavior"]),
    ("Clean restaurant but high price", ["Cleanliness", "Price"]),
    ("The food quality was excellent", ["Food Quality"]),
    ("The restaurant cleanliness was poor", ["Cleanliness"]),
    ("Staff behavior was excellent", ["Staff Behavior"]),
    ("The price was too high", ["Price"]),
]

# Opinion model is trained on text plus category context.
OPINION_SAMPLES = [
    ("Food Quality: delicious fresh tasty excellent food", "positive"),
    ("Food Quality: amazing food good meal perfect taste", "positive"),
    ("Food Quality: cold tasteless bad burnt undercooked food", "negative"),
    ("Food Quality: average food normal taste okay meal", "neutral"),
    ("Cleanliness: clean neat hygienic organized place", "positive"),
    ("Cleanliness: dirty unclean messy bad smell tables", "negative"),
    ("Cleanliness: normal place acceptable cleanliness", "neutral"),
    ("Staff Behavior: friendly helpful polite kind staff", "positive"),
    ("Staff Behavior: rude ignored bad service unhelpful staff", "negative"),
    ("Staff Behavior: service was normal average staff", "neutral"),
    ("Price: affordable cheap reasonable good price", "positive"),
    ("Price: expensive overpriced high price too costly", "negative"),
    ("Price: normal price acceptable cost", "neutral"),
    ("Food Quality: good food but not special", "neutral"),
    ("Cleanliness: clean restaurant but tables need attention", "neutral"),
    ("Staff Behavior: slow service but staff were polite", "neutral"),
    ("Price: price was fair", "positive"),
]


def train_category_model():
    x_category = [text for text, _ in CATEGORY_SAMPLES]
    y_category_labels = [labels for _, labels in CATEGORY_SAMPLES]

    label_binarizer = MultiLabelBinarizer()
    y_category = label_binarizer.fit_transform(y_category_labels)

    category_model = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), lowercase=True)),
            ("clf", OneVsRestClassifier(LogisticRegression(max_iter=1000))),
        ]
    )

    category_model.fit(x_category, y_category)

    joblib.dump(category_model, MODEL_DIR / "category_model.joblib")
    joblib.dump(label_binarizer, MODEL_DIR / "category_labels.joblib")

    return label_binarizer


def train_opinion_model():
    x_opinion = [text for text, _ in OPINION_SAMPLES]
    y_opinion = [label for _, label in OPINION_SAMPLES]

    opinion_model = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), lowercase=True)),
            ("clf", LogisticRegression(max_iter=1000)),
        ]
    )

    opinion_model.fit(x_opinion, y_opinion)
    joblib.dump(opinion_model, MODEL_DIR / "opinion_model.joblib")


def write_training_report(label_binarizer):
    report = f"""
Training completed.

Category samples: {len(CATEGORY_SAMPLES)}
Opinion samples: {len(OPINION_SAMPLES)}
Categories: {list(label_binarizer.classes_)}

Model approach:
- Category model: TF-IDF + OneVsRest Logistic Regression
- Opinion model: TF-IDF + Logistic Regression

Important limitations:
- This is a small controlled dataset for a prototype.
- The model mainly learns keyword-based patterns.
- It is not production-ready.
- Reliable performance requires a larger real-world dataset and proper evaluation metrics.
""".strip()

    (MODEL_DIR / "training_report.txt").write_text(report, encoding="utf-8")


def main():
    label_binarizer = train_category_model()
    train_opinion_model()
    write_training_report(label_binarizer)

    print("Models trained and saved in models/")
    print("Categories:", list(label_binarizer.classes_))
    print("Training report saved to models/training_report.txt")


if __name__ == "__main__":
    main()
