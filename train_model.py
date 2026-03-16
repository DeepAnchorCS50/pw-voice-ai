import pandas as pd
import json
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

# ── Paths ─────────────────────────────────────────────────────────────────────
CSV_FILE = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\src\data\synthetic_leads_dataset.csv"
MODEL_DIR = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\src\data"
MODEL_FILE = os.path.join(MODEL_DIR, "lead_scoring_model.pkl")
ENCODER_FILE = os.path.join(MODEL_DIR, "label_encoders.pkl")

print("=" * 60)
print("WEEK 5: TRAINING LEAD SCORING ML MODEL")
print("=" * 60)

# ── Step 1: Load data ─────────────────────────────────────────────────────────
print("\n[Step 1] Loading dataset...")
df = pd.read_csv(CSV_FILE)
print("   Rows: {} | Columns: {}".format(len(df), len(df.columns)))
print("   Tier distribution:")
print(df["tier_label"].value_counts().to_string())

# ── Step 2: Select features ───────────────────────────────────────────────────
# WHY these features?
# - current_class: proxy for urgency (Class 12 > Class 11 > Class 10)
# - target_exam: different exams have different timelines
# - exam_year: how far away is the exam
# - urgency_level: extracted from conversation tone
# - budget_concern: strong negative signal
# - decision_maker: self-deciders convert faster
# - engagement_level: strongest predictor of intent
# NOT included: full_name, location, conversation_id (not predictive)

print("\n[Step 2] Selecting features...")
FEATURE_COLS = [
    "current_class",
    "target_exam",
    "exam_year",
    "urgency_level",
    "budget_concern",
    "decision_maker",
    "engagement_level"
]
TARGET_COL = "tier_label"

# ── Step 3: Handle missing values ─────────────────────────────────────────────
print("\n[Step 3] Cleaning data...")
df_clean = df[FEATURE_COLS + [TARGET_COL]].copy()

# Fill missing values with "unknown"
for col in FEATURE_COLS:
    df_clean[col] = df_clean[col].fillna("unknown").astype(str)

# Convert budget_concern to string (it's boolean in CSV)
df_clean["budget_concern"] = df_clean["budget_concern"].str.lower()

print("   Missing values after cleaning: {}".format(df_clean.isnull().sum().sum()))

# ── Step 4: Encode categorical features ───────────────────────────────────────
# WHY encoding? ML models need numbers, not text.
# "HOT" → 0, "WARM" → 1, "COLD" → 2
# "high" → 0, "low" → 1, "medium" → 2
# LabelEncoder does this automatically and remembers the mapping

print("\n[Step 4] Encoding categorical features...")
encoders = {}

for col in FEATURE_COLS:
    le = LabelEncoder()
    df_clean[col] = le.fit_transform(df_clean[col])
    encoders[col] = le
    print("   {} → {}".format(col, dict(zip(le.classes_, le.transform(le.classes_)))))

# Encode target label
target_encoder = LabelEncoder()
df_clean[TARGET_COL] = target_encoder.fit_transform(df_clean[TARGET_COL])
encoders["tier_label"] = target_encoder
print("\n   Tier mapping: {}".format(
    dict(zip(target_encoder.classes_, target_encoder.transform(target_encoder.classes_)))
))

# ── Step 5: Split into train and test ─────────────────────────────────────────
# WHY split? You train on 80% of data, test on the remaining 20%.
# Testing on data the model has NEVER seen gives honest accuracy.
# If you tested on training data, the model would "cheat" — it already memorised it.

print("\n[Step 5] Splitting data into train/test sets...")
X = df_clean[FEATURE_COLS]
y = df_clean[TARGET_COL]

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,       # 20% for testing = 20 leads
    random_state=42,     # Fixed seed = reproducible split every time
    stratify=y           # Ensure HOT/WARM/COLD are proportionally represented in both sets
)

print("   Training set: {} leads".format(len(X_train)))
print("   Test set: {} leads".format(len(X_test)))

# ── Step 6: Train the model ───────────────────────────────────────────────────
# n_estimators=100 → build 100 decision trees
# max_depth=5 → each tree can ask max 5 questions (prevents overfitting)
# random_state=42 → reproducible results

print("\n[Step 6] Training Random Forest...")
print("   Building 100 decision trees...")

model = RandomForestClassifier(
    n_estimators=100,
    max_depth=5,
    random_state=42,
    class_weight="balanced"  # Handles any slight class imbalance
)

model.fit(X_train, y_train)
print("   Training complete!")

# ── Step 7: Evaluate on test set ──────────────────────────────────────────────
print("\n[Step 7] Evaluating on test set...")
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("\n   ACCURACY: {:.1f}%".format(accuracy * 100))
print("\n   Detailed Report:")
print(classification_report(
    y_test, y_pred,
    target_names=target_encoder.classes_
))

# ── Step 8: Feature importance ────────────────────────────────────────────────
# Which features matter most to the model?
print("\n[Step 8] Feature importance (what the model learned):")
importances = model.feature_importances_
feature_importance = sorted(
    zip(FEATURE_COLS, importances),
    key=lambda x: x[1],
    reverse=True
)
for feature, importance in feature_importance:
    bar = "█" * int(importance * 50)
    print("   {:<20} {:.3f}  {}".format(feature, importance, bar))

# ── Step 9: Save model and encoders ───────────────────────────────────────────
print("\n[Step 9] Saving model to disk...")
joblib.dump(model, MODEL_FILE)
joblib.dump(encoders, ENCODER_FILE)
print("   Model saved: {}".format(MODEL_FILE))
print("   Encoders saved: {}".format(ENCODER_FILE))

print("\n" + "=" * 60)
print("SESSION 1 COMPLETE")
print("   Your ML model is trained and saved.")
print("   Next: Session 2 will analyse what it learned.")
print("=" * 60)