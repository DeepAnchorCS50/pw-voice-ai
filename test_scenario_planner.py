# patch_scenario_planner.py
# Adds generate_scenario(call_type) method to scenario_planner.py
# Run from project root: python patch_scenario_planner.py

PLANNER_PATH = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\src\agents\scenario_planner.py"

NEW_METHOD = '''
    def generate_scenario(self, call_type="inbound"):
        """
        Generate a single scenario for live demo.
        call_type: "inbound" or "outbound"
        Attributes randomized independently.
        Single differentiator: engagement_level distribution.
        """
        # Independent attribute pools
        classes         = ["10", "11", "12", "dropper"]
        class_weights   = [0.1, 0.35, 0.35, 0.2]
        exams           = ["JEE Main", "JEE Advanced", "NEET"]
        exam_weights    = [0.4, 0.3, 0.3]
        decision_makers = ["self", "parent_present", "parent_later"]
        dm_weights      = [0.3, 0.2, 0.5]

        # Engagement skews by call type
        if call_type == "inbound":
            engagement_options = ["very_high", "high", "medium"]
            engagement_weights = [0.2, 0.5, 0.3]
        else:  # outbound
            engagement_options = ["medium", "low", "high"]
            engagement_weights = [0.4, 0.4, 0.2]

        # Sample attributes independently
        current_class  = random.choices(classes, weights=class_weights, k=1)[0]
        exam           = random.choices(exams, weights=exam_weights, k=1)[0]
        decision_maker = random.choices(decision_makers, weights=dm_weights, k=1)[0]
        engagement     = random.choices(engagement_options, weights=engagement_weights, k=1)[0]
        budget_concern = random.choice([True, False, False])  # 33% chance
        months_to_exam = random.randint(3, 24)

        lead_sources = [
            "downloaded our JEE preparation guide",
            "visited our website yesterday",
            "registered for our free webinar",
            "filled out an inquiry form",
            "watched Alakh sir\'s YouTube video",
        ]

        scenario = {
            "scenario_id":      f"{call_type}_{random.randint(1000, 9999)}",
            "call_type":        call_type,
            "student_name":     random.choice(self.names),
            "city":             random.choice(self.cities),
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

'''

# Read file
with open(PLANNER_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Check if already patched
if "def generate_scenario" in content:
    print("Already patched — generate_scenario method already exists.")
else:
    # Insert before _pick_relevant_course
    insert_before = "    def _pick_relevant_course(self, exam):"
    if insert_before not in content:
        print("ERROR: Could not find insertion point. Check file manually.")
    else:
        new_content = content.replace(insert_before, NEW_METHOD + insert_before)
        with open(PLANNER_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("SUCCESS: generate_scenario method added to scenario_planner.py")

# Verify
with open(PLANNER_PATH, "r", encoding="utf-8") as f:
    verify = f.read()

if "def generate_scenario" in verify:
    print("Verified: method is present in file.")
else:
    print("ERROR: Method not found after patching.")