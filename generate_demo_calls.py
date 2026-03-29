"""
generate_demo_calls.py — PW Voice AI
Generates 5 pre-built demo call bundles (JSON + WAV) for the Operations page.
Run once locally: python generate_demo_calls.py
Outputs to: src/data/demo_calls/

Calls:
  call_001_outbound_hot  — Class 12, JEE Main, 3 months, high engagement → HOT
  call_002_inbound_cold  — Class 10, JEE, 24 months, low engagement     → COLD
  call_003_outbound_warm — Class 11, NEET, 12 months, medium            → WARM
  call_004_inbound_hot   — Class 12, NEET, 4 months, high               → HOT
  call_005_outbound_cold — Class 10, Board, 20 months, low              → COLD
"""

import os, sys, json, wave, io, base64, re
import joblib, pandas as pd

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT         = os.path.dirname(os.path.abspath(__file__))
SRC          = os.path.join(ROOT, "src")
OUTPUT_DIR   = os.path.join(SRC, "data", "demo_calls")
KB_PATH      = os.path.join(ROOT, "pw_knowledge_base", "pw_knowledge_base.json")
MODEL_FILE   = os.path.join(SRC, "data", "lead_scoring_model.pkl")
ENCODER_FILE = os.path.join(SRC, "data", "label_encoders.pkl")

sys.path.insert(0, ROOT)
sys.path.insert(0, SRC)

os.makedirs(OUTPUT_DIR, exist_ok=True)

from config.api_keys import CLAUDE_API_KEY
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(ROOT, "config", "google_credentials.json")

# ── Voice + audio constants ────────────────────────────────────────────────────
AGENT_VOICE          = "hi-IN-Chirp3-HD-Aoede"
STUDENT_VOICE_MALE   = "hi-IN-Chirp3-HD-Fenrir"
STUDENT_VOICE_FEMALE = "hi-IN-Chirp3-HD-Kore"
LANG                 = "hi-IN"
SAMPLE_RATE          = 24000
SILENCE_MS           = 500

FEMALE_NAMES = {
    "sneha","priya","pooja","anjali","neha","aarti","divya","meera","riya",
    "simran","ananya","kavya","ishita","shreya","tanvi","nisha","swati",
    "deepika","komal","preeti","sonal","richa","monika","sunita","geeta",
    "rekha","seema","usha","nandini"
}

FEATURE_COLS = [
    "current_class", "target_exam", "exam_year",
    "urgency_level", "budget_concern", "decision_maker", "engagement_level"
]

# ── The 5 call specifications ──────────────────────────────────────────────────
CALL_SPECS = [
    {
        "call_id":    "call_001",
        "filename":   "call_001_outbound_hot",
        "call_type":  "outbound",
        "expected_tier": "HOT",
        "scenario_override": {
            "student_name":     "Rahul Kumar",
            "city":             "Delhi",
            "class":            "12",
            "exam":             "JEE Main",
            "exam_year":        "2026",
            "months_to_exam":   3,
            "budget_concern":   False,
            "decision_maker":   "self",
            "engagement_level": "very_high",
            "lead_source":      "Downloaded JEE prep guide from PW website",
            "urgency_level":    "high",
            "key_phrase":       "I want to enroll in Arjuna batch — how do I proceed?",
        }
    },
    {
        "call_id":    "call_002",
        "filename":   "call_002_inbound_cold",
        "call_type":  "inbound",
        "expected_tier": "COLD",
        "scenario_override": {
            "student_name":     "Aakash Singh",
            "city":             "Lucknow",
            "class":            "10",
            "exam":             "JEE Main",
            "exam_year":        "2028",
            "months_to_exam":   24,
            "budget_concern":   True,
            "decision_maker":   "parent_later",
            "engagement_level": "low",
            "lead_source":      "Inbound — PW Helpline",
            "urgency_level":    "low",
            "key_phrase":       "I am just exploring options right now, not sure yet.",
        }
    },
    {
        "call_id":    "call_003",
        "filename":   "call_003_outbound_warm",
        "call_type":  "outbound",
        "expected_tier": "WARM",
        "scenario_override": {
            "student_name":     "Priya Sharma",
            "city":             "Pune",
            "class":            "11",
            "exam":             "NEET",
            "exam_year":        "2027",
            "months_to_exam":   12,
            "budget_concern":   True,
            "decision_maker":   "self",
            "engagement_level": "medium",
            "lead_source":      "Watched NEET free lecture on YouTube",
            "urgency_level":    "medium",
            "key_phrase":       "I am interested but I need to discuss with my parents first.",
        }
    },
    {
        "call_id":    "call_004",
        "filename":   "call_004_inbound_hot",
        "call_type":  "inbound",
        "expected_tier": "HOT",
        "scenario_override": {
            "student_name":     "Ananya Reddy",
            "city":             "Hyderabad",
            "class":            "12",
            "exam":             "NEET",
            "exam_year":        "2026",
            "months_to_exam":   4,
            "budget_concern":   False,
            "decision_maker":   "self",
            "engagement_level": "high",
            "lead_source":      "Inbound — PW Helpline",
            "urgency_level":    "high",
            "key_phrase":       "I want to start immediately — what is the fastest way to enroll?",
        }
    },
    {
        "call_id":    "call_005",
        "filename":   "call_005_outbound_cold",
        "call_type":  "outbound",
        "expected_tier": "COLD",
        "scenario_override": {
            "student_name":     "Suresh Yadav",
            "city":             "Patna",
            "class":            "10",
            "exam":             "JEE Main",
            "exam_year":        "2028",
            "months_to_exam":   20,
            "budget_concern":   True,
            "decision_maker":   "parent_present",
            "engagement_level": "low",
            "lead_source":      "Downloaded study material from PW app",
            "urgency_level":    "low",
            "key_phrase":       "My son wants to prepare but we need to think about the budget.",
        }
    },
]

# ── Helpers ────────────────────────────────────────────────────────────────────
def get_student_voice(name):
    return STUDENT_VOICE_FEMALE if name.strip().split()[0].lower() in FEMALE_NAMES else STUDENT_VOICE_MALE

def synthesize_wav(tts_client, text, voice_name, speed=1.0):
    from google.cloud import texttospeech

    text = text.replace("PhysicsWallah", "Physics Waala")
    text = re.sub(r'\bPW\b', 'P W', text)
    text = re.sub(r'\bJEE\b', 'J E E', text)
    text = re.sub(r'J E E\s*Main', 'J E E Main', text)
    text = re.sub(r'\bNEET\b', 'Neat', text)

    # Pronunciation fixes
    text = re.sub(r'(?<!J E E )\bmain\b', 'mein', text)   # Hindi main → mein, except JEE Main
    text = re.sub(r'(?<!J E E )\bMain\b', 'Mein', text)   # Capitalized version
    text = text.replace(' - ', ', ')                        # Hyphen-dash
    text = text.replace(' — ', ', ')                        # Em-dash (ASCII)
    text = text.replace(' \u2014 ', ', ')                   # Em-dash (unicode)
    text = text.replace('\u2014', ', ')                     # Em-dash without spaces

    def fix_price(m):
        num = int(m.group(1).replace(',',''))
        return f"{num:,} rupees"
    text = re.sub(r'₹([\d,]+)',    fix_price, text)
    text = re.sub(r'Rs\.?\s*([\d,]+)', fix_price, text)

    r = tts_client.synthesize_speech(
        input=texttospeech.SynthesisInput(text=text),
        voice=texttospeech.VoiceSelectionParams(language_code=LANG, name=voice_name),
        audio_config=texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=speed, pitch=0.0, sample_rate_hertz=SAMPLE_RATE
        )
    )
    return r.audio_content

def get_wav_duration_ms(wav_bytes):
    with wave.open(io.BytesIO(wav_bytes), 'rb') as w:
        return int(w.getnframes() / w.getframerate() * 1000)

def merge_wav_with_timestamps(audio_chunks):
    silence_frames = int(SAMPLE_RATE * SILENCE_MS / 1000)
    silence_bytes  = b'\x00\x00' * silence_frames
    timestamps     = []
    current_ms     = 0
    out_buffer     = io.BytesIO()
    with wave.open(out_buffer, 'wb') as out_wav:
        out_wav.setnchannels(1)
        out_wav.setsampwidth(2)
        out_wav.setframerate(SAMPLE_RATE)
        for i, chunk in enumerate(audio_chunks):
            timestamps.append(current_ms)
            with wave.open(io.BytesIO(chunk), 'rb') as in_wav:
                out_wav.writeframes(in_wav.readframes(in_wav.getnframes()))
            current_ms += get_wav_duration_ms(chunk)
            if i < len(audio_chunks) - 1:
                out_wav.writeframes(silence_bytes)
                current_ms += SILENCE_MS
    return out_buffer.getvalue(), timestamps

def ml_predict(scenario):
    model, encoders = joblib.load(MODEL_FILE), joblib.load(ENCODER_FILE)
    engagement = scenario.get("engagement_level", "medium")
    urgency    = "high" if engagement in ["very_high","high"] else "medium" if engagement == "medium" else "low"
    row = {
        "current_class":    str(scenario.get("class","11")),
        "target_exam":      scenario.get("exam","JEE Main"),
        "exam_year":        str(scenario.get("exam_year","2027")),
        "urgency_level":    urgency,
        "budget_concern":   "yes" if scenario.get("budget_concern") else "no",
        "decision_maker":   scenario.get("decision_maker","parent_later"),
        "engagement_level": engagement,
    }
    X = pd.DataFrame([{
        col: encoders[col].transform([str(row[col]).lower()])[0]
        if str(row[col]).lower() in encoders[col].classes_ else 0
        for col in FEATURE_COLS
    }])
    pred  = encoders["tier_label"].inverse_transform(model.predict(X))[0]
    proba = {
        encoders["tier_label"].inverse_transform([i])[0]: round(float(p)*100,1)
        for i,p in enumerate(model.predict_proba(X)[0])
    }
    return pred, proba

def generate_action_cards(scenario, tier, messages):
    """Generate templated action cards based on tier — no Claude API call needed."""
    name   = scenario.get("student_name","Student")
    city   = scenario.get("city","India")
    exam   = scenario.get("exam","JEE Main")
    cls    = scenario.get("class","12")
    source = scenario.get("lead_source","PW inquiry")

    # Extract any promised actions from transcript
    promised = []
    for m in messages:
        if m["speaker"] == "agent":
            t = m["text"].lower()
            if any(w in t for w in ["send", "share", "forward", "whatsapp", "email", "link"]):
                promised.append("Send course details and enrollment link")
                break
    if not promised:
        promised = ["Follow up within 24 hours"]

    if tier == "HOT":
        return {
            "promised_actions":   promised,
            "recommended_actions":["Assign to senior sales rep","Schedule parent/student call today"],
            "slack_message": {
                "channel": "#pw-hot-leads",
                "preview": f"🔥 HOT lead: {name}, {exam}, Class {cls}, {city}. High intent, ready to enroll. Immediate callback recommended."
            },
            "email": {
                "to":      name,
                "subject": f"Your {exam} Preparation Plan — PhysicsWallah",
                "preview": f"Hi {name.split()[0]}, it was great speaking with you today! Based on your preparation goals, I've put together a personalized plan for your {exam} journey."
            },
            "crm_record": {
                "status":        "Qualified — HOT",
                "assigned_to":   "Senior Sales Team",
                "follow_up":     "Today",
                "lead_source":   source,
                "notes":         f"High engagement, self decision-maker. Likely to convert with one follow-up call."
            }
        }
    elif tier == "WARM":
        return {
            "promised_actions":   promised,
            "recommended_actions":["Send course brochure","Schedule callback in 48 hours"],
            "slack_message": {
                "channel": "#pw-warm-leads",
                "preview": f"🔶 WARM lead: {name}, {exam}, Class {cls}, {city}. Interested but needs nurturing. Follow up in 2 days."
            },
            "email": {
                "to":      name,
                "subject": f"Continuing Your {exam} Journey — PhysicsWallah",
                "preview": f"Hi {name.split()[0]}, thank you for your time today. I understand you'd like to discuss with your family — I've attached our course guide to help with that conversation."
            },
            "crm_record": {
                "status":        "Nurturing — WARM",
                "assigned_to":   "Standard Sales Team",
                "follow_up":     "In 48 hours",
                "lead_source":   source,
                "notes":         f"Interested but needs parental approval. Send materials, follow up in 2 days."
            }
        }
    else:  # COLD
        return {
            "promised_actions":   promised,
            "recommended_actions":["Add to drip email campaign","Schedule follow-up in 3 months"],
            "slack_message": {
                "channel": "#pw-nurture",
                "preview": f"❄️ COLD lead: {name}, {exam}, Class {cls}, {city}. Early stage, low urgency. Added to nurture campaign."
            },
            "email": {
                "to":      name,
                "subject": f"Start Your {exam} Preparation Early — PhysicsWallah",
                "preview": f"Hi {name.split()[0]}, thank you for reaching out to PhysicsWallah! Even though your exam is a while away, starting early gives you a real advantage."
            },
            "crm_record": {
                "status":        "Nurture Pool — COLD",
                "assigned_to":   "Drip Campaign",
                "follow_up":     "In 3 months",
                "lead_source":   source,
                "notes":         f"Low urgency, budget concern. Long-term nurture via email drip campaign."
            }
        }

# ── Main generation loop ───────────────────────────────────────────────────────
def generate_call(spec):
    from agents.conversation_generator import ConversationGenerator
    from google.cloud import texttospeech

    call_id   = spec["call_id"]
    filename  = spec["filename"]
    call_type = spec["call_type"]
    scenario  = spec["scenario_override"].copy()
    scenario["scenario_id"] = call_id
    scenario["call_type"]   = call_type

    print(f"\n{'='*60}")
    print(f"Generating {filename}")
    print(f"  Student: {scenario['student_name']} ({scenario['city']})")
    print(f"  Exam:    {scenario['exam']} Class {scenario['class']}")
    print(f"  Expected: {spec['expected_tier']}")

    # 1. Generate conversation
    print("  [1/4] Generating conversation via Claude API...")
    gen  = ConversationGenerator(CLAUDE_API_KEY, KB_PATH)
    conv = gen.generate(scenario)
    if conv.get("failed"):
        raise Exception(f"Conversation failed: {conv.get('error')}")
    messages = conv.get("messages", [])
    print(f"        → {len(messages)} messages generated")

    # 2. Synthesize audio
    print(f"  [2/4] Synthesizing {len(messages)} audio segments...")
    tts_client    = texttospeech.TextToSpeechClient()
    student_voice = get_student_voice(scenario["student_name"])
    audio_chunks  = []
    for i, msg in enumerate(messages):
        voice = AGENT_VOICE if msg["speaker"] == "agent" else student_voice
        speed = 0.95 if msg["speaker"] == "agent" else 0.90
        audio_chunks.append(synthesize_wav(tts_client, msg["text"], voice, speed))
        print(f"        → {i+1}/{len(messages)}", end="\r")
    print()

    # 3. Merge audio with timestamps
    print("  [3/4] Merging audio...")
    merged_wav, timestamps = merge_wav_with_timestamps(audio_chunks)
    duration_s = sum(get_wav_duration_ms(c) for c in audio_chunks) / 1000
    print(f"        → Duration: {duration_s:.1f}s, Size: {len(merged_wav)/1024:.0f}KB")

    # Attach timestamps to messages
    for i, msg in enumerate(messages):
        msg["timestamp"] = timestamps[i] / 1000.0  # convert ms to seconds

    # 4. ML scoring
    print("  [4/4] Running ML scoring...")
    ml_tier, ml_proba = ml_predict(scenario)
    print(f"        → Predicted: {ml_tier} (expected: {spec['expected_tier']})")

    # 5. Generate action cards (templated, no API call)
    actions = generate_action_cards(scenario, ml_tier, messages)

    # 6. Rule-based score (simple heuristic for display)
    engagement_scores = {"very_high":95,"high":80,"medium":60,"low":35}
    rule_score = engagement_scores.get(scenario.get("engagement_level","medium"), 60)
    if scenario.get("budget_concern"): rule_score -= 10
    if scenario.get("decision_maker") == "self": rule_score += 5
    if scenario.get("months_to_exam",12) <= 6: rule_score += 10
    rule_score = max(0, min(100, rule_score))

    # 7. Build call bundle JSON
    call_bundle = {
        "call_id":    call_id,
        "call_type":  call_type,
        "student": {
            "name":        scenario["student_name"],
            "city":        scenario["city"],
            "class":       scenario["class"],
            "exam":        scenario["exam"],
            "lead_source": scenario.get("lead_source","PW inquiry"),
        },
        "transcript": messages,
        "timestamps": timestamps,
        "duration_seconds": duration_s,
        "extracted_fields": {
            "name":            scenario["student_name"],
            "class":           scenario["class"],
            "exam":            scenario["exam"],
            "city":            scenario["city"],
            "months_to_exam":  scenario.get("months_to_exam",12),
            "budget_concern":  scenario.get("budget_concern",False),
            "decision_maker":  scenario.get("decision_maker","parent_later"),
            "engagement_level":scenario.get("engagement_level","medium"),
        },
        "rule_based_score": rule_score,
        "ml_score":          int(round(max(ml_proba.values()))),
        "ml_proba":          ml_proba,
        "tier":              ml_tier,
        "action_cards":      actions,
    }

    # 8. Save JSON
    json_path = os.path.join(OUTPUT_DIR, filename + ".json")
    with open(json_path, "w") as f:
        json.dump(call_bundle, f, indent=2)
    print(f"        → Saved JSON: {json_path}")

    # 9. Save WAV
    wav_path = os.path.join(OUTPUT_DIR, filename + ".wav")
    with open(wav_path, "wb") as f:
        f.write(merged_wav)
    print(f"        → Saved WAV:  {wav_path} ({len(merged_wav)/1024/1024:.1f} MB)")

    return call_bundle

# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate demo call bundles for PW Voice AI")
    parser.add_argument("--calls", nargs="+", type=int, choices=[1,2,3,4,5],
                        help="Which calls to generate (e.g. --calls 1 2). Default: all 5.")
    args = parser.parse_args()

    specs_to_run = CALL_SPECS
    if args.calls:
        specs_to_run = [CALL_SPECS[i-1] for i in args.calls]

    print(f"\nPW Voice AI — Demo Call Generator")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Generating {len(specs_to_run)} call(s)...\n")

    results = []
    for spec in specs_to_run:
        try:
            result = generate_call(spec)
            results.append({"filename": spec["filename"], "status": "✅", "tier": result["tier"]})
        except Exception as e:
            print(f"\n  ❌ FAILED: {e}")
            results.append({"filename": spec["filename"], "status": "❌", "error": str(e)})

    print(f"\n{'='*60}")
    print("Summary:")
    for r in results:
        if r["status"] == "✅":
            print(f"  ✅ {r['filename']} → {r['tier']}")
        else:
            print(f"  ❌ {r['filename']} → {r['error']}")

    print(f"\nDone. Files saved to: {OUTPUT_DIR}")
    print("Next step: commit src/data/demo_calls/ to GitHub")
