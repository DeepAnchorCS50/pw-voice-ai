# src/create_dataset.py
# Session 3: Convert processed_leads.json → synthetic_leads_dataset.csv
# This is the final artifact that feeds your ML model in Week 5

import json
import csv
import os
from datetime import datetime

def create_dataset(input_path="data/processed_leads.json", 
                   output_path="data/synthetic_leads_dataset.csv"):
    
    print("\n" + "="*60)
    print("SESSION 3: CREATING ML DATASET")
    print("="*60)
    
    # Load processed leads
    with open(input_path, 'r') as f:
        leads = json.load(f)
    
    print(f"\n📂 Loaded {len(leads)} processed leads")
    
    # Filter: only include QA-valid leads
    valid_leads = [l for l in leads if l.get('qa_valid', False)]
    invalid_count = len(leads) - len(valid_leads)
    
    print(f"   ✅ Passing QA: {len(valid_leads)}")
    print(f"   ❌ Failing QA (excluded): {invalid_count}")
    
    if len(valid_leads) < 50:
        print("⚠️  WARNING: Less than 50 valid leads. Dataset may be too small for ML.")
        print("   Consider re-running Session 1 or relaxing QA thresholds.")
    
    # Define columns — these become your ML features + labels
    # DESIGN DECISION: Include scenario_tier (ground truth) AND predicted_tier (system output)
    # This lets you measure how well your scoring aligns with your intended labels
    columns = [
        # Identifiers
        "conversation_id",
        
        # Demographics (ML features)
        "full_name",
        "current_class",
        "target_exam", 
        "exam_year",
        "months_to_exam",
        "location",
        
        # Behavioral signals (ML features — most predictive)
        "urgency_level",
        "budget_concern",
        "decision_maker",
        "engagement_level",
        
        # Scoring output
        "score",
        "predicted_tier",
        
        # Ground truth (for supervised ML training)
        "tier_label",           # This is what Agent 1 designed the scenario as
        
        # Quality metadata (useful for debugging, not ML features)
        "qa_valid",
        "qa_score",
        "extraction_confidence"
    ]
    
    # Write CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        
        for lead in valid_leads:
            # Convert lists to strings for CSV compatibility
            row = {}
            for col in columns:
                value = lead.get(col, '')
                if isinstance(value, list):
                    value = '|'.join(value)  # Join lists with pipe separator
                elif isinstance(value, bool):
                    value = str(value).lower()
                row[col] = value
            
            writer.writerow(row)
    
    print(f"\n📊 Dataset created: {output_path}")
    print(f"   Rows: {len(valid_leads)}")
    print(f"   Columns: {len(columns)}")
    
    # Validate distribution
    print("\n📊 Distribution Check:")
    tier_counts = {}
    for lead in valid_leads:
        tier = lead.get('tier_label', 'unknown')
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    
    for tier, count in sorted(tier_counts.items()):
        pct = count / len(valid_leads) * 100
        bar = "█" * int(pct / 2)
        print(f"   {tier:6}: {count:3} ({pct:.1f}%) {bar}")
    
    # Check balance
    if tier_counts:
        max_count = max(tier_counts.values())
        min_count = min(tier_counts.values())
        imbalance = max_count / max(min_count, 1)
        
        if imbalance > 2.0:
            print(f"\n⚠️  WARNING: Dataset is imbalanced (ratio: {imbalance:.1f}x)")
            print("   Consider adding more scenarios for the minority tier")
        else:
            print(f"\n✅ Distribution is balanced (ratio: {imbalance:.1f}x)")
    
    # Agreement check: Does predicted_tier match tier_label?
    agreements = sum(1 for l in valid_leads 
                    if l.get('predicted_tier') == l.get('tier_label'))
    agreement_rate = agreements / len(valid_leads) * 100
    print(f"\n📊 Scoring Agreement: {agreement_rate:.1f}% of predictions match ground truth")
    
    if agreement_rate < 60:
        print("   ⚠️  Low agreement — review your scoring_engine.py thresholds")
    elif agreement_rate > 85:
        print("   ✅ High agreement — your scoring logic is consistent with scenario design")
    
    print(f"\n{'='*60}")
    print(f"SESSION 3 COMPLETE ✅")
    print(f"  Your ML dataset is ready: {output_path}")
    print(f"  Week 5 will train a Random Forest on this data")
    print(f"{'='*60}\n")
    
    return output_path

if __name__ == "__main__":
    create_dataset()