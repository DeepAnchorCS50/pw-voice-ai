import os
from google.cloud import texttospeech

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\config\google_credentials.json"

client = texttospeech.TextToSpeechClient()
response = client.list_voices()

print("Available voices for hi-IN and en-IN:\n")

for voice in sorted(response.voices, key=lambda v: v.name):
    if any(lang in voice.language_codes for lang in ["hi-IN", "en-IN"]):
        gender = "FEMALE" if voice.ssml_gender == texttospeech.SsmlVoiceGender.FEMALE else "MALE"
        print("{:<45} {}  {}".format(
            voice.name,
            ", ".join(voice.language_codes),
            gender
        ))