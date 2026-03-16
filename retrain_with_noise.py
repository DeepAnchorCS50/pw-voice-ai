# retrain_with_noise.py
# Week 7 Task 1: Inject noise into training data, retrain model to ~85-90% accuracy
# Run from project root:
# python retrain_with_noise.py

import pandas as pd
import numpy as np
import joblib
import json
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import random

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT      = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone"
DATA_FILE = ROOT + r"\src\data\synthetic_leads_dataset.csv"
MODEL_V1  = ROOT + r"\src\data\lead_scoring_model_v1.pkl"   # backup
MODEL_NEW = ROOT + r"\src\data\lead_scoring_model.pkl"       # overwrites
ENC_FILE  = ROOT + r"\src\data\label_encoders.pkl"
EVAL_FILE = ROOT + r"\src\data\eval_metrics.json"            # for evals page

FEATURE_COLS = [
    "current_class", "target_exam", "exam_year",
    "urgency_level", "budget_concern", "decision_maker", "engagement_level"
]
TARGET_COL = "tier_label"

RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# ── Load data ─────────────────────────────────────────────────────────────────
print("Loading data...")
df = pd.read_csv(DATA_FILE)
print(f"  Loaded {len(df)} rows")
print(f"  Tier distribution:\n{df[TARGET_COL].value_counts().to_string()}")

# ── Backup original model ─────────────────────────────────────────────────────
print("\nSkipping backup — lead_scoring_model_v1.pkl already exists.")

# ── Inject label noise ────────────────────────────────────────────────────────
print("\nInjecting noise...")
df_noisy = df.copy()
tiers = ["HOT", "WARM", "COLD"]

# 1. Flip labels for 12% of rows
n_flip = int(len(df) * 0.12)
flip_indices = random.sample(range(len(df)), n_flip)
for idx in flip_indices:
    current = df_noisy.at[idx, TARGET_COL]
    others  = [t for t in tiers if t != current]
    df_noisy.at[idx, TARGET_COL] = random.choice(others)

print(f"  Flipped {n_flip} labels")
print(f"  Noisy tier distribution:\n{df_noisy[TARGET_COL].value_counts().to_string()}")

# 2. Randomize engagement/urgency for 10% of rows
n_scramble = int(len(df) * 0.10)
scramble_indices = random.sample(range(len(df)), n_scramble)
engagement_levels = ["very_high", "high", "medium", "low"]
urgency_levels    = ["high", "medium", "low"]

for idx in scramble_indices:
    df_noisy.at[idx, "engagement_level"] = random.choice(engagement_levels)
    df_noisy.at[idx, "urgency_level"]    = random.choice(urgency_levels)

print(f"  Scrambled engagement/urgency for {n_scramble} rows")

# ── Encode features ───────────────────────────────────────────────────────────
print("\nEncoding features...")
encoders = {}
X = pd.DataFrame()

for col in FEATURE_COLS:
    le = LabelEncoder()
    X[col] = le.fit_transform(df_noisy[col].astype(str).str.lower())
    encoders[col] = le

# Encode target
le_target = LabelEncoder()
y = le_target.fit_transform(df_noisy[TARGET_COL])
encoders["tier_label"] = le_target

# ── Train model ───────────────────────────────────────────────────────────────
print("\nTraining Random Forest...")
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=8,          # limit depth to prevent overfitting noise away
    min_samples_leaf=3,   # require at least 3 samples per leaf
    random_state=RANDOM_SEED
)
model.fit(X, y)

# ── Evaluate ──────────────────────────────────────────────────────────────────
print("\nEvaluating...")
train_acc = model.score(X, y)

# Cross-validation gives a more honest accuracy estimate
cv_scores = cross_val_score(model, X, y, cv=5, scoring="accuracy")
cv_mean   = cv_scores.mean()
cv_std    = cv_scores.std()

y_pred = model.predict(X)
tier_names = le_target.classes_

print(f"\n  Train accuracy:       {train_acc*100:.1f}%")
print(f"  CV accuracy (5-fold): {cv_mean*100:.1f}% ± {cv_std*100:.1f}%")
print(f"\n  Classification Report:")
print(classification_report(y, y_pred, target_names=tier_names))
print(f"  Confusion Matrix:")
cm = confusion_matrix(y, y_pred)
print(cm)

# Feature importance
print(f"\n  Feature Importance:")
for feat, imp in sorted(zip(FEATURE_COLS, model.feature_importances_), key=lambda x: -x[1]):
    print(f"    {feat}: {imp*100:.1f}%")

# ── Save model + encoders ─────────────────────────────────────────────────────
print(f"\nSaving new model to lead_scoring_model.pkl...")
joblib.dump(model, MODEL_NEW)
joblib.dump(encoders, ENC_FILE)
print("  Saved.")

# ── Save eval metrics for evals page ─────────────────────────────────────────
from sklearn.metrics import precision_score, recall_score, f1_score

eval_metrics = {
    "train_accuracy":     round(train_acc * 100, 1),
    "cv_accuracy_mean":   round(cv_mean * 100, 1),
    "cv_accuracy_std":    round(cv_std * 100, 1),
    "precision_macro":    round(precision_score(y, y_pred, average="macro") * 100, 1),
    "recall_macro":       round(recall_score(y, y_pred, average="macro") * 100, 1),
    "f1_macro":           round(f1_score(y, y_pred, average="macro") * 100, 1),
    "confusion_matrix":   cm.tolist(),
    "tier_names":         tier_names.tolist(),
    "feature_importance": dict(zip(FEATURE_COLS, [round(x*100,1) for x in model.feature_importances_])),
    "n_estimators":       100,
    "noise_injected":     True,
    "label_noise_pct":    12,
    "feature_noise_pct":  10,
}

with open(EVAL_FILE, "w") as f:
    json.dump(eval_metrics, f, indent=2)

print(f"  Eval metrics saved to eval_metrics.json")

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "="*50)
print("DONE")
print(f"  CV Accuracy: {cv_mean*100:.1f}% (target: 85-90%)")
if 80 <= cv_mean*100 <= 93:
    print("  ✅ Accuracy looks realistic for demo")
else:
    print("  ⚠️  Accuracy outside target range — consider adjusting noise %")
print("="*50)