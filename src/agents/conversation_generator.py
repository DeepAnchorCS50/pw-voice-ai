# src/agents/conversation_generator.py
# Agent 2: Conversation Generator
# Job: Take a scenario (who the student is) and write a realistic conversation
# Why separate from Scenario Planner: Planning diversity ≠ writing dialogue.
# These are different skills. An architect designs a house; a builder constructs it.

# src/agents/conversation_generator.py
import anthropic
import json
import time


class ConversationGenerator:

    def __init__(self, api_key, knowledge_base_path):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"

        with open(knowledge_base_path, 'r') as f:
            self.kb = json.load(f)

        self.pw_context = self._build_pw_context()

    def _build_pw_context(self):
        """Build a concise context string from the knowledge base."""
        courses = self.kb.get('courses', {})

        course_summary = ""
        for category, course_list in courses.items():
            for course in course_list[:2]:
                name = course.get('full_name', course.get('name', 'Unknown'))
                price = course.get('pricing', {}).get('discounted_price', 'N/A')
                emi = course.get('pricing', {}).get('emi_monthly', 'N/A')
                course_summary += f"- {name}: {price} rupees (EMI: {emi} rupees/month)\n"

        objections = self.kb.get('objection_handling_context', {})
        price_response = objections.get('pricing_objections', {}).get(
            'emi_pitch', 'We have EMI options available to make it affordable.'
        )

        return f"""
PhysicsWallah (PW) is India's leading affordable EdTech platform.
Key courses (mention naturally if relevant):
{course_summary}
If student mentions price concern: "{price_response}"
Agent name: Priya (friendly, helpful, not pushy)
Language: Follow the language instruction provided in the student profile below.
"""

    def generate(self, scenario):
        """Generate one conversation from a scenario."""
        engagement_instructions = {
            "very_high": "Student is extremely enthusiastic, asks detailed questions, ready to enroll",
            "high": "Student is genuinely interested, engages well, has 1-2 questions",
            "medium": "Student is interested but cautious, needs some convincing, asks about alternatives",
            "low": "Student is hesitant, gives short answers, has multiple objections, not in a rush"
        }

        engagement = scenario.get("engagement_level", "medium")
        engagement_guide = engagement_instructions.get(engagement, engagement_instructions["medium"])

        decision_scripts = {
            "self": "Student can make the decision independently on the call",
            "parent_present": "Parent is also on the call and asks questions too",
            "parent_later": "Student needs to check with parents before deciding, asks to call back"
        }
        decision_guide = decision_scripts.get(
            scenario.get("decision_maker", "parent_later"),
            decision_scripts["parent_later"]
        )

        # Determine call type and opening
        call_type   = scenario.get("call_type", "inbound")
        lead_source = scenario.get("lead_source", "visited our website")

        if call_type == "inbound":
            opening_instruction = "Agent ANSWERS the call: \"Namaste! Thank you for calling PhysicsWallah. This is Priya, how can I help you today?\""
        else:
            opening_instruction = f"Agent INITIATES the call: \"Hi, am I speaking with {scenario['student_name']}? This is Priya from PhysicsWallah. I noticed you {lead_source} — wanted to reach out and see how I can help.\""

        prompt = f"""You are simulating a real phone sales call between:
- AGENT: Priya from PhysicsWallah sales team
- STUDENT: {scenario['student_name']} from {scenario['city']}
- CALL TYPE: {call_type.upper()} — {opening_instruction}

{self.pw_context}

STUDENT PROFILE (don't reveal this explicitly — let it emerge naturally in conversation):
- Language: {"Speak primarily in Hindi with natural English mixing (Hinglish). Agent mirrors student's language." if scenario.get('language','hindi') == 'hindi' else "Speak primarily in English. Agent mirrors student's language."}
- Currently in: Class {scenario['class']}
- Target exam: {scenario['exam']}
- Months until exam: {scenario['months_to_exam']} months
- Budget concern: {'Yes, will ask about pricing' if scenario['budget_concern'] else 'No significant concern'}
- Decision authority: {decision_guide}
- Engagement style: {engagement_guide}
- The student should naturally say something like: "{scenario['key_phrase']}"

CONVERSATION RULES:
1. Generate exactly 20 messages (8 to 12 agent + 8 to 12 student alternating)
2. Start with the agent's opening line as specified above (inbound vs outbound)
3. Agent should collect: name, class, exam, timeline, budget, decision authority
4. Make it feel like a REAL call — natural pauses, use the language from the student profile above
5. Student should NOT volunteer all information immediately — agent must ask
6. Inbound: student has a specific question — agent discovers it naturally
7. Outbound: student may be surprised by the call — agent earns their interest
8. When mentioning prices, write them in English words only (e.g., "4999 rupees" or "4,999 rupees"). Never use ₹ symbol or Hindi number words.
9. When mentioning phone numbers, write them with spaces between every digit (e.g., "9 8 7 6 5 4 3 2 1 0") so they are spoken clearly.

Output ONLY valid JSON, nothing else:
{{
  "messages": [
    {{"speaker": "agent", "text": "..."}},
    {{"speaker": "student", "text": "..."}}
  ]
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=7000,
                temperature=0.8,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text.strip()

            try:
                conversation_data = json.loads(response_text)
            except json.JSONDecodeError:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                if start != -1 and end > start:
                    conversation_data = json.loads(response_text[start:end])
                else:
                    raise ValueError("No valid JSON found in response")

            result = {
                "conversation_id": scenario["scenario_id"],
                "scenario": scenario,
                "messages": conversation_data["messages"],
                "total_turns": len(conversation_data["messages"]),
                "tier_label": scenario.get("tier", "UNKNOWN")
            }

            time.sleep(0.5)

            return result

        except Exception as e:
            return {
                "conversation_id": scenario["scenario_id"],
                "scenario": scenario,
                "messages": [],
                "tier_label": scenario.get("tier", "UNKNOWN"),
                "error": str(e),
                "failed": True
            }