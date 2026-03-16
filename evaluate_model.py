import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report

# ── Paths ─────────────────────────────────────────────────────────────────────
CSV_FILE = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\src\data\synthetic_leads_dataset.csv"
MODEL_FILE = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\src\data\lead_scoring_model.pkl"
ENCODER_FILE = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\src\data\label_encoders.pkl"

FEATURE_COLS = [
    "current_class", "target_exam", "exam_year",
    "urgency_level", "budget_concern", "decision_maker", "engagement_level"
]
TARGET_COL = "tier_label"

print("=" * 60)
print("WEEK 5 SESSION 2: MODEL EVALUATION")
print("=" * 60)

# ── Load model and data ───────────────────────────────────────────────────────
print("\n[Step 1] Loading model and data...")
model = joblib.load(MODEL_FILE)
encoders = joblib.load(ENCODER_FILE)
df = pd.read_csv(CSV_FILE)
print("   Model loaded: {} trees".format(model.n_estimators))
print("   Dataset: {} leads".format(len(df)))

# ── Prepare features (same as training) ──────────────────────────────────────
print("\n[Step 2] Preparing features...")
df_clean = df[FEATURE_COLS + [TARGET_COL]].copy()
for col in FEATURE_COLS:
    df_clean[col] = df_clean[col].fillna("unknown").astype(str)
df_clean["budget_concern"] = df_clean["budget_concern"].str.lower()

for col in FEATURE_COLS:
    le = encoders[col]
    # Handle unseen values gracefully
    df_clean[col] = df_clean[col].apply(
        lambda x: le.transform([x])[0] if x in le.classes_ else -1
    )

target_encoder = encoders["tier_label"]
df_clean[TARGET_COL] = target_encoder.transform(df_clean[TARGET_COL])

X = df_clean[FEATURE_COLS]
y = df_clean[TARGET_COL]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ── Confusion matrix ──────────────────────────────────────────────────────────
# WHY confusion matrix?
# It shows not just HOW MANY the model got wrong, but WHAT TYPE of errors it makes.
# Getting a HOT lead wrong (predicting COLD) is much worse than WARM→COLD.
# A confusion matrix reveals which mistakes matter most.

print("\n[Step 3] Confusion Matrix (test set — 20 leads):")
print("   Rows = Actual tier | Columns = Predicted tier\n")

y_pred = model.predict(X_test)
cm = confusion_matrix(y_test, y_pred)
tier_names = target_encoder.classes_  # ['COLD', 'HOT', 'WARM']

# Print header
print("              ", end="")
for name in tier_names:
    print("{:>8}".format("→" + name), end="")
print()

# Print rows
for i, row in enumerate(cm):
    print("   Actual {:>4}  ".format(tier_names[i]), end="")
    for val in row:
        marker = " ✅" if val > 0 and i == list(row).index(max(row)) else ""
        print("{:>8}".format(val), end="")
    print()

print("\n   How to read: Each row is the actual tier.")
print("   Numbers on the diagonal = correct predictions.")
print("   Numbers off diagonal = mistakes.")

# ── Where did it go wrong? ────────────────────────────────────────────────────
print("\n[Step 4] Analysing mistakes on FULL dataset...")

y_pred_all = model.predict(X)
y_actual_all = df_clean[TARGET_COL].values

mistakes = []
for i, (actual, predicted) in enumerate(zip(y_actual_all, y_pred_all)):
    if actual != predicted:
        actual_label = target_encoder.inverse_transform([actual])[0]
        predicted_label = target_encoder.inverse_transform([predicted])[0]
        mistakes.append({
            "conversation_id": df.iloc[i]["conversation_id"],
            "actual": actual_label,
            "predicted": predicted_label,
            "score": df.iloc[i]["score"],
            "urgency": df.iloc[i]["urgency_level"],
            "engagement": df.iloc[i]["engagement_level"],
            "class": df.iloc[i]["current_class"],
            "decision_maker": df.iloc[i]["decision_maker"]
        })

if mistakes:
    print("\n   Leads where ML disagrees with ground truth:")
    print("   {:<15} {:>6} {:>6} {:>8} {:>10} {:>7} {:>10}".format(
        "ID", "Actual", "ML Says", "Urgency", "Engagement", "Class", "Decision"
    ))
    print("   " + "-" * 70)
    for m in mistakes:
        print("   {:<15} {:>6} {:>8} {:>8} {:>10} {:>7} {:>10}".format(
            m["conversation_id"], m["actual"], m["predicted"],
            m["urgency"], m["engagement"], m["class"], m["decision_maker"]
        ))
else:
    print("   No mistakes on full dataset — perfect agreement with ground truth.")

# ── Compare ML vs rule-based ──────────────────────────────────────────────────
print("\n[Step 5] ML model vs Rule-based scorer comparison...")

# Rule-based agreement with ground truth
rule_correct = (df["predicted_tier"] == df["tier_label"]).sum()
rule_accuracy = rule_correct / len(df) * 100

# ML agreement with ground truth
ml_correct = len(df) - len(mistakes)
ml_accuracy = ml_correct / len(df) * 100

print("\n   {:<25} {:>10} {:>10}".format("", "Correct", "Accuracy"))
print("   " + "-" * 45)
print("   {:<25} {:>10} {:>9.1f}%".format("Rule-based scorer", rule_correct, rule_accuracy))
print("   {:<25} {:>10} {:>9.1f}%".format("ML model", ml_correct, ml_accuracy))

improvement = ml_accuracy - rule_accuracy
if improvement > 0:
    print("\n   ✅ ML improves on rule-based by {:.1f} percentage points".format(improvement))
elif improvement == 0:
    print("\n   ➡️  ML matches rule-based accuracy")
else:
    print("\n   ⚠️  ML is {:.1f}pp below rule-based (expected with small dataset)".format(abs(improvement)))

# ── What the model learned ────────────────────────────────────────────────────
print("\n[Step 6] Decision patterns the model learned:")
print("\n   Feature importance ranking:")
importances = model.feature_importances_
feature_importance = sorted(
    zip(FEATURE_COLS, importances),
    key=lambda x: x[1],
    reverse=True
)
for rank, (feature, importance) in enumerate(feature_importance, 1):
    bar = "█" * int(importance * 50)
    print("   {}. {:<20} {:.1f}%  {}".format(rank, feature, importance * 100, bar))

print("\n   Interpretation:")
top_feature = feature_importance[0][0]
second_feature = feature_importance[1][0]
print("   - '{}' is the strongest predictor".format(top_feature))
print("   - '{}' is nearly as important".format(second_feature))
print("   - Together they drive {:.0f}% of decisions".format(
    (feature_importance[0][1] + feature_importance[1][1]) * 100
))

print("\n" + "=" * 60)
print("SESSION 2 COMPLETE")
print("   You now understand what your model learned.")
print("   Next: Session 3 adds ML scoring to your dashboard.")
print("=" * 60)