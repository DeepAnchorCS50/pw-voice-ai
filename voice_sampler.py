import os
from google.cloud import texttospeech

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\config\google_credentials.json"

PROJECT = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone"
SAMPLE_DIR = os.path.join(PROJECT, "src", "data", "voice_samples")
os.makedirs(SAMPLE_DIR, exist_ok=True)

client = texttospeech.TextToSpeechClient()

# ── Sample texts ───────────────────────────────────────────────────────────────
AGENT_TEXT_HI = "Haan ji, namaste! Main Priya bol rahi hoon PhysicsWallah se. Aap ne hamare baare mein inquiry ki thi, toh main aapki kuch help kar sakti hoon kya? Aap kis class mein hain abhi?"

STUDENT_TEXT_HI = "Haan... main class 12 mein hoon. JEE ki taiyari kar raha hoon. Actually mujhe nahi pata tha ki aap call karenge, but haan, main interested hoon. Thoda batao kya hota hai PW mein?"

AGENT_TEXT_EN = "Hello! This is Priya calling from PhysicsWallah. You had enquired about our JEE preparation courses. How are you doing today? Could you tell me which class you are currently in?"

STUDENT_TEXT_EN = "Oh hi... yes I did fill the form. I'm in Class 12 right now. I'm targeting JEE Advanced actually. I wanted to know more about the courses and the faculty."

# ── Voice candidates to test ───────────────────────────────────────────────────
SAMPLES = [
    # Agent voices - Hindi (Hinglish)
    {
        "file": "01_agent_hindi_Aoede.mp3",
        "label": "Agent Hindi - Aoede (current)",
        "text": AGENT_TEXT_HI,
        "lang": "hi-IN",
        "voice": "hi-IN-Chirp3-HD-Aoede",
        "speed": 0.95, "pitch": 0.0
    },
    {
        "file": "02_agent_hindi_Kore.mp3",
        "label": "Agent Hindi - Kore (warmer)",
        "text": AGENT_TEXT_HI,
        "lang": "hi-IN",
        "voice": "hi-IN-Chirp3-HD-Kore",
        "speed": 0.92, "pitch": -1.0
    },
    {
        "file": "03_agent_hindi_Neural2A.mp3",
        "label": "Agent Hindi - Neural2-A (different model)",
        "text": AGENT_TEXT_HI,
        "lang": "hi-IN",
        "voice": "hi-IN-Neural2-A",
        "speed": 0.90, "pitch": -1.5
    },
    {
        "file": "04_agent_hindi_Leda.mp3",
        "label": "Agent Hindi - Leda (softer)",
        "text": AGENT_TEXT_HI,
        "lang": "hi-IN",
        "voice": "hi-IN-Chirp3-HD-Leda",
        "speed": 0.90, "pitch": -0.5
    },

    # Student voices - Hindi (teenage male)
    {
        "file": "05_student_hindi_Charon.mp3",
        "label": "Student Hindi - Charon (current)",
        "text": STUDENT_TEXT_HI,
        "lang": "hi-IN",
        "voice": "hi-IN-Chirp3-HD-Charon",
        "speed": 1.05, "pitch": 2.0
    },
    {
        "file": "06_student_hindi_Puck.mp3",
        "label": "Student Hindi - Puck (younger feel)",
        "text": STUDENT_TEXT_HI,
        "lang": "hi-IN",
        "voice": "hi-IN-Chirp3-HD-Puck",
        "speed": 1.05, "pitch": 3.0
    },
    {
        "file": "07_student_hindi_Neural2B.mp3",
        "label": "Student Hindi - Neural2-B (different model)",
        "text": STUDENT_TEXT_HI,
        "lang": "hi-IN",
        "voice": "hi-IN-Neural2-B",
        "speed": 1.05, "pitch": 2.5
    },
    {
        "file": "08_student_hindi_Orus.mp3",
        "label": "Student Hindi - Orus",
        "text": STUDENT_TEXT_HI,
        "lang": "hi-IN",
        "voice": "hi-IN-Chirp3-HD-Orus",
        "speed": 1.08, "pitch": 3.5
    },

    # Agent voices - English (South India)
    {
        "file": "09_agent_english_Aoede.mp3",
        "label": "Agent English - Aoede (current)",
        "text": AGENT_TEXT_EN,
        "lang": "en-IN",
        "voice": "en-IN-Chirp3-HD-Aoede",
        "speed": 0.95, "pitch": 0.0
    },
    {
        "file": "10_agent_english_Neural2D.mp3",
        "label": "Agent English - Neural2-D (different model)",
        "text": AGENT_TEXT_EN,
        "lang": "en-IN",
        "voice": "en-IN-Neural2-D",
        "speed": 0.92, "pitch": -1.0
    },
    {
        "file": "11_agent_english_Kore.mp3",
        "label": "Agent English - Kore",
        "text": AGENT_TEXT_EN,
        "lang": "en-IN",
        "voice": "en-IN-Chirp3-HD-Kore",
        "speed": 0.90, "pitch": -0.5
    },

    # Student voices - English (South India, teenage)
    {
        "file": "12_student_english_Charon.mp3",
        "label": "Student English - Charon (current)",
        "text": STUDENT_TEXT_EN,
        "lang": "en-IN",
        "voice": "en-IN-Chirp3-HD-Charon",
        "speed": 1.05, "pitch": 2.0
    },
    {
        "file": "13_student_english_Puck.mp3",
        "label": "Student English - Puck (younger)",
        "text": STUDENT_TEXT_EN,
        "lang": "en-IN",
        "voice": "en-IN-Chirp3-HD-Puck",
        "speed": 1.05, "pitch": 3.0
    },
    {
        "file": "14_student_english_Neural2C.mp3",
        "label": "Student English - Neural2-C (different model)",
        "text": STUDENT_TEXT_EN,
        "lang": "en-IN",
        "voice": "en-IN-Neural2-C",
        "speed": 1.05, "pitch": 2.5
    },
]

# ── Generate samples ───────────────────────────────────────────────────────────
print("=" * 60)
print("VOICE SAMPLER — generating {} samples".format(len(SAMPLES)))
print("=" * 60)

for sample in SAMPLES:
    print("Generating: {}".format(sample["label"]), end="", flush=True)

    try:
        synthesis_input = texttospeech.SynthesisInput(text=sample["text"])
        voice = texttospeech.VoiceSelectionParams(
            language_code=sample["lang"],
            name=sample["voice"]
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=sample["speed"],
            pitch=sample["pitch"]
        )
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        output_path = os.path.join(SAMPLE_DIR, sample["file"])
        with open(output_path, "wb") as f:
            f.write(response.audio_content)
        print(" ✅")

    except Exception as e:
        print(" ❌ {}".format(e))

print("\n" + "=" * 60)
print("DONE. All samples saved to:")
print(SAMPLE_DIR)
print("\nListen in this order:")
print("  Files 01-04: Agent Hindi voices (pick best agent voice)")
print("  Files 05-08: Student Hindi voices (pick most teenage-sounding)")
print("  Files 09-11: Agent English voices")
print("  Files 12-14: Student English voices")
print("\nTell me which file number sounds best for each role.")
print("=" * 60)