# data_extractor.py
# Extracts structured data from AI conversations using Claude API

import anthropic
import json
import sys

# Import API key
sys.path.append('C:\\Users\\kddipank\\Documents\\Documents\\Personal\\PMCurve\\PW_AI_Capstone')
from config.api_keys import CLAUDE_API_KEY

def extract_data_from_conversation(conversation_json):
    """Extract structured lead data from conversation"""
    
    # Step 1: Create Claude API client
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    
    # Step 2: Convert conversation to readable text format
    # This joins all messages into one string for Claude to analyze
    conv_text = "\n".join([
        f"{msg['speaker'].upper()}: {msg['text']}"
        for msg in conversation_json['messages']
    ])
    
    # Step 3: Create extraction prompt
    # This tells Claude exactly what data to extract and how to format it
    extraction_prompt = f"""Analyze this phone conversation between a PhysicsWallah agent and a student.

CONVERSATION:
{conv_text}

Extract the following information and output ONLY valid JSON with these exact keys:

Fields to extract:
- full_name: Student's full name (string, or null if not mentioned)
- current_class: Which standard/class (must be "9", "10", "11", or "12" as string, or null)
- target_exam: Exam name like "JEE", "NEET", "JEE Main", "JEE Advanced" (string, or null)
- exam_year: Year when they'll take the exam in YYYY format (string like "2026", or null)
- urgency_level: "high", "medium", or "low" based on timeline and student's tone
- budget_concern: true if student mentions budget/cost/money as a concern, false otherwise
- decision_maker: "self" if student can decide alone, "parent" if parents decide, "both" if shared decision
- engagement_level: "high" if asking questions and detailed responses, "medium" if polite but brief, "low" if disengaged

Rules for extraction:
1. Output ONLY the JSON object, no extra text before or after
2. Use null for any field not found in conversation (don't guess)
3. Infer urgency from timeline: exam in <6 months = high, 6-18 months = medium, >18 months = low
4. Infer engagement from: response length, questions asked, enthusiasm shown
5. Be conservative - if unsure, use null

Output format (EXACT):
{{
  "full_name": "...",
  "current_class": "...",
  "target_exam": "...",
  "exam_year": "...",
  "urgency_level": "...",
  "budget_concern": true/false,
  "decision_maker": "...",
  "engagement_level": "..."
}}"""

    # Step 4: Call Claude API
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            temperature=0.3,  # Lower temperature = more consistent/factual
            messages=[{"role": "user", "content": extraction_prompt}]
        )
        
        # Step 5: Get response text
        response_text = response.content[0].text
        
        # Step 6: Extract JSON from response (robust parsing)
        # Sometimes Claude adds text before/after JSON, so we extract just the JSON part
        try:
            # Try direct parsing first
            extracted_data = json.loads(response_text)
        except json.JSONDecodeError:
            # If that fails, find the { } brackets and parse what's inside
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            
            if start == -1 or end == 0:
                print("ERROR: No JSON found in Claude's response")
                print("Response was:", response_text[:200])
                return None
            
            json_text = response_text[start:end]
            extracted_data = json.loads(json_text)
        
        return extracted_data
        
    except Exception as e:
        print(f"ERROR during extraction: {e}")
        return None

if __name__ == "__main__":
    print("="*70)
    print("DATA EXTRACTOR TEST")
    print("="*70)
    
    # Load Week 1 conversation file
    import os
    
    # Update this path to match your actual conversation file
    conv_file = "C:\\Users\\kddipank\\Documents\\Documents\\Personal\\PMCurve\\PW_AI_Capstone\\Data\\Conversations\\conv_20260215_172755.json"
    
    # Check if file exists
    if not os.path.exists(conv_file):
        print(f"\nERROR: Conversation file not found at: {conv_file}")
        print("\nLet me list what files are available...")
        
        conv_dir = "../data/conversations/"
        if os.path.exists(conv_dir):
            files = os.listdir(conv_dir)
            if files:
                print(f"\nAvailable files in {conv_dir}:")
                for f in files:
                    print(f"  • {f}")
                print("\nUpdate 'conv_file' variable to use one of these files.")
            else:
                print(f"\nNo files found in {conv_dir}")
        else:
            print(f"\nDirectory {conv_dir} doesn't exist!")
        
        sys.exit(1)
    
    # Load the conversation
    print(f"\n[STEP 1] Loading conversation from: {conv_file}")
    with open(conv_file, 'r', encoding='utf-8') as f:
        conversation = json.load(f)
    
    num_messages = len(conversation.get('messages', []))
    print(f"✅ Loaded conversation with {num_messages} messages\n")
    
    # Extract data
    print("[STEP 2] Extracting structured data using Claude API...")
    print("(This will take 2-3 seconds)\n")
    
    extracted = extract_data_from_conversation(conversation)
    
    # Display results
    if extracted:
        print("="*70)
        print("✅ EXTRACTION SUCCESSFUL!")
        print("="*70)
        print("\nExtracted Data:")
        print("-"*70)
        
        for key, value in extracted.items():
            # Format nicely with padding
            print(f"  {key:20s} : {value}")
        
        print("-"*70)
        
        # Validate critical fields
        required = ['full_name', 'current_class', 'target_exam']
        missing = [f for f in required if not extracted.get(f)]
        
        if missing:
            print(f"\n⚠️  WARNING: Missing critical fields: {', '.join(missing)}")
            print("   This is OK if the conversation didn't mention these.")
        else:
            print("\n✅ All critical fields present!")
        
        print("\n" + "="*70)
        print("TEST COMPLETE - Data extractor is working!")
        print("="*70)
        
    else:
        print("="*70)
        print("❌ EXTRACTION FAILED")
        print("="*70)
        print("\nCheck the error messages above for details.")