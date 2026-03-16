"""
Voice Sampler v2 - Minimal 5 samples
Goal: Pick best student voice. Agent = Aoede (already decided)
"""

from google.cloud import texttospeech
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\config\google_credentials.json"

# ── Sample texts ──────────────────────────────────────────────────────────────
AGENT_TEXT = "Haan Rahul! Bilkul sahi socha aapne. JEE Lakshya batch mein Alakh Sir khud padhate hain. Aur pricing bhi bahut reasonable hai — sirf 35,999 rupaye poore 2 saal ke liye."

STUDENT_TEXT = "Haan... matlab, mujhe lagta hai JEE dena chahiye. But papa bol rahe hain pehle boards pe focus karo. Aur coaching ka kharcha bhi bahut hai yaar."

SAMPLES = [
    # Agent reference - we already like Aoede, just confirming
    {
        "file": "01_agent_Aoede_reference.mp3",
        "label": "Agent - Aoede (REFERENCE - already selected)",
        "text": AGENT_TEXT,
        "lang": "hi-IN",
        "voice": "hi-IN-Chirp3-HD-Aoede",
        "speed": 0.95, "pitch": 0.0
    },

    # Student candidates - all Chirp3-HD, pitch=0.0
    {
        "file": "02_student_Charon.mp3",
        "label": "Student - Charon (male, should sound young)",
        "text": STUDENT_TEXT,
        "lang": "hi-IN",
        "voice": "hi-IN-Chirp3-HD-Charon",
        "speed": 1.05, "pitch": 0.0
    },
    {
        "file": "03_student_Puck.mp3",
        "label": "Student - Puck (male, lighter tone)",
        "text": STUDENT_TEXT,
        "lang": "hi-IN",
        "voice": "hi-IN-Chirp3-HD-Puck",
        "speed": 1.05, "pitch": 0.0
    },
    {
        "file": "04_student_Orus.mp3",
        "label": "Student - Orus (male, different character)",
        "text": STUDENT_TEXT,
        "lang": "hi-IN",
        "voice": "hi-IN-Chirp3-HD-Orus",
        "speed": 1.05, "pitch": 0.0
    },
    {
        "file": "05_student_Fenrir.mp3",
        "label": "Student - Fenrir (male, untested)",
        "text": STUDENT_TEXT,
        "lang": "hi-IN",
        "voice": "hi-IN-Chirp3-HD-Fenrir",
        "speed": 1.05, "pitch": 0.0
    },
]

# ── Output folder ─────────────────────────────────────────────────────────────
OUTPUT_DIR = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\src\data\voice_samples_v2"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Generate ──────────────────────────────────────────────────────────────────
client = texttospeech.TextToSpeechClient()

print("=" * 60)
print(f"VOICE SAMPLER v2 — generating {len(SAMPLES)} samples")
print("=" * 60)

for s in SAMPLES:
    out_path = os.path.join(OUTPUT_DIR, s["file"])
    print(f"Generating: {s['label']} ... ", end="", flush=True)

    try:
        synthesis_input = texttospeech.SynthesisInput(text=s["text"])

        voice = texttospeech.VoiceSelectionParams(
            language_code=s["lang"],
            name=s["voice"]
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=s["speed"],
            pitch=s["pitch"]   # 0.0 for all Chirp3-HD
        )

        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        with open(out_path, "wb") as f:
            f.write(response.audio_content)

        print("✅")

    except Exception as e:
        print(f"❌ {e}")

print("\n" + "=" * 60)
print(f"Done! Samples saved to:\n{OUTPUT_DIR}")
print("\nListen and tell me:")
print("  File 01: Agent Aoede — still happy with this?")
print("  Files 02-05: Which student sounds most like a real Indian teenager?")
print("=" * 60)