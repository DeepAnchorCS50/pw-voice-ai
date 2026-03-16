# test_week7.py
# Tests scenario planner + conversation generator with inbound/outbound
# Run from project root: python test_week7.py

import sys
import os
sys.path.insert(0, 'src')

from agents.scenario_planner import ScenarioPlanner

ROOT    = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone"
KB_PATH = os.path.join(ROOT, "pw_knowledge_base", "pw_knowledge_base.json")

p = ScenarioPlanner(KB_PATH)

print("=== INBOUND SCENARIO ===")
s = p.generate_scenario('inbound')
print(f"  Name:        {s['student_name']}")
print(f"  City:        {s['city']}")
print(f"  Class:       {s['class']}")
print(f"  Exam:        {s['exam']}")
print(f"  Engagement:  {s['engagement_level']}")
print(f"  Call type:   {s['call_type']}")

print("\n=== OUTBOUND SCENARIO ===")
s2 = p.generate_scenario('outbound')
print(f"  Name:        {s2['student_name']}")
print(f"  City:        {s2['city']}")
print(f"  Class:       {s2['class']}")
print(f"  Exam:        {s2['exam']}")
print(f"  Engagement:  {s2['engagement_level']}")
print(f"  Call type:   {s2['call_type']}")
print(f"  Lead source: {s2['lead_source']}")

print("\n✅ Scenario planner OK")
print("\nNow testing conversation generator (1 inbound call)...")
print("This will take ~15 seconds...")

from config.api_keys import CLAUDE_API_KEY
from agents.conversation_generator import ConversationGenerator

gen  = ConversationGenerator(CLAUDE_API_KEY, KB_PATH)
conv = gen.generate(s)

if conv.get("failed"):
    print(f"❌ Generator failed: {conv.get('error')}")
else:
    msgs = conv.get("messages", [])
    print(f"✅ Generated {len(msgs)} messages")
    print(f"\nFirst 3 messages:")
    for msg in msgs[:3]:
        speaker = msg['speaker'].upper()
        text    = msg['text'][:80]
        print(f"  [{speaker}] {text}...")