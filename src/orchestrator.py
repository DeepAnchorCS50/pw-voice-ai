# src/orchestrator.py
# The Orchestrator: Coordinates all 4 agents
# Job: Run the full pipeline for 100 conversations
# Think of it as a factory manager — knows the process, delegates the work

import json
import os
import sys
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.api_keys import CLAUDE_API_KEY
from agents.scenario_planner import ScenarioPlanner
from agents.conversation_generator import ConversationGenerator

# Paths — adjust if your folder structure is different
KB_PATH = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\pw_knowledge_base\pw_knowledge_base.json"
CONVERSATIONS_DIR = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\src\data\conversations"
CHECKPOINT_FILE = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\src\data\pipeline_checkpoint.json"

def ensure_directories():
    """Create output directories if they don't exist."""
    os.makedirs(CONVERSATIONS_DIR, exist_ok=True)
    os.makedirs("data", exist_ok=True)
    print("✅ Directories ready")

def load_checkpoint():
    """
    Load checkpoint of completed conversations.
    
    WHY checkpointing? If your script runs for 45 minutes and crashes at conversation 80,
    without a checkpoint you restart from 0. With a checkpoint, you resume from 80.
    This is a critical production pattern — always checkpoint long-running pipelines.
    """
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r') as f:
            return json.load(f)
    return {"completed_ids": [], "failed_ids": []}

def save_checkpoint(checkpoint):
    """Save checkpoint after each conversation."""
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump(checkpoint, f, indent=2)

def run_session_1():
    """
    Session 1: Generate all 100 conversations.
    Runs Agent 1 (Scenario Planner) then Agent 2 (Conversation Generator) for each scenario.
    """
    print("\n" + "="*60)
    print("SESSION 1: GENERATING 100 CONVERSATIONS")
    print("="*60)
    
    ensure_directories()
    checkpoint = load_checkpoint()
    already_done = set(checkpoint["completed_ids"])
    
    # --- AGENT 1: Scenario Planner ---
    print("\n[Agent 1] Scenario Planner: Designing 100 student profiles...")
    planner = ScenarioPlanner(KB_PATH)
    all_scenarios = planner.generate_all_scenarios()
    
    # Filter out already-completed scenarios (checkpoint resume)
    pending = [s for s in all_scenarios if s["scenario_id"] not in already_done]
    print(f"   Pending: {len(pending)} | Already done: {len(already_done)}")
    
    # --- AGENT 2: Conversation Generator ---
    print(f"\n[Agent 2] Conversation Generator: Writing {len(pending)} conversations...")
    generator = ConversationGenerator(CLAUDE_API_KEY, KB_PATH)
    
    success_count = 0
    fail_count = 0
    
    for i, scenario in enumerate(pending, 1):
        total = len(pending)
        print(f"  [{i}/{total}] Generating: {scenario['scenario_id']} ({scenario['tier']}) — {scenario['student_name']} from {scenario['city']}", end="")
        
        # Generate conversation
        conversation = generator.generate(scenario)
        
        if conversation.get("failed"):
            print(f" ❌ FAILED: {conversation.get('error', 'Unknown error')}")
            checkpoint["failed_ids"].append(scenario["scenario_id"])
            fail_count += 1
        else:
            # Save conversation to file
            filepath = os.path.join(CONVERSATIONS_DIR, f"{scenario['scenario_id']}.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(conversation, f, indent=2, ensure_ascii=False)
            
            print(f" ✅ ({len(conversation['messages'])} turns)")
            checkpoint["completed_ids"].append(scenario["scenario_id"])
            success_count += 1
        
        # Save checkpoint every 10 conversations
        if i % 10 == 0:
            save_checkpoint(checkpoint)
            print(f"\n  💾 Checkpoint saved ({i} processed)\n")
    
    # Final checkpoint
    save_checkpoint(checkpoint)
    
    print(f"\n{'='*60}")
    print(f"SESSION 1 COMPLETE")
    print(f"  ✅ Generated: {success_count} conversations")
    print(f"  ❌ Failed: {fail_count} conversations")
    print(f"  📁 Saved to: {CONVERSATIONS_DIR}/")
    print(f"{'='*60}\n")
    
    return success_count, fail_count
def run_session_2():
    """
    Session 2: Extract data and score all 100 conversations.
    Runs Agent 3 (Extractor) + existing scoring_engine + Agent 4 (QA Validator).
    """
    print("\n" + "="*60)
    print("SESSION 2: EXTRACTING DATA + SCORING")
    print("="*60)
    
    # Import agents
    from agents.extractor_agent import ExtractorAgent
    from agents.qa_validator import QAValidator
    
    # Import your existing Week 2 scoring engine (function-based)
    sys.path.append('src')
    from scoring_engine import calculate_lead_score
    
    # Load all generated conversations
    conv_files = [f for f in os.listdir(CONVERSATIONS_DIR) if f.endswith('.json')]
    print(f"\n📂 Found {len(conv_files)} conversation files")
    
    if len(conv_files) == 0:
        print("❌ No conversations found! Run Session 1 first.")
        return []
    
    extractor = ExtractorAgent(CLAUDE_API_KEY)
    validator = QAValidator()
    # No need to instantiate — calculate_lead_score is a plain function
    
    all_leads = []
    
    print(f"\n[Agent 3] Extracting data from {len(conv_files)} conversations...")
    
    for i, filename in enumerate(conv_files, 1):
        filepath = os.path.join(CONVERSATIONS_DIR, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            conversation = json.load(f)
        
        # Extract
        print(f"  [{i}/{len(conv_files)}] Extracting: {conversation['conversation_id']}", end="")
        extracted = extractor.extract(conversation)
        
        # Score using your Week 2 engine
        try:
            score_result = calculate_lead_score(extracted)
            extracted['score'] = score_result.get('score', 0)
            extracted['predicted_tier'] = score_result.get('tier', 'COLD')
            extracted['score_breakdown'] = score_result.get('breakdown', {})
        except Exception as e:
            extracted['score'] = 0
            extracted['predicted_tier'] = 'COLD'
            extracted['score_breakdown'] = {}
            print(f" ⚠️  Scoring error: {e}", end="")
        
        all_leads.append(extracted)
        print(f" ✅ Score: {extracted.get('score', 0)}/100 → {extracted.get('predicted_tier')}")
        
        # Rate limit
        import time
        time.sleep(0.3)
    
    # QA Validate all leads
    print(f"\n[Agent 4] QA Validating {len(all_leads)} leads...")
    validation_results = validator.validate_batch(all_leads)
    
    # Attach validation to each lead
    val_dict = {v['conversation_id']: v for v in validation_results}
    for lead in all_leads:
        val = val_dict.get(lead['conversation_id'], {})
        lead['qa_valid'] = val.get('is_valid', False)
        lead['qa_score'] = val.get('quality_score', 0)
        lead['qa_issues'] = val.get('issues', [])
    
    # Save processed leads
    with open(r'C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\src\data\processed_leads.json', 'w') as f:
        json.dump(all_leads, f, indent=2)
    
    valid_count = sum(1 for l in all_leads if l.get('qa_valid'))
    print(f"\n{'='*60}")
    print(f"SESSION 2 COMPLETE")
    print(f"  📊 Processed: {len(all_leads)} leads")
    print(f"  ✅ Valid (pass QA): {valid_count}")
    print(f"  ❌ Invalid (fail QA): {len(all_leads) - valid_count}")
    print(f"  💾 Saved: data/processed_leads.json")
    print(f"{'='*60}\n")
    
    return all_leads

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='PW Lead Scoring Pipeline')
    parser.add_argument('--session', type=int, choices=[1, 2, 3], 
                        help='Which session to run (1, 2, or 3)')
    args = parser.parse_args()
    
    print("\n🚀 PW Lead Scoring — Week 3 Pipeline")
    print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    if args.session == 1 or not args.session:
        run_session_1()
    if args.session == 2:
        run_session_2()