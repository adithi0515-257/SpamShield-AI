from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile
from io import BytesIO

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

BASE_DIR = Path(__file__).parent
MODEL_PATH = BASE_DIR / "spam_model.joblib"
DATA_PATH = BASE_DIR / "SMSSpamCollection"
DATA_URL = "https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip"

def get_dataset():
    if DATA_PATH.exists():
        print("Using existing dataset:", DATA_PATH.name)
        return
    print("Downloading the public UCI SMS Spam Collection dataset...")
    try:
        with urlopen(DATA_URL, timeout=30) as response:
            archive_bytes = response.read()
        with ZipFile(BytesIO(archive_bytes)) as archive:
            # The archive contains a file named SMSSpamCollection.
            candidate = next((n for n in archive.namelist() if n.endswith("SMSSpamCollection")), None)
            if not candidate:
                raise FileNotFoundError("SMSSpamCollection was not found inside the downloaded archive.")
            DATA_PATH.write_bytes(archive.read(candidate))
        print("Dataset downloaded.")
    except Exception as exc:
        raise RuntimeError(
            "Dataset download failed. Check your internet connection and run python train_model.py again."
        ) from exc

def main():
    get_dataset()
    data = pd.read_csv(
        DATA_PATH,
        sep="\t",
        header=None,
        names=["label", "message"],
        encoding="utf-8",
        on_bad_lines="skip",
    )
    data = data.dropna()
    data["label"] = data["label"].str.strip().str.lower()
    data = data[data["label"].isin(["ham", "spam"])]
    data["label"] = data["label"].map({"ham": "legitimate", "spam": "spam"})

    X_train, X_test, y_train, y_test = train_test_split(
        data["message"],
        data["label"],
        test_size=0.2,
        random_state=42,
        stratify=data["label"],
    )

    model = Pipeline([
        ("tfidf", TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            max_features=30000,
            sublinear_tf=True,
        )),
        ("classifier", MultinomialNB(alpha=0.5)),
    ])

    print(f"Training on {len(X_train)} messages...")
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    print(f"\nTest accuracy: {accuracy_score(y_test, predictions):.3f}")
    print("\nClassification report:")
    print(classification_report(y_test, predictions, digits=3))

    joblib.dump(model, MODEL_PATH)
    print(f"\nSaved trained model to: {MODEL_PATH}")
    print("Now run: python -m streamlit run app.py")

if __name__ == "__main__":
    main()
