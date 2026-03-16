# test_session1.py — Quick test: generate just 3 conversations
import sys, os
sys.path.append('src')

from config.api_keys import CLAUDE_API_KEY
from agents.scenario_planner import ScenarioPlanner
from agents.conversation_generator import ConversationGenerator

KB_PATH = "pw_knowledge_base/pw_knowledge_base.json"

# Generate 3 scenarios (1 of each tier)
planner = ScenarioPlanner(KB_PATH)
scenarios = [
    planner.generate_hot_scenarios(1)[0],    # 1 HOT
    planner.generate_warm_scenarios(1)[0],   # 1 WARM
    planner.generate_cold_scenarios(1)[0],   # 1 COLD
]

print(f"Generated {len(scenarios)} test scenarios")

# Generate conversations
generator = ConversationGenerator(CLAUDE_API_KEY, KB_PATH)

for scenario in scenarios:
    print(f"\n--- Testing: {scenario['scenario_id']} ({scenario['tier']}) ---")
    conv = generator.generate(scenario)
    
    if conv.get("failed"):
        print(f"❌ FAILED: {conv['error']}")
    else:
        print(f"✅ SUCCESS: {len(conv['messages'])} messages")
        # Print first 2 exchanges
        for msg in conv['messages'][:4]:
            emoji = "🤖" if msg['speaker'] == 'agent' else "👤"
            print(f"  {emoji} {msg['speaker'].upper()}: {msg['text'][:80]}...")