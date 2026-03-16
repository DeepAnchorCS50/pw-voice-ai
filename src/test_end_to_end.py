# test_end_to_end.py
# Tests complete pipeline: Conversation → Extraction → Scoring

import json
import sys
sys.path.append('C:\\Users\\kddipank\\Documents\\Documents\\Personal\\PMCurve\\PW_AI_Capstone')

# Import our modules
from data_extractor import extract_data_from_conversation
from scoring_engine import calculate_lead_score

def test_full_pipeline(conversation_file):
    """Test the complete end-to-end pipeline"""
    
    print("="*70)
    print("END-TO-END PIPELINE TEST")
    print("="*70)
    
    # ================================================================
    # STEP 1: Load Conversation
    # ================================================================
    print("\n[STEP 1/4] Loading conversation file...")
    
    try:
        with open(conversation_file, 'r', encoding='utf-8') as f:
            conversation = json.load(f)
        
        num_messages = len(conversation.get('messages', []))
        print(f"✅ Loaded conversation with {num_messages} messages")
        
    except FileNotFoundError:
        print(f"❌ ERROR: File not found: {conversation_file}")
        return None
    except Exception as e:
        print(f"❌ ERROR loading file: {e}")
        return None
    
    # ================================================================
    # STEP 2: Extract Data
    # ================================================================
    print("\n[STEP 2/4] Extracting structured data...")
    print("(Calling Claude API - this takes 2-3 seconds)")
    
    extracted = extract_data_from_conversation(conversation)
    
    if not extracted:
        print("❌ Extraction failed!")
        return None
    
    print("✅ Extraction successful!\n")
    print("Extracted Fields:")
    print("-" * 70)
    for key, value in extracted.items():
        print(f"  {key:20s} : {value}")
    print("-" * 70)
    
    # ================================================================
    # STEP 3: Calculate Score
    # ================================================================
    print("\n[STEP 3/4] Calculating lead score...")
    
    scored = calculate_lead_score(extracted)
    
    print("✅ Scoring successful!\n")
    print(f"Final Score: {scored['score']}/100")
    print(f"Tier:        {scored['tier']}\n")
    
    print("Score Breakdown:")
    print("-" * 70)
    for factor, points in scored['breakdown'].items():
        factor_name = factor.replace('_', ' ').title()
        print(f"  {factor_name:25s} : {points:2d} points")
    print("-" * 70)
    
    # ================================================================
    # STEP 4: Prepare Final Result
    # ================================================================
    print("\n[STEP 4/4] Preparing data for export...")
    
    # Combine all data into one dictionary
    final_result = {
        # Metadata from conversation
        'conversation_id': conversation.get('conversation_id', 'unknown'),
        'timestamp': conversation.get('timestamp', ''),
        
        # Extracted fields
        'full_name': extracted.get('full_name'),
        'current_class': extracted.get('current_class'),
        'target_exam': extracted.get('target_exam'),
        'exam_year': extracted.get('exam_year'),
        'urgency_level': extracted.get('urgency_level'),
        'budget_concern': extracted.get('budget_concern'),
        'decision_maker': extracted.get('decision_maker'),
        'engagement_level': extracted.get('engagement_level'),
        
        # Scoring results
        'score': scored['score'],
        'tier': scored['tier'],
        
        # Score breakdown
        'timeline_urgency': scored['breakdown'].get('timeline_urgency'),
        'class_relevance': scored['breakdown'].get('class_relevance'),
        'decision_authority': scored['breakdown'].get('decision_authority'),
        'budget_fit': scored['breakdown'].get('budget_fit'),
        'engagement_score': scored['breakdown'].get('engagement_level'),
        
        # Reasoning
        'reasoning': scored['reasoning']
    }
    
    print(f"✅ Data prepared - {len(final_result)} fields ready")
    
    return final_result


if __name__ == "__main__":
    # Test with your Week 1 conversation
    # UPDATE THIS PATH to match your actual file
    conv_file = "C:\\Users\\kddipank\\Documents\\Documents\\Personal\\PMCurve\\PW_AI_Capstone\\Data\\Conversations\\conv_20260215_172755.json"
    
    print("\nTesting with conversation file:")
    print(f"  {conv_file}\n")
    
    result = test_full_pipeline(conv_file)
    
    if result:
        print("\n" + "="*70)
        print("✅ END-TO-END PIPELINE TEST SUCCESSFUL!")
        print("="*70)
        
        print(f"\nFinal Result Summary:")
        print(f"  Student:    {result['full_name']}")
        print(f"  Class:      {result['current_class']}")
        print(f"  Exam:       {result['target_exam']} ({result['exam_year']})")
        print(f"  Score:      {result['score']}/100")
        print(f"  Tier:       {result['tier']}")
        
        print("\n✅ System is ready to process leads!")
        print("✅ Data format is ready for Google Sheets!")
        
    else:
        print("\n" + "="*70)
        print("❌ PIPELINE TEST FAILED")
        print("="*70)
        print("Check the error messages above for details.")