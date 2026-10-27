# SpamShield AI

A beginner-friendly, explainable SMS spam detector built with Python, TF-IDF, Multinomial Naive Bayes, and Streamlit.

## Features
- Classifies a message as spam or likely legitimate
- Displays a model-estimated spam score
- Explains visible warning patterns such as suspicious links, urgency, prize language, and requests for sensitive details
- Clean dashboard UI with example messages

## Setup (Windows / VS Code)

Open a terminal in this folder.

### 1. Create and activate a virtual environment (optional but recommended)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can still use the Python executable inside `.venv`, or use Command Prompt activation:
```bat
.venv\Scripts\activate.bat
```

### 2. Install packages
```powershell
python -m pip install -r requirements.txt
```

### 3. Train the model
```powershell
python train_model.py
```
The script downloads the UCI SMS Spam Collection dataset. Internet access is needed for the first training run.

### 4. Start the website
```powershell
python -m streamlit run app.py
```
Open the Local URL printed in the terminal, usually `http://localhost:8501`.

## ML concepts to explain in your interview
- **TF-IDF:** Converts text into numeric features, giving more weight to terms that are useful for distinguishing messages.
- **Multinomial Naive Bayes:** A probabilistic classifier that works well with word-frequency-style text features.
- **Train/test split:** Evaluates the model on messages it did not train on.
- **Explainability layer:** Transparent text-pattern checks provide readable clues; they are not the same as the model's prediction.

## Limitations
- Training data is an SMS dataset, so performance may differ on emails, new scam styles, and other languages.
- A message marked legitimate is not guaranteed to be safe.
- The displayed spam score is the model's estimated probability, not a security guarantee.
- The warning-signal checker uses simple patterns and can miss subtle or new scam tactics.
