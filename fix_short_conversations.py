import json
import os

# ── The 18 short conversations to regenerate ──────────────────────────────────
SHORT_IDS = [
    "hot_018", "hot_023", "hot_022", "hot_024",
    "cold_006", "cold_024", "cold_034",
    "hot_005", "hot_007", "hot_011", "hot_014",
    "warm_002", "warm_006", "warm_009", "warm_016", "warm_031",
    "hot_015", "warm_017"
]

CHECKPOINT_FILE = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\src\data\pipeline_checkpoint.json"
CONV_DIR = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\src\data\conversations"

print("=" * 60)
print("FIXING SHORT CONVERSATIONS")
print("=" * 60)

# ── Step 1: Remove short IDs from checkpoint ──────────────────────────────────
print("\n[Step 1] Updating checkpoint...")
with open(CHECKPOINT_FILE, "r") as f:
    checkpoint = json.load(f)

before = len(checkpoint["completed_ids"])
checkpoint["completed_ids"] = [
    id for id in checkpoint["completed_ids"]
    if id not in SHORT_IDS
]
after = len(checkpoint["completed_ids"])

with open(CHECKPOINT_FILE, "w") as f:
    json.dump(checkpoint, f, indent=2)

print("   Removed {} IDs from checkpoint".format(before - after))
print("   Checkpoint now has {} completed IDs".format(after))

# ── Step 2: Delete the short conversation files ───────────────────────────────
print("\n[Step 2] Deleting short conversation files...")
deleted = 0
for conv_id in SHORT_IDS:
    filepath = os.path.join(CONV_DIR, "{}.json".format(conv_id))
    if os.path.exists(filepath):
        os.remove(filepath)
        print("   Deleted: {}.json".format(conv_id))
        deleted += 1
    else:
        print("   Not found: {}.json (skipping)".format(conv_id))

print("\n   Deleted {} files".format(deleted))

print("\n" + "=" * 60)
print("READY TO REGENERATE")
print("   Run: python src/orchestrator.py --session 1")
print("   The orchestrator will regenerate only these 18 conversations.")
print("=" * 60)