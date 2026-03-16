import os

# Point to credentials file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\config\google_credentials.json"

print("=" * 60)
print("TESTING GOOGLE CLOUD APIs")
print("=" * 60)

# ── Test 1: Text-to-Speech ────────────────────────────────────────────────────
print("\n[Test 1] Text-to-Speech API...")
try:
    from google.cloud import texttospeech

    client = texttospeech.TextToSpeechClient()

    # Test with a simple Hindi+English sentence (Hinglish)
    text = "Hello! Main Priya bol rahi hoon PhysicsWallah se. Kya aap JEE ki taiyari kar rahe hain?"

    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="hi-IN",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    # Save test audio file
    test_audio_path = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\src\data\test_tts.mp3"
    with open(test_audio_path, "wb") as f:
        f.write(response.audio_content)

    size_kb = len(response.audio_content) / 1024
    print("   ✅ TTS works! Generated {:.1f}KB audio file".format(size_kb))
    print("   Saved to: test_tts.mp3")

except Exception as e:
    print("   ❌ TTS failed: {}".format(e))

# ── Test 2: Speech-to-Text ────────────────────────────────────────────────────
print("\n[Test 2] Speech-to-Text API...")
try:
    from google.cloud import speech

    client = speech.SpeechClient()

    # Use the audio we just generated to test STT
    with open(test_audio_path, "rb") as f:
        audio_content = f.read()

    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=24000,
        language_code="hi-IN",
        alternative_language_codes=["en-IN"],  # Support Hinglish
        enable_automatic_punctuation=True
    )

    response = client.recognize(config=config, audio=audio)

    if response.results:
        transcript = response.results[0].alternatives[0].transcript
        confidence = response.results[0].alternatives[0].confidence
        print("   ✅ STT works!")
        print("   Transcript: {}".format(transcript))
        print("   Confidence: {:.1f}%".format(confidence * 100))
    else:
        print("   ⚠️  STT connected but no transcript returned")
        print("   (This is OK — API is working, audio may need adjustment)")

except Exception as e:
    print("   ❌ STT failed: {}".format(e))

print("\n" + "=" * 60)
print("API TEST COMPLETE")
print("If both show ✅, you are ready to build the voice pipeline.")
print("=" * 60)