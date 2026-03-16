import sys
import os
import json

PROJECT = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone"
sys.path.append(PROJECT)
sys.path.append(os.path.join(PROJECT, "src"))

from config.api_keys import CLAUDE_API_KEY
from agents.scenario_planner import ScenarioPlanner
from agents.conversation_generator import ConversationGenerator

KB_PATH = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\pw_knowledge_base\pw_knowledge_base.json"

# Generate scenario plan to get hot_018's profile
planner = ScenarioPlanner(KB_PATH)
all_scenarios = planner.generate_all_scenarios()

# Find hot_018
scenario = next((s for s in all_scenarios if s["scenario_id"] == "hot_018"), None)

if not scenario:
    print("hot_018 not found in scenarios")
    sys.exit(1)

print("Scenario: {}".format(scenario))
print("\nGenerating conversation...")

generator = ConversationGenerator(CLAUDE_API_KEY, KB_PATH)
conversation = generator.generate(scenario)

if conversation.get("failed"):
    print("FAILED: {}".format(conversation.get("error")))
else:
    count = len(conversation["messages"])
    print("\nTotal messages: {}".format(count))
    print("First message: {}".format(conversation["messages"][0]["text"][:100]))
    print("Last message: {}".format(conversation["messages"][-1]["text"][:100]))

    if count >= 14:
        print("\n✅ SUCCESS — conversation is long enough")
    else:
        print("\n❌ Still short — {} messages".format(count))