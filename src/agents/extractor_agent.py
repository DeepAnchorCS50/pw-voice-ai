# src/agents/extractor_agent.py
# Agent 3: Extractor
# Job: Pull structured lead data from a conversation
# Why separate from scoring: Extraction is a reading task. Scoring is a judgment task.
# Keeping them separate means you can improve extraction without changing scoring logic.

import anthropic
import json
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ExtractorAgent:
    """
    Extracts structured data from raw conversation text.
    
    Product insight: This agent is your "structured data factory."
    Unstructured conversation → structured fields that ML can learn from.
    The quality of extraction directly impacts ML model quality.
    Garbage in = garbage out.
    """
    
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
    
    def extract(self, conversation):
        """
        Extract structured fields from a conversation.
        
        Returns: dict with extracted fields + confidence metadata
        """
        
        # Convert messages to readable text
        conv_text = "\n".join([
            f"{msg['speaker'].upper()}: {msg['text']}"
            for msg in conversation.get('messages', [])
        ])
        
        if not conv_text.strip():
            return self._empty_extraction(conversation["conversation_id"], "Empty conversation")
        
        prompt = f"""Extract lead qualification data from this PhysicsWallah sales call transcript.

TRANSCRIPT:
{conv_text}

Extract these fields. If a field is not mentioned, use "unknown" or false as appropriate.

Output ONLY valid JSON:
{{
  "full_name": "student's full name or first name",
  "current_class": "10/11/12/dropper",
  "target_exam": "JEE Main/JEE Advanced/NEET/Boards/Other",
  "exam_year": "2025/2026/2027/2028 — infer from class + months if not stated",
  "months_to_exam": <number or 0 if unknown>,
  "location": "city name or unknown",
  "urgency_level": "high/medium/low",
  "budget_concern": <true or false>,
  "decision_maker": "self/parent_present/parent_later/unknown",
  "engagement_level": "high/medium/low",
  "objections_raised": ["list", "of", "objections"] or [],
  "interested_in_course": "course name mentioned or unknown",
  "extraction_confidence": "high/medium/low"
}}"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=600,
                temperature=0.1,  # Low temperature — we want consistent, factual extraction
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            
            try:
                extracted = json.loads(response_text)
            except json.JSONDecodeError:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                extracted = json.loads(response_text[start:end])
            
            # Add metadata
            extracted["conversation_id"] = conversation["conversation_id"]
            extracted["tier_label"] = conversation.get("tier_label", "unknown")
            extracted["extraction_success"] = True
            
            return extracted
            
        except Exception as e:
            return self._empty_extraction(conversation["conversation_id"], str(e))
    
    def _empty_extraction(self, conv_id, reason):
        """Return a safe empty extraction on failure."""
        return {
            "conversation_id": conv_id,
            "full_name": "unknown",
            "current_class": "unknown",
            "target_exam": "unknown",
            "exam_year": "unknown",
            "months_to_exam": 0,
            "location": "unknown",
            "urgency_level": "low",
            "budget_concern": False,
            "decision_maker": "unknown",
            "engagement_level": "low",
            "objections_raised": [],
            "interested_in_course": "unknown",
            "extraction_confidence": "low",
            "tier_label": "unknown",
            "extraction_success": False,
            "extraction_error": reason
        }