# src/agents/scenario_planner.py
# Agent 1: Scenario Planner
# Job: Design 100 diverse student profiles (33 HOT, 33 WARM, 34 COLD)
# Why separate: Ensures diversity BEFORE generation. If you generate + plan at same time,
# you get repetitive conversations. Separation of concerns = better outputs.

import json
import random


SOUTH_INDIAN_CITIES = {
    "bangalore", "bengaluru", "chennai", "hyderabad", "coimbatore",
    "mysore", "kochi", "thiruvananthapuram", "vizag", "visakhapatnam",
    "madurai", "mangalore", "vijayawada"
}

def get_language_for_city(city):
    return "english" if city.strip().lower() in SOUTH_INDIAN_CITIES else "hindi"


class ScenarioPlanner:

    def __init__(self, knowledge_base_path):
        with open(knowledge_base_path, 'r') as f:
            self.kb = json.load(f)

        demographics = self.kb.get('student_demographics', {})
        self.cities = demographics.get('common_cities', ['Delhi', 'Mumbai', 'Bangalore'])

        names_data = demographics.get('common_names', {})
        self.names = names_data.get('male', []) + names_data.get('female', [])

        if not self.names:
            self.names = ['Rahul', 'Priya', 'Arjun', 'Sneha', 'Vikram']
        if not self.cities:
            self.cities = ['Delhi', 'Mumbai', 'Bangalore']

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
             "urgency_phrase": "I've been watching Alakh sir's videos and want to join"},
            {"class": "dropper", "exam": "JEE Main", "months_to_exam": 5,
             "decision_maker": "self", "budget_concern": False, "engagement": "high",
             "urgency_phrase": "This is my last chance"},
        ]

        for i in range(count):
            template = hot_templates[i % len(hot_templates)]
            city = random.choice(self.cities)
            scenario = {
                "scenario_id":      f"hot_{i+1:03d}",
                "tier":             "HOT",
                "student_name":     random.choice(self.names),
                "city":             city,
                "language":         get_language_for_city(city),
                "class":            template["class"],
                "exam":             template["exam"],
                "months_to_exam":   template["months_to_exam"] + random.randint(-1, 1),
                "decision_maker":   template["decision_maker"],
                "budget_concern":   template["budget_concern"],
                "engagement_level": template["engagement"],
                "key_phrase":       template["urgency_phrase"],
                "course_to_mention": self._pick_relevant_course(template["exam"])
            }
            scenarios.append(scenario)

        return scenarios

    def generate_warm_scenarios(self, count=33):
        scenarios = []

        warm_templates = [
            {"class": "11", "exam": "JEE Main", "months_to_exam": 10,
             "decision_maker": "parent_later", "budget_concern": True, "engagement": "medium",
             "key_phrase": "I'm interested but need to discuss with my parents"},
            {"class": "11", "exam": "NEET", "months_to_exam": 12,
             "decision_maker": "parent_later", "budget_concern": False, "engagement": "medium",
             "key_phrase": "I want to start but not sure about timing"},
            {"class": "12", "exam": "JEE Main", "months_to_exam": 9,
             "decision_maker": "parent_later", "budget_concern": True, "engagement": "medium",
             "key_phrase": "Can you tell me about EMI options?"},
            {"class": "11", "exam": "JEE Advanced", "months_to_exam": 14,
             "decision_maker": "self", "budget_concern": True, "engagement": "medium",
             "key_phrase": "I want to compare a few options first"},
        ]

        for i in range(count):
            template = warm_templates[i % len(warm_templates)]
            city = random.choice(self.cities)
            scenario = {
                "scenario_id":      f"warm_{i+1:03d}",
                "tier":             "WARM",
                "student_name":     random.choice(self.names),
                "city":             city,
                "language":         get_language_for_city(city),
                "class":            template["class"],
                "exam":             template["exam"],
                "months_to_exam":   template["months_to_exam"] + random.randint(-1, 2),
                "decision_maker":   template["decision_maker"],
                "budget_concern":   template["budget_concern"],
                "engagement_level": template["engagement"],
                "key_phrase":       template["key_phrase"],
                "course_to_mention": self._pick_relevant_course(template["exam"])
            }
            scenarios.append(scenario)

        return scenarios

    def generate_cold_scenarios(self, count=34):
        scenarios = []

        cold_templates = [
            {"class": "10", "exam": "JEE Main", "months_to_exam": 24,
             "decision_maker": "parent_later", "budget_concern": True, "engagement": "low",
             "key_phrase": "I'm just looking at options for now"},
            {"class": "11", "exam": "NEET", "months_to_exam": 18,
             "decision_maker": "parent_later", "budget_concern": True, "engagement": "low",
             "key_phrase": "My friend told me to call, I'm not sure I'm ready"},
            {"class": "10", "exam": "JEE Advanced", "months_to_exam": 26,
             "decision_maker": "self", "budget_concern": True, "engagement": "low",
             "key_phrase": "Too expensive, let me think about it"},
            {"class": "11", "exam": "JEE Main", "months_to_exam": 20,
             "decision_maker": "parent_later", "budget_concern": False, "engagement": "low",
             "key_phrase": "I'm exploring, not ready to decide yet"},
        ]

        for i in range(count):
            template = cold_templates[i % len(cold_templates)]
            city = random.choice(self.cities)
            scenario = {
                "scenario_id":      f"cold_{i+1:03d}",
                "tier":             "COLD",
                "student_name":     random.choice(self.names),
                "city":             city,
                "language":         get_language_for_city(city),
                "class":            template["class"],
                "exam":             template["exam"],
                "months_to_exam":   template["months_to_exam"] + random.randint(0, 3),
                "decision_maker":   template["decision_maker"],
                "budget_concern":   template["budget_concern"],
                "engagement_level": template["engagement"],
                "key_phrase":       template["key_phrase"],
                "course_to_mention": self._pick_relevant_course(template["exam"])
            }
            scenarios.append(scenario)

        return scenarios

    def generate_all_scenarios(self):
        hot  = self.generate_hot_scenarios(33)
        warm = self.generate_warm_scenarios(33)
        cold = self.generate_cold_scenarios(34)

        all_scenarios = hot + warm + cold
        random.shuffle(all_scenarios)

        print(f"✅ Scenario Planner: Generated {len(all_scenarios)} scenarios")
        print(f"   HOT: {len(hot)} | WARM: {len(warm)} | COLD: {len(cold)}")

        return all_scenarios

    def generate_scenario(self, call_type="inbound"):
        """
        Generate a single scenario for live demo.
        call_type: "inbound" or "outbound"
        Attributes randomized independently.
        Single differentiator: engagement_level distribution.
        """
        classes         = ["10", "11", "12", "dropper"]
        class_weights   = [0.1, 0.35, 0.35, 0.2]
        exams           = ["JEE Main", "JEE Advanced", "NEET"]
        exam_weights    = [0.4, 0.3, 0.3]
        decision_makers = ["self", "parent_present", "parent_later"]
        dm_weights      = [0.3, 0.2, 0.5]

        if call_type == "inbound":
            engagement_options = ["very_high", "high", "medium"]
            engagement_weights = [0.2, 0.5, 0.3]
        else:
            engagement_options = ["medium", "low", "high"]
            engagement_weights = [0.4, 0.4, 0.2]

        current_class  = random.choices(classes, weights=class_weights, k=1)[0]
        exam           = random.choices(exams, weights=exam_weights, k=1)[0]
        decision_maker = random.choices(decision_makers, weights=dm_weights, k=1)[0]
        engagement     = random.choices(engagement_options, weights=engagement_weights, k=1)[0]
        budget_concern = random.choice([True, False, False])
        months_to_exam = random.randint(3, 24)
        city           = random.choice(self.cities)
        language       = get_language_for_city(city)

        lead_sources = [
            "downloaded our JEE preparation guide",
            "visited our website yesterday",
            "registered for our free webinar",
            "filled out an inquiry form",
            "watched Alakh sir's YouTube video",
        ]

        scenario = {
            "scenario_id":      f"{call_type}_{random.randint(1000, 9999)}",
            "call_type":        call_type,
            "student_name":     random.choice(self.names),
            "city":             city,
            "language":         language,
            "class":            current_class,
            "exam":             exam,
            "months_to_exam":   months_to_exam,
            "decision_maker":   decision_maker,
            "budget_concern":   budget_concern,
            "engagement_level": engagement,
            "key_phrase":       "I want to know more about your courses",
            "lead_source":      random.choice(lead_sources),
            "course_to_mention": self._pick_relevant_course(exam),
        }
        return scenario

    def _pick_relevant_course(self, exam):
        """Pick a relevant course name based on exam type."""
        courses = self.kb.get('courses', {})

        try:
            if 'JEE' in exam:
                jee_courses = courses.get('jee', [])
                return jee_courses[0]['full_name'] if jee_courses else 'JEE Lakshya 2027'
            elif 'NEET' in exam:
                neet_courses = courses.get('neet', [])
                return neet_courses[0]['full_name'] if neet_courses else 'NEET Yakeen 2027'
            else:
                boards = courses.get('boards', [])
                return boards[0]['full_name'] if boards else 'Board Exam Udaan 2026'
        except Exception:
            return 'JEE Lakshya 2027'