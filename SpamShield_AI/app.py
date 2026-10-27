import re
from pathlib import Path

import joblib
import streamlit as st

MODEL_PATH = Path(__file__).parent / "spam_model.joblib"

st.set_page_config(
    page_title="SpamShield AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- UI styling ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #f5f7fb; }
.block-container { padding-top: 1.7rem; max-width: 1180px; }
.hero {
    background: linear-gradient(120deg, #101b35 0%, #173d5b 60%, #087e8b 100%);
    padding: 2rem 2.2rem; border-radius: 24px; color: white;
    margin-bottom: 1.2rem; box-shadow: 0 12px 35px rgba(16, 27, 53, .12);
}
.hero h1 { font-family: 'Space Grotesk', sans-serif; font-size: 2.25rem; margin: 0; color: white; }
.hero p { color: #dce9f3; font-size: 1rem; margin: .55rem 0 0 0; }
.eyebrow { color: #73e0d1; font-weight: 700; letter-spacing: .12em; font-size: .75rem; text-transform: uppercase; }
.panel {
    background: white; padding: 1.25rem 1.35rem; border: 1px solid #e5eaf2;
    border-radius: 18px; box-shadow: 0 4px 18px rgba(16, 27, 53, .035);
}
.metric-label { color: #63718a; font-size: .82rem; font-weight: 600; }
.metric-value { color: #14213d; font-family: 'Space Grotesk', sans-serif; font-size: 1.55rem; font-weight: 700; }
.small-muted { color: #69778d; font-size: .88rem; }
div.stButton > button { border-radius: 11px; font-weight: 700; min-height: 2.7rem; }
div[data-testid="stTextArea"] textarea { border-radius: 14px; border: 1px solid #d8e0ec; }
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def find_signals(message: str):
    """Simple, transparent indicators to explain patterns; these do not replace the ML model."""
    text = message.lower()
    signals = []
    patterns = [
        (r"\b(free|winner|won|prize|reward|claim|cash|gift|lottery)\b",
         "Prize / reward language", "Words such as free, winner, prize, or claim can be used to lure a recipient."),
        (r"\b(urgent|immediately|act now|limited time|expires today|verify now)\b",
         "Urgency or pressure", "Pressure to act quickly can discourage careful checking."),
        (r"\b(password|otp|pin|bank account|credit card|verify account|login details)\b",
         "Sensitive information request", "Requests involving passwords, OTPs, PINs, or account details deserve extra caution."),
        (r"\b(click|tap|open link|visit link|call now)\b",
         "Call to action", "A request to click, call, or open something may be used to drive risky actions."),
        (r"(https?://|www\.)\S+",
         "Link detected", "Unexpected links can lead to fake login pages or malicious websites."),
        (r"(₹\s?\d+|\$\s?\d+|\b\d+\s?(?:rupees|rs|dollars)\b)",
         "Money-related wording", "Unexpected money offers or payment requests should be independently verified."),
        (r"\b(congratulations|selected|you have been chosen|act fast)\b",
         "Unexpected good-news wording", "Unsolicited claims that you have been selected or won something can be deceptive."),
    ]
    for pattern, title, explanation in patterns:
        if re.search(pattern, text):
            signals.append((title, explanation))
    if message.count("!") >= 3:
        signals.append(("Excessive exclamation marks", "Repeated punctuation can be used to create excitement or urgency."))
    if len(re.findall(r"[A-Z]", message)) >= 8 and len(message) > 20:
        signals.append(("Many uppercase letters", "Heavy use of uppercase letters may be intended to grab attention."))
    return signals

# Sidebar
with st.sidebar:
    st.markdown("## 🛡️ SpamShield AI")
    st.caption("Message safety, made explainable.")
    st.markdown("---")
    st.markdown("**How it works**")
    st.markdown("1. Clean and vectorize text with TF-IDF")
    st.markdown("2. Classify with Naive Bayes")
    st.markdown("3. Show transparent warning signals")
    st.markdown("---")
    st.caption("Built with Python · scikit-learn · Streamlit")
    st.info("A prediction is a helpful signal, not proof. Never share OTPs, passwords, or banking details.")

st.markdown("""
<div class="hero">
  <div class="eyebrow">AI MESSAGE SECURITY</div>
  <h1>Think before you click.</h1>
  <p>Analyze suspicious SMS messages with machine learning and understand the patterns that may make them risky.</p>
</div>
""", unsafe_allow_html=True)

if not MODEL_PATH.exists():
    st.error("The trained model was not found yet.")
    st.markdown("Open the VS Code terminal in this folder and run:")
    st.code("python train_model.py", language="powershell")
    st.caption("This downloads the public SMS Spam Collection dataset, trains the model, and saves spam_model.joblib.")
    st.stop()

try:
    model = joblib.load(MODEL_PATH)
except Exception as exc:
    st.error(f"Could not load the model: {exc}")
    st.stop()

st.markdown("### Message analyzer")
st.markdown('<p class="small-muted">Paste a message below, or try a sample. Your text is analyzed locally by this app.</p>', unsafe_allow_html=True)

sample_col1, sample_col2, sample_col3 = st.columns(3)
sample_spam = "Congratulations! You have won a FREE cash prize. Claim now at http://example.com"
sample_safe = "Hi, are we still meeting at the library at 4 pm? Please let me know."
sample_bank = "URGENT: Verify your bank account immediately by clicking this link."

if "message_input" not in st.session_state:
    st.session_state.message_input = ""

with sample_col1:
    if st.button("Try a spam-like message", use_container_width=True):
        st.session_state.message_input = sample_spam
with sample_col2:
    if st.button("Try a normal message", use_container_width=True):
        st.session_state.message_input = sample_safe
with sample_col3:
    if st.button("Try a phishing-style message", use_container_width=True):
        st.session_state.message_input = sample_bank

message = st.text_area(
    "Message text",
    key="message_input",
    height=155,
    placeholder="Example: Your package is waiting. Confirm your details at ...",
    help="For privacy, use sample messages or remove personal information before testing.",
)

analyze_col, clear_col = st.columns([1, 5])
with analyze_col:
    analyze = st.button("🔎 Analyze message", type="primary", use_container_width=True)
with clear_col:
    st.caption("Tip: check the sender separately. Do not click an unexpected link just to test it.")

if analyze:
    if not message.strip():
        st.warning("Please paste a message before analyzing.")
    else:
        prediction = model.predict([message])[0]
        probabilities = model.predict_proba([message])[0]
        classes = list(model.classes_)
        spam_index = classes.index("spam")
        spam_probability = float(probabilities[spam_index])
        label = "SPAM" if prediction == "spam" else "LIKELY LEGITIMATE"
        color = "#b42318" if prediction == "spam" else "#087e67"
        icon = "🚨" if prediction == "spam" else "✅"

        st.markdown("---")
        st.markdown("### Analysis result")
        result_col, confidence_col, signals_col = st.columns([1.25, 1, 1])
        with result_col:
            st.markdown(f"""
            <div class="panel">
              <div class="metric-label">MODEL CLASSIFICATION</div>
              <div style="font-size:1.55rem;font-weight:800;color:{color};margin-top:.35rem">{icon} {label}</div>
              <div class="small-muted" style="margin-top:.45rem">Based on patterns learned from labeled SMS examples.</div>
            </div>""", unsafe_allow_html=True)
        with confidence_col:
            st.markdown(f"""
            <div class="panel">
              <div class="metric-label">SPAM SCORE</div>
              <div class="metric-value">{spam_probability:.0%}</div>
              <div class="small-muted">Model-estimated probability</div>
            </div>""", unsafe_allow_html=True)
        signals = find_signals(message)
        with signals_col:
            st.markdown(f"""
            <div class="panel">
              <div class="metric-label">EXPLANATION SIGNALS</div>
              <div class="metric-value">{len(signals)}</div>
              <div class="small-muted">Patterns found in the text</div>
            </div>""", unsafe_allow_html=True)

        st.progress(spam_probability, text=f"Spam score: {spam_probability:.0%}")
        st.markdown("#### Why should you pay attention?")
        if signals:
            for title, explanation in signals:
                st.markdown(f"- **{title}:** {explanation}")
        else:
            st.success("No obvious warning patterns were found by the simple signal checker. This does not guarantee the message is safe.")

        with st.expander("What does the score mean?"):
            st.write(
                "The spam score is the model's estimated probability for the spam class, based on its training data. "
                "It is not a guarantee that a message is malicious or safe. The explanation signals are transparent text-pattern checks; "
                "they are separate from the machine-learning prediction."
            )
        st.warning("Safety reminder: Never share an OTP, password, PIN, or banking details because a message asks you to. Verify requests using an official channel.")

st.markdown("---")
left, right = st.columns(2)
with left:
    st.markdown("#### 🧠 ML pipeline")
    st.markdown('<div class="panel">Raw text → TF-IDF features → Naive Bayes → Spam / Legitimate</div>', unsafe_allow_html=True)
with right:
    st.markdown("#### 🔍 Explainable layer")
    st.markdown('<div class="panel">Keyword patterns + link detection + urgency indicators → human-readable reasons</div>', unsafe_allow_html=True)

st.caption("Demo project for learning. The public SMS dataset is not a substitute for real-world security testing.")
