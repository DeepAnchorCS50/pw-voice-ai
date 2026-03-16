import os
import json
import time
import anthropic
from google.cloud import texttospeech

# ── Credentials ───────────────────────────────────────────────────────────────
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\config\google_credentials.json"

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone"
VOICE_DIR = os.path.join(PROJECT, "src", "data", "voice_conversations")
KB_PATH = os.path.join(PROJECT, "pw_knowledge_base", "pw_knowledge_base.json")
CONFIG_PATH = os.path.join(PROJECT, "config", "api_keys.py")

os.makedirs(VOICE_DIR, exist_ok=True)

# ── Load API key ──────────────────────────────────────────────────────────────
import importlib.util
spec = importlib.util.spec_from_file_location("api_keys", CONFIG_PATH)
api_keys = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api_keys)
CLAUDE_API_KEY = api_keys.CLAUDE_API_KEY

claude = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
tts_client = texttospeech.TextToSpeechClient()

# ── 15 scenarios: North India (Hinglish) + South India (English) ──────────────
SCENARIOS = [
    # North India - Hinglish
    {
        "id": "voice_hot_001", "tier": "HOT", "region": "north",
        "name": "Arjun", "city": "Delhi", "state": "Delhi",
        "class": "12", "exam": "JEE Advanced", "months_to_exam": 4,
        "decision_maker": "self", "budget_concern": False,
        "key_situation": "Dropped Aakash coaching, looking for better online option urgently"
    },
    {
        "id": "voice_hot_002", "tier": "HOT", "region": "north",
        "name": "Priya", "city": "Kota", "state": "Rajasthan",
        "class": "12", "exam": "NEET", "months_to_exam": 5,
        "decision_maker": "parent_present", "budget_concern": False,
        "key_situation": "Father on call, ready to enroll today if price is right"
    },
    {
        "id": "voice_hot_003", "tier": "HOT", "region": "north",
        "name": "Rahul", "city": "Jaipur", "state": "Rajasthan",
        "class": "dropper", "exam": "JEE Main", "months_to_exam": 3,
        "decision_maker": "self", "budget_concern": False,
        "key_situation": "Second attempt, scored 87 percentile last year, wants to crack 99+"
    },
    {
        "id": "voice_warm_001", "tier": "WARM", "region": "north",
        "name": "Sneha", "city": "Lucknow", "state": "UP",
        "class": "11", "exam": "NEET", "months_to_exam": 14,
        "decision_maker": "parent_later", "budget_concern": True,
        "key_situation": "Interested but wants to discuss fees with parents tonight"
    },
    {
        "id": "voice_warm_002", "tier": "WARM", "region": "north",
        "name": "Vikram", "city": "Patna", "state": "Bihar",
        "class": "11", "exam": "JEE Main", "months_to_exam": 16,
        "decision_maker": "self", "budget_concern": True,
        "key_situation": "Comparing PW with Unacademy, price sensitive"
    },
    {
        "id": "voice_warm_003", "tier": "WARM", "region": "north",
        "name": "Anjali", "city": "Indore", "state": "MP",
        "class": "12", "exam": "JEE Main", "months_to_exam": 8,
        "decision_maker": "parent_later", "budget_concern": False,
        "key_situation": "Wants to start but confused between online and offline"
    },
    {
        "id": "voice_cold_001", "tier": "COLD", "region": "north",
        "name": "Rohan", "city": "Kanpur", "state": "UP",
        "class": "10", "exam": "JEE Main", "months_to_exam": 26,
        "decision_maker": "parent_later", "budget_concern": True,
        "key_situation": "Just exploring, parents not aware he called"
    },
    {
        "id": "voice_edge_001", "tier": "WARM", "region": "north",
        "name": "Kabir", "city": "Varanasi", "state": "UP",
        "class": "12", "exam": "JEE Advanced", "months_to_exam": 6,
        "decision_maker": "self", "budget_concern": True,
        "key_situation": "Very urgent timeline but serious budget constraint — edge case"
    },
    # South India - English
    {
        "id": "voice_hot_004", "tier": "HOT", "region": "south",
        "name": "Aryan", "city": "Bangalore", "state": "Karnataka",
        "class": "12", "exam": "JEE Advanced", "months_to_exam": 4,
        "decision_maker": "self", "budget_concern": False,
        "key_situation": "Software engineer father, ready to pay, wants best faculty"
    },
    {
        "id": "voice_hot_005", "tier": "HOT", "region": "south",
        "name": "Divya", "city": "Chennai", "state": "Tamil Nadu",
        "class": "dropper", "exam": "NEET", "months_to_exam": 4,
        "decision_maker": "parent_present", "budget_concern": False,
        "key_situation": "Mother on call, missed by 12 marks last year, very motivated"
    },
    {
        "id": "voice_warm_004", "tier": "WARM", "region": "south",
        "name": "Karthik", "city": "Hyderabad", "state": "Telangana",
        "class": "11", "exam": "JEE Main", "months_to_exam": 15,
        "decision_maker": "parent_later", "budget_concern": False,
        "key_situation": "Good engagement, needs parent approval before enrolling"
    },
    {
        "id": "voice_warm_005", "tier": "WARM", "region": "south",
        "name": "Lakshmi", "city": "Kochi", "state": "Kerala",
        "class": "11", "exam": "NEET", "months_to_exam": 14,
        "decision_maker": "self", "budget_concern": True,
        "key_situation": "Interested but comparing with local coaching institutes"
    },
    {
        "id": "voice_cold_002", "tier": "COLD", "region": "south",
        "name": "Suresh", "city": "Thiruvananthapuram", "state": "Kerala",
        "class": "10", "exam": "JEE Main", "months_to_exam": 28,
        "decision_maker": "parent_later", "budget_concern": True,
        "key_situation": "Too early, just checking options, no urgency"
    },
    {
        "id": "voice_cold_003", "tier": "COLD", "region": "south",
        "name": "Meena", "city": "Coimbatore", "state": "Tamil Nadu",
        "class": "11", "exam": "NEET", "months_to_exam": 18,
        "decision_maker": "parent_later", "budget_concern": True,
        "key_situation": "Already enrolled in local institute, just price checking"
    },
    {
        "id": "voice_edge_002", "tier": "HOT", "region": "south",
        "name": "Aditya", "city": "Bangalore", "state": "Karnataka",
        "class": "12", "exam": "JEE Main", "months_to_exam": 5,
        "decision_maker": "self", "budget_concern": True,
        "key_situation": "High urgency + budget concern but decides to enroll — edge case"
    },
]

# ── Voice settings ────────────────────────────────────────────────────────────
def get_voice_config(speaker, region):
    """Return TTS voice config based on speaker and region."""
    if speaker == "agent":
        # Agent is always female, warm voice
        if region == "north":
            return "hi-IN", texttospeech.SsmlVoiceGender.FEMALE, "hi-IN-Chirp3-HD-Aoede"
        else:
            return "en-IN", texttospeech.SsmlVoiceGender.FEMALE, "en-IN-Chirp3-HD-Aoede"
    else:
        # Student voice varies by region
        if region == "north":
            return "hi-IN", texttospeech.SsmlVoiceGender.MALE, "hi-IN-Chirp3-HD-Charon"
        else:
            return "en-IN", texttospeech.SsmlVoiceGender.MALE, "en-IN-Chirp3-HD-Charon"


def generate_tts(text, speaker, region, output_path):
    """Convert text to speech and save as MP3."""
    lang_code, gender, voice_name = get_voice_config(speaker, region)

    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Try specific voice first, fall back to generic
    try:
        voice = texttospeech.VoiceSelectionParams(
            language_code=lang_code,
            name=voice_name
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.95,
            pitch=0.0
        )
        response = tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
    except Exception:
        # Fallback to generic voice
        voice = texttospeech.VoiceSelectionParams(
            language_code=lang_code,
            ssml_gender=gender
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.95
        )
        response = tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

    with open(output_path, "wb") as f:
        f.write(response.audio_content)

    return len(response.audio_content)


def generate_conversation(scenario):
    """Generate realistic conversation text using Claude."""
    region = scenario["region"]
    language_instruction = (
        "Use Hinglish (mix of Hindi and English) — like real North Indian students speak. "
        "Hindi script for Hindi words, English for technical terms. "
        "Example: 'Haan bhaiya, main JEE ki taiyari kar raha hoon. Mujhe lagta hai PW better hai.'"
        if region == "north"
        else
        "Use clear Indian English — like real South Indian students speak. "
        "Formal but warm. Occasional Tamil/Telugu words are fine. Add slight Tamil or Telugu accents to make it sound real"
        "Example: 'Yes, I am currently in Class 12 and targeting JEE Advanced. My father suggested I look at PW.'"
    )

    prompt = """Generate a realistic PhysicsWallah sales call conversation.

SCENARIO:
- Student: {name} from {city}, {state}
- Class: {cls} | Exam: {exam} | Months to exam: {months}
- Decision maker: {decision_maker}
- Budget concern: {budget}
- Situation: {situation}
- Lead tier: {tier}

LANGUAGE: {lang}

AGENT: Priya from PhysicsWallah. Warm, helpful, consultative. NOT pushy.
She asks qualifying questions, listens carefully, recommends the right course.

CONVERSATION REQUIREMENTS:
- 20-30 message turns (alternating agent/student)
- Agent opens with greeting and qualification questions
- Student reveals situation naturally through conversation
- Agent recommends specific PW course based on student profile
- If HOT: student shows strong interest, asks about enrollment
- If WARM: student is interested but has 1-2 hesitations
- If COLD: student is polite but clearly not ready
- If EDGE CASE: show the tension between the conflicting signals. Include case where student is rude and agent handles it gracefully. 
- End naturally (not abruptly)

OUTPUT FORMAT (JSON only, no other text):
{{
  "messages": [
    {{"speaker": "agent", "text": "..."}},
    {{"speaker": "student", "text": "..."}},
    ...
  ]
}}""".format(
        name=scenario["name"],
        city=scenario["city"],
        state=scenario["state"],
        cls=scenario["class"],
        exam=scenario["exam"],
        months=scenario["months_to_exam"],
        decision_maker=scenario["decision_maker"],
        budget=scenario["budget_concern"],
        situation=scenario["key_situation"],
        tier=scenario["tier"],
        lang=language_instruction
    )

    response = claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        temperature=0.8,
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.content[0].text.strip()
    # Clean JSON
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        return json.loads(text[start:end])
    return None


# ── Main pipeline ─────────────────────────────────────────────────────────────
print("=" * 60)
print("WEEK 6: VOICE CONVERSATION GENERATOR")
print("Generating {} conversations".format(len(SCENARIOS)))
print("=" * 60)

results = []

for i, scenario in enumerate(SCENARIOS, 1):
    conv_id = scenario["id"]
    region = scenario["region"]
    tier = scenario["tier"]
    city = scenario["city"]

    print("\n[{}/{}] {} — {} ({}) from {}".format(
        i, len(SCENARIOS), conv_id, tier, region.upper(), city
    ))

    # Create folder for this conversation
    conv_dir = os.path.join(VOICE_DIR, conv_id)
    os.makedirs(conv_dir, exist_ok=True)

    # Step 1: Generate conversation text
    print("   Generating conversation text...", end="", flush=True)
    conv_data = generate_conversation(scenario)

    if not conv_data:
        print(" ❌ FAILED")
        continue

    messages = conv_data["messages"]
    print(" ✅ {} messages".format(len(messages)))

    # Step 2: Generate TTS for each message
    print("   Generating audio ({} messages)...".format(len(messages)), end="", flush=True)
    audio_files = []
    total_size = 0

    for j, msg in enumerate(messages):
        speaker = msg["speaker"]
        text = msg["text"]
        audio_path = os.path.join(conv_dir, "msg_{:03d}_{}.mp3".format(j, speaker))

        try:
            size = generate_tts(text, speaker, region, audio_path)
            total_size += size
            audio_files.append({
                "index": j,
                "speaker": speaker,
                "text": text,
                "audio_file": "msg_{:03d}_{}.mp3".format(j, speaker)
            })
            time.sleep(0.1)  # Avoid rate limiting
        except Exception as e:
            print("\n   ⚠️  TTS failed for message {}: {}".format(j, e))

    print(" ✅ {:.1f}KB total".format(total_size / 1024))

    # Step 3: Save conversation metadata
    metadata = {
        "conversation_id": conv_id,
        "tier": tier,
        "region": region,
        "scenario": scenario,
        "messages": audio_files,
        "total_messages": len(audio_files),
        "language": "hinglish" if region == "north" else "english"
    }

    metadata_path = os.path.join(conv_dir, "conversation.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    results.append({
        "id": conv_id,
        "tier": tier,
        "city": city,
        "messages": len(audio_files),
        "status": "success"
    })

    print("   💾 Saved to: {}".format(conv_dir))
    time.sleep(1)  # Rate limiting between conversations

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("SESSION 1 COMPLETE")
print("Generated {} conversations".format(len(results)))
print("\nSummary:")
for r in results:
    print("  {} — {} ({} messages)".format(r["id"], r["tier"], r["messages"]))
print("\nAll saved to: {}".format(VOICE_DIR))
print("Next: Run session 2 to add STT transcription")
print("=" * 60)