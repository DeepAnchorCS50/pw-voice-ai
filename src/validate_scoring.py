# validate_scoring.py
# Validates that scoring logic meets business expectations

import json
import sys
sys.path.append('C:\\Users\\kddipank\\Documents\\Documents\\Personal\\PMCurve\\PW_AI_Capstone')

from scoring_engine import calculate_lead_score

def validate_all_scenarios():
    """Test all predefined scenarios and validate results"""
    
    print("="*70)
    print("SCORING VALIDATION TEST")
    print("="*70)
    print("\nThis tests our scoring logic against expected outcomes.\n")
    
    # Load test scenarios
    try:
        with open('../data/test_scenarios.json', 'r') as f:
            test_data = json.load(f)
        scenarios = test_data['scenarios']
    except FileNotFoundError:
        print("❌ ERROR: test_scenarios.json not found in data/ folder")
        print("Please create this file first (see Step 3)")
        return
    
    results = []
    
    # Test each scenario
    for i, scenario in enumerate(scenarios, 1):
        print(f"{'='*70}")
        print(f"TEST {i}/{len(scenarios)}: {scenario['name']}")
        print(f"{'='*70}")
        print(f"Description: {scenario['description']}\n")
        
        # Run scoring
        scored = calculate_lead_score(scenario['data'])
        
        # Extract expected values
        expected_tier = scenario['expected_tier']
        expected_range = scenario['expected_score_range']
        actual_score = scored['score']
        actual_tier = scored['tier']
        
        # Validate tier
        tier_match = (expected_tier == actual_tier)
        
        # Validate score range
        score_in_range = (expected_range[0] <= actual_score <= expected_range[1])
        
        # Display results
        print(f"Expected Tier:       {expected_tier}")
        print(f"Actual Tier:         {actual_tier}")
        print(f"Tier Match:          {'✅ PASS' if tier_match else '❌ FAIL'}")
        
        print(f"\nExpected Score:      {expected_range[0]}-{expected_range[1]}")
        print(f"Actual Score:        {actual_score}")
        print(f"Score In Range:      {'✅ PASS' if score_in_range else '❌ FAIL'}")
        
        print(f"\nScore Breakdown:")
        for factor, points in scored['breakdown'].items():
            factor_name = factor.replace('_', ' ').title()
            print(f"  • {factor_name:25s}: {points:2d} points")
        
        # Record result
        test_passed = tier_match and score_in_range
        results.append({
            'scenario': scenario['name'],
            'tier_match': tier_match,
            'score_in_range': score_in_range,
            'passed': test_passed
        })
        
        print(f"\nOverall: {'✅ PASSED' if test_passed else '❌ FAILED'}")
        print()
    
    # Summary
    print(f"{'='*70}")
    print("VALIDATION SUMMARY")
    print(f"{'='*70}\n")
    
    total = len(results)
    passed = sum(1 for r in results if r['passed'])
    failed = total - passed
    
    print(f"Total Scenarios Tested:  {total}")
    print(f"Passed:                  {passed}")
    print(f"Failed:                  {failed}")
    
    if passed == total:
        print("\n" + "🎉"*20)
        print("✅ ALL VALIDATION TESTS PASSED!")
        print("🎉"*20)
        print("\nYour scoring engine is working perfectly!")
        print("Business logic is validated and ready for production!")
    else:
        print("\n⚠️  SOME VALIDATIONS FAILED")
        print("\nFailed Scenarios:")
        for r in results:
            if not r['passed']:
                print(f"  • {r['scenario']}")
                if not r['tier_match']:
                    print(f"    - Tier mismatch")
                if not r['score_in_range']:
                    print(f"    - Score out of expected range")
        
        print("\nRecommendation:")
        print("  1. Review scoring weights in scoring_engine.py")
        print("  2. Check if thresholds (80, 60) need adjustment")
        print("  3. Verify test scenario expectations are realistic")
    
    print(f"\n{'='*70}")


if __name__ == "__main__":
    validate_all_scenarios()