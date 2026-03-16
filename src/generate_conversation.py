# generate_conversation.py - Week 1 Conversation Generator (FIXED VERSION)
# This creates a realistic conversation between agent and student

import anthropic
import json
import re
from datetime import datetime

# Import API key
import sys
sys.path.append('C:\\Users\\kddipank\\Documents\\Documents\\Personal\\PMCurve\\PW_AI_Capstone')
from config.api_keys import CLAUDE_API_KEY

# Create client
client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

# Define the scenario
scenario = {
    'student_name': 'Rites Raman',
    'class': '11th',
    'exam': 'JEE',
    'urgency': 'low',
    'budget_concern': 'True',
    'parent_support': 'False'
}

# Create the system prompt
system_prompt = f"""You are simulating a phone conversation between:
- AGENT: Priya, a sales agent from PhysicsWallah
- STUDENT: {scenario['student_name']}, a {scenario['class']} student interested in {scenario['exam']} coaching

Student Profile:
- Currently in: {scenario['class']} standard
- Target Exam: {scenario['exam']}
- Urgency: {scenario['urgency']}
- Budget Concern: {scenario['budget_concern']}
- Parent Support: {scenario['parent_support']}

Generate a realistic 10-turn conversation (10 agent messages + 10 student responses = 20 total).

The conversation should:
1. Start with agent introducing herself
2. Ask qualifying questions (class, exam, timeline, budget)
3. Student responds naturally (sometimes hesitant, asks questions)
4. Include realistic objections if budget_concern = True
5. Provide scholarship options if budget_concern = True
5. End with next steps

CRITICAL: Output ONLY the JSON, nothing else. No preamble, no explanation.

Format:
{{
  "messages": [
    {{"speaker": "agent", "text": "Good morning! This is Priya from PhysicsWallah. Am I speaking with Rahul?"}},
    {{"speaker": "student", "text": "Yes, this is Rahul."}},
    {{"speaker": "agent", "text": "Great! I understand you're interested in our JEE coaching program. Which class are you currently in?"}},
    {{"speaker": "student", "text": "I'm in 11th standard right now."}}
  ]
}}

Make it feel REAL - natural speech, hesitations, realistic flow."""

# Send request to Claude
print("🎙️  Generating conversation...")
print(f"Scenario: {scenario['student_name']} - {scenario['class']} - {scenario['exam']}")

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4000,
    temperature=0.7,
    system=system_prompt,
    messages=[
        {"role": "user", "content": "Generate the conversation now. Output ONLY the JSON, with no other text."}
    ]
)

# Get the response text
response_text = response.content[0].text

# Debug: Print what we received (first 500 chars)
print("\n📥 Received response from Claude (first 500 chars):")
print(response_text[:500])
print("...")

# Try to extract JSON from the response
# Method 1: Try direct parsing first
try:
    conversation_json = json.loads(response_text)
    print("\n✅ Successfully parsed JSON directly!")
except json.JSONDecodeError:
    print("\n⚠️  Direct parsing failed. Trying to extract JSON...")
    
    # Method 2: Look for JSON between curly braces
    # Find the first { and last }
    try:
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        
        if start != -1 and end > start:
            json_text = response_text[start:end]
            conversation_json = json.loads(json_text)
            print("✅ Successfully extracted and parsed JSON!")
        else:
            print("❌ Could not find JSON in response")
            print("\nFull response:")
            print(response_text)
            sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
        print("\nExtracted text:")
        print(json_text[:500])
        sys.exit(1)

# Verify we have messages
if 'messages' not in conversation_json:
    print("❌ Error: No 'messages' key in JSON")
    print("JSON structure:", list(conversation_json.keys()))
    sys.exit(1)

# Add metadata
conversation = {
    'conversation_id': f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    'timestamp': datetime.now().isoformat(),
    'scenario': scenario,
    'messages': conversation_json['messages'],
    'total_turns': len(conversation_json['messages']),
    'duration_seconds': len(conversation_json['messages']) * 25
}

# Save to file
output_file = f"../data/conversations/{conversation['conversation_id']}.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(conversation, f, indent=2, ensure_ascii=False)

# Display the conversation
print("\n💬 Generated Conversation:\n")
for msg in conversation['messages']:
    speaker_emoji = "🤖" if msg['speaker'] == 'agent' else "👤"
    print(f"{speaker_emoji} {msg['speaker'].upper()}: {msg['text']}\n")

print(f"\n✅ Conversation saved to: {output_file}")
print(f"📊 Total turns: {conversation['total_turns']}")
print(f"⏱️  Estimated duration: {conversation['duration_seconds']} seconds")
