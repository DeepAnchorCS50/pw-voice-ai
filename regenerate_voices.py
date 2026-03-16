"""
Regenerate voice MP3s for 3 showcase conversations
Agent: Aoede (hi-IN-Chirp3-HD-Aoede)
Student male: Fenrir (hi-IN-Chirp3-HD-Fenrir)
Student female: Kore (hi-IN-Chirp3-HD-Kore)
Gender detected automatically from student name in scenario
"""

import os
import json
import time
from google.cloud import texttospeech

# ── Credentials ───────────────────────────────────────────────────────────────
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\config\google_credentials.json"

# ── Voice config ──────────────────────────────────────────────────────────────
AGENT_VOICE          = "hi-IN-Chirp3-HD-Aoede"
STUDENT_VOICE_MALE   = "hi-IN-Chirp3-HD-Fenrir"
STUDENT_VOICE_FEMALE = "hi-IN-Chirp3-HD-Kore"
LANG = "hi-IN"

AGENT_SPEED   = 0.95
STUDENT_SPEED = 1.05

# ── Female names in your dataset ──────────────────────────────────────────────
FEMALE_NAMES = {
    "sneha", "priya", "pooja", "anjali", "neha", "aarti", "divya",
    "meera", "riya", "simran", "ananya", "kavya", "ishita", "shreya",
    "tanvi", "nisha", "swati", "deepika", "komal", "preeti", "sonal",
    "richa", "monika", "sunita", "geeta", "rekha", "seema", "usha"
}

def get_student_voice(scenario):
    """Pick male or female voice based on student name in scenario."""
    name = scenario.get("name", "").strip().lower()
    if name in FEMALE_NAMES:
        print(f"  -> Female student detected ({scenario['name']}), using Kore")
        return STUDENT_VOICE_FEMALE
    else:
        print(f"  -> Male student detected ({scenario['name']}), using Fenrir")
        return STUDENT_VOICE_MALE

# ── Conversations to regenerate ───────────────────────────────────────────────
BASE = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\src\data\voice_conversations"

CONVERSATIONS = [
    "voice_hot_001",   # HOT showcase
    "voice_warm_001",  # WARM showcase
    "voice_cold_001",  # COLD showcase
]

# ── TTS client ────────────────────────────────────────────────────────────────
client = texttospeech.TextToSpeechClient()

def synthesize(text, voice_name, speed):
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code=LANG,
        name=voice_name
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=speed,
        pitch=0.0  # Chirp3-HD requires pitch=0.0
    )
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )
    return response.audio_content


# ── Main loop ─────────────────────────────────────────────────────────────────
for conv_id in CONVERSATIONS:
    conv_dir = os.path.join(BASE, conv_id)
    json_path = os.path.join(conv_dir, "conversation.json")

    print(f"\n{'='*60}")
    print(f"Processing: {conv_id}")
    print(f"{'='*60}")

    with open(json_path, "r", encoding="utf-8") as f:
        conv = json.load(f)

    student_voice = get_student_voice(conv["scenario"])

    messages = conv["messages"]
    total = len(messages)
    success = 0
    failed = 0

    for msg in messages:
        idx = msg["index"]
        speaker = msg["speaker"]
        text = msg["text"]
        audio_file = msg["audio_file"]
        out_path = os.path.join(conv_dir, audio_file)

        voice_name = AGENT_VOICE if speaker == "agent" else student_voice
        speed = AGENT_SPEED if speaker == "agent" else STUDENT_SPEED

        print(f"  [{idx+1}/{total}] {speaker}: {text[:50]}...", end=" ", flush=True)

        try:
            audio = synthesize(text, voice_name, speed)
            with open(out_path, "wb") as f:
                f.write(audio)
            print("OK")
            success += 1
            time.sleep(0.3)  # avoid rate limiting

        except Exception as e:
            print(f"FAILED: {e}")
            failed += 1

    print(f"\n  {success} generated, {failed} failed -- {conv_id} done")

print(f"\n{'='*60}")
print("COMPLETE -- 3 showcase conversations regenerated")
print(f"  HOT:  voice_hot_001")
print(f"  WARM: voice_warm_001")
print(f"  COLD: voice_cold_001")
print(f"  Voices: Aoede (agent) + Fenrir/Kore (student, gender-aware)")
print(f"{'='*60}")