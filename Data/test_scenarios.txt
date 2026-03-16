import os

# ── Correct paths based on your actual folder structure ──────────────────────
PROJECT = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone"
KB_PATH = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\pw_knowledge_base\pw_knowledge_base.json"
CONV_DIR = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\Data\Conversations"

# ── Create folders ────────────────────────────────────────────────────────────
os.makedirs(os.path.join(PROJECT, "src", "agents"), exist_ok=True)
os.makedirs(os.path.join(PROJECT, "Data", "Conversations"), exist_ok=True)
open(os.path.join(PROJECT, "src", "agents", "__init__.py"), "w").close()

# ── scenario_planner.py ───────────────────────────────────────────────────────
with open(os.path.join(PROJECT, "src", "agents", "scenario_planner.py"), "w") as f:
    f.write('''import json
import random

class ScenarioPlanner:

    def __init__(self, knowledge_base_path):
        with open(knowledge_base_path, "r") as f:
            self.kb = json.load(f)
        demographics = self.kb.get("student_demographics", {})
        self.cities = demographics.get("common_cities", ["Delhi", "Mumbai", "Bangalore"])
        names_data = demographics.get("common_names", {})
        self.names = names_data.get("male", []) + names_data.get("female", [])
        if not self.names:
            self.names = ["Rahul", "Priya", "Arjun", "Sneha", "Vikram"]
        if not self.cities:
            self.cities = ["Delhi", "Mumbai", "Bangalore"]

    def generate_hot_scenarios(self, count=33):
        scenarios = []
        hot_templates = [
            {"class": "12", "exam": "JEE Main", "months_to_exam": 3,
             "decision_maker": "self", "budget_concern": False, "engagement": "high",
             "urgency_phrase": "I need to enroll this week"},
            {"class": "dropper", "exam": "NEET", "months_to_exam": 5,
             "decision_maker": "self", "budget_concern": False, "engagement": "high",
             "urgency_phrase": "I failed last year and must crack it this time"},
            {"class": "12", "exam": "JEE Advanced", "months_to_exam": 4,
             "decision_maker": "parent_present", "budget_concern": False, "engagement": "high",
             "urgency_phrase": "My parents want me to start immediately"},
            {"class": "12", "exam": "NEET", "months_to_exam": 6,
             "decision_maker": "self", "budget_concern": False, "engagement": "very_high",
             "urgency_phrase": "I have been watching Alakh sir videos and want to join"},
            {"class": "dropper", "exam": "JEE Main", "months_to_exam": 5,
             "decision_maker": "self", "budget_concern": False, "engagement": "high",
             "urgency_phrase": "This is my last chance"},
        ]
        for i in range(count):
            template = hot_templates[i % len(hot_templates)]
            scenario = {
                "scenario_id": f"hot_{i+1:03d}",
                "tier": "HOT",
                "student_name": random.choice(self.names),
                "city": random.choice(self.cities),
                "class": template["class"],
                "exam": template["exam"],
                "months_to_exam": template["months_to_exam"] + random.randint(-1, 1),
                "decision_maker": template["decision_maker"],
                "budget_concern": template["budget_concern"],
                "engagement_level": template["engagement"],
                "key_phrase": template["urgency_phrase"],
                "course_to_mention": self._pick_relevant_course(template["exam"])
            }
            scenarios.append(scenario)
        return scenarios

    def generate_warm_scenarios(self, count=33):
        scenarios = []
        warm_templates = [
            {"class": "11", "exam": "JEE Main", "months_to_exam": 10,
             "decision_maker": "parent_later", "budget_concern": True, "engagement": "medium",
             "key_phrase": "I am interested but need to discuss with my parents"},
            {"class": "11", "exam": "NEET", "months_to_exam": 12,
             "decision_maker": "parent_later", "budget_concern": False, "engagement": "medium",
             "key_phrase": "I want to start but not sure about timing"},
            {"class": "12", "exam": "JEE Main", "months_to_exam": 9,
             "decision_maker": "parent_later", "budget_concern": True, "engagement": "medium",
             "key_phrase": "Can you tell me about EMI options"},
            {"class": "11", "exam": "JEE Advanced", "months_to_exam": 14,
             "decision_maker": "self", "budget_concern": True, "engagement": "medium",
             "key_phrase": "I want to compare a few options first"},
        ]
        for i in range(count):
            template = warm_templates[i % len(warm_templates)]
            scenario = {
                "scenario_id": f"warm_{i+1:03d}",
                "tier": "WARM",
                "student_name": random.choice(self.names),
                "city": random.choice(self.cities),
                "class": template["class"],
                "exam": template["exam"],
                "months_to_exam": template["months_to_exam"] + random.randint(-1, 2),
                "decision_maker": template["decision_maker"],
                "budget_concern": template["budget_concern"],
                "engagement_level": template["engagement"],
                "key_phrase": template["key_phrase"],
                "course_to_mention": self._pick_relevant_course(template["exam"])
            }
            scenarios.append(scenario)
        return scenarios

    def generate_cold_scenarios(self, count=34):
        scenarios = []
        cold_templates = [
            {