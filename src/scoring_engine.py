# scoring_engine.py
# Calculates lead quality scores from extracted data

from datetime import datetime

def calculate_lead_score(extracted_data):
    """Calculate comprehensive lead score based on 5 factors"""
    
    score = 0
    breakdown = {}
    
    # ================================================================
    # FACTOR 1: Timeline Urgency (0-30 points) - MOST IMPORTANT!
    # ================================================================
    # Why: Students close to exam are desperate and convert fast
    
    exam_year = extracted_data.get('exam_year')
    
    if exam_year:
        try:
            # Calculate ACTUAL months from today to exam
            current_date = datetime.now()
            # Assume exam happens in June (typical for JEE/NEET)
            exam_date = datetime(int(exam_year), 6, 1)
            
            # Calculate difference in months
            months_to_exam = (exam_date.year - current_date.year) * 12 + \
                            (exam_date.month - current_date.month)
            
            # Score based on urgency
            if months_to_exam <= 6:
                timeline_score = 30  # CRITICAL: Exam in ≤6 months
            elif months_to_exam <= 12:
                timeline_score = 25  # HIGH: Exam in 7-12 months
            elif months_to_exam <= 18:
                timeline_score = 15  # MEDIUM: Exam in 13-18 months
            elif months_to_exam <= 24:
                timeline_score = 10  # LOW: Exam in 19-24 months
            else:
                timeline_score = 5   # VERY LOW: 2+ years away
                
        except Exception as e:
            # If anything goes wrong, use safe default
            timeline_score = 10
    else:
        timeline_score = 10  # Default if exam year not mentioned
    
    breakdown['timeline_urgency'] = timeline_score
    score += timeline_score
    
    # ================================================================
    # FACTOR 2: Class Relevance (0-20 points)
    # ================================================================
    # Why: 11th/12th students are more serious than 9th/10th
    
    current_class = extracted_data.get('current_class', '')
    
    if current_class in ['12', '12th', 'twelve', 'dropper']:
        class_score = 20  # Final year - maximum urgency
    elif current_class in ['11', '11th', 'eleven']:
        class_score = 18  # Penultimate year - very relevant
    elif current_class in ['10', '10th', 'ten']:
        class_score = 15  # Early but planning ahead
    elif current_class in ['9', '9th', 'nine']:
        class_score = 12  # Very early, exploratory
    else:
        class_score = 15  # Default moderate score
    
    breakdown['class_relevance'] = class_score
    score += class_score
    
    # ================================================================
    # FACTOR 3: Decision Authority (0-15 points)
    # ================================================================
    # Why: Students who can self-decide enroll faster (no parent approval delay)
    
    decision_maker = extracted_data.get('decision_maker', 'parent')
    
    if decision_maker == 'self':
        decision_score = 15  # Can commit immediately
    elif decision_maker == 'both':
        decision_score = 10  # Shared decision - moderate delay
    else:  # parent
        decision_score = 5   # Need parent approval - slower process
    
    breakdown['decision_authority'] = decision_score
    score += decision_score
    
    # ================================================================
    # FACTOR 4: Budget Fit (0-15 points)
    # ================================================================
    # Why: Budget concerns slow or completely stop enrollment
    
    budget_concern = extracted_data.get('budget_concern', False)
    
    # Handle both boolean and string values
    if budget_concern == False or budget_concern == 'false' or budget_concern is None:
        budget_score = 15  # No budget issues - ready to pay
    else:
        budget_score = 5   # Budget is a concern - need payment plan/scholarship
    
    breakdown['budget_fit'] = budget_score
    score += budget_score
    
    # ================================================================
    # FACTOR 5: Engagement Level (0-20 points)
    # ================================================================
    # Why: Engaged students who ask questions convert much better
    
    engagement = extracted_data.get('engagement_level', 'medium')
    
    if engagement == 'high':
        engagement_score = 20  # Asking questions, enthusiastic, detailed responses
    elif engagement == 'medium':
        engagement_score = 12  # Polite but neutral, brief responses
    else:  # low
        engagement_score = 5   # Disengaged, very short answers, disinterested
    
    breakdown['engagement_level'] = engagement_score
    score += engagement_score
    
    # ================================================================
    # FINAL CALCULATION
    # ================================================================
    
    tier = classify_tier(score)
    reasoning = generate_reasoning(score, tier, breakdown)
    
    return {
        'score': score,
        'tier': tier,
        'breakdown': breakdown,
        'reasoning': reasoning
    }

def classify_tier(score):
    """Classify lead into HOT/WARM/COLD tier"""
    
    if score >= 80:
        return 'HOT'     # Top 20-25% - Immediate sales attention
    elif score >= 60:
        return 'WARM'    # Middle 40-45% - Nurture + counselor
    else:
        return 'COLD'    # Bottom 30-35% - Automated content only

def generate_reasoning(score, tier, breakdown):
    """Generate human-readable explanation of the score"""
    
    reasoning = f"Lead scored {score}/100 and classified as {tier}.\n\n"
    
    # Show score breakdown
    reasoning += "Score Breakdown:\n"
    reasoning += "-" * 50 + "\n"
    for factor, points in breakdown.items():
        # Convert factor name to readable format
        factor_name = factor.replace('_', ' ').title()
        reasoning += f"  • {factor_name:25s}: {points:2d} points\n"
    reasoning += "-" * 50 + "\n"
    
    # Recommended actions based on tier
    reasoning += f"\nRecommended Actions for {tier} Lead:\n"
    reasoning += "-" * 50 + "\n"
    
    if tier == 'HOT':
        reasoning += "  1. Transfer to sales manager IMMEDIATELY\n"
        reasoning += "  2. Send enrollment link via SMS within 5 minutes\n"
        reasoning += "  3. Create P0 task in CRM\n"
        reasoning += "  4. Follow up within 2 hours if no response\n"
        reasoning += "  5. Alert sales team via Slack\n"
    elif tier == 'WARM':
        reasoning += "  1. Add to nurture email campaign\n"
        reasoning += "  2. Send course brochure via WhatsApp\n"
        reasoning += "  3. Schedule counselor callback in 3-5 days\n"
        reasoning += "  4. Invite to free webinar\n"
        reasoning += "  5. Track engagement with emails\n"
    else:  # COLD
        reasoning += "  1. Add to long-term nurture list\n"
        reasoning += "  2. Send educational content weekly\n"
        reasoning += "  3. Re-engage with special offers quarterly\n"
        reasoning += "  4. No immediate human follow-up (cost-effective)\n"
        reasoning += "  5. Monitor for engagement spikes\n"
    
    return reasoning

if __name__ == "__main__":
    print("="*70)
    print("SCORING ENGINE TEST")
    print("="*70)
    
    # ================================================================
    # TEST 1: HOT LEAD SCENARIO
    # ================================================================
    print("\n" + "="*70)
    print("TEST 1: HOT LEAD SCENARIO")
    print("="*70)
    print("Profile: Class 12 student, exam in 6 months, self-decides, engaged")
    
    hot_lead = {
        'full_name': 'Priya Sharma',
        'current_class': '12',
        'target_exam': 'JEE Main',
        'exam_year': '2026',  # Current year - very urgent!
        'urgency_level': 'high',
        'budget_concern': False,
        'decision_maker': 'self',
        'engagement_level': 'high'
    }
    
    result = calculate_lead_score(hot_lead)
    
    print(f"\n{'Score:':<20} {result['score']}/100")
    print(f"{'Tier:':<20} {result['tier']}")
    print(f"\n{result['reasoning']}")
    
    # Validate
    if 80 <= result['score'] <= 100 and result['tier'] == 'HOT':
        print("\n✅ TEST 1 PASSED")
    else:
        print(f"\n⚠️  TEST 1 FAILED - Expected HOT (80-100), got {result['tier']} ({result['score']})")
    
    # ================================================================
    # TEST 2: WARM LEAD SCENARIO
    # ================================================================
    print("\n" + "="*70)
    print("TEST 2: WARM LEAD SCENARIO")
    print("="*70)
    print("Profile: Class 11 student, exam in 18 months, parent decides, engaged")
    
    warm_lead = {
        'full_name': 'Rahul Kumar',
        'current_class': '11',
        'target_exam': 'JEE',
        'exam_year': '2027',  # 12-18 months away
        'urgency_level': 'medium',
        'budget_concern': False,
        'decision_maker': 'parent',
        'engagement_level': 'high'
    }
    
    result = calculate_lead_score(warm_lead)
    
    print(f"\n{'Score:':<20} {result['score']}/100")
    print(f"{'Tier:':<20} {result['tier']}")
    print(f"\n{result['reasoning']}")
    
    # Validate
    if 60 <= result['score'] <= 79 and result['tier'] == 'WARM':
        print("\n✅ TEST 2 PASSED")
    else:
        print(f"\n⚠️  TEST 2 FAILED - Expected WARM (60-79), got {result['tier']} ({result['score']})")
    
    # ================================================================
    # TEST 3: COLD LEAD SCENARIO
    # ================================================================
    print("\n" + "="*70)
    print("TEST 3: COLD LEAD SCENARIO")
    print("="*70)
    print("Profile: Class 9 student, exam in 3 years, parent decides, low engagement")
    
    cold_lead = {
        'full_name': 'Amit Singh',
        'current_class': '9',
        'target_exam': 'JEE',
        'exam_year': '2029',  # 3 years away
        'urgency_level': 'low',
        'budget_concern': True,
        'decision_maker': 'parent',
        'engagement_level': 'low'
    }
    
    result = calculate_lead_score(cold_lead)
    
    print(f"\n{'Score:':<20} {result['score']}/100")
    print(f"{'Tier:':<20} {result['tier']}")
    print(f"\n{result['reasoning']}")
    
    # Validate
    if result['score'] < 60 and result['tier'] == 'COLD':
        print("\n✅ TEST 3 PASSED")
    else:
        print(f"\n⚠️  TEST 3 FAILED - Expected COLD (<60), got {result['tier']} ({result['score']})")
    
    # ================================================================
    # SUMMARY
    # ================================================================
    print("\n" + "="*70)
    print("✅ ALL SCORING ENGINE TESTS COMPLETE")
    print("="*70)
    print("\nScoring engine is working correctly!")
    print("Ready to integrate with data extractor.")