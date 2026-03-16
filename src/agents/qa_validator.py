# src/agents/qa_validator.py  
# Agent 4: QA Validator
# Job: Check each extracted lead for consistency and quality
# Why: Bad data + ML = confidently wrong predictions. Validate before it enters the dataset.
# This agent uses RULES (not Claude API) — fast, free, deterministic.

class QAValidator:
    """
    Validates extracted lead data for consistency.
    
    Design decision: This agent uses rule-based logic, NOT an LLM.
    Why? Validation rules are deterministic — we know exactly what "valid" means.
    Using an LLM for this would be slower, more expensive, and less reliable.
    Always use the simplest tool that solves the problem.
    """
    
    def validate(self, extracted_lead):
        """
        Run all quality checks on an extracted lead.
        
        Returns: dict with is_valid, quality_score, issues list
        """
        issues = []
        quality_score = 100  # Start at 100, deduct for each issue
        
        # Check 1: Required fields present
        required_fields = ['full_name', 'current_class', 'target_exam', 'months_to_exam']
        for field in required_fields:
            value = extracted_lead.get(field, 'unknown')
            if value == 'unknown' or value == '' or value is None:
                issues.append(f"Missing required field: {field}")
                quality_score -= 10
        
        # Check 2: Class is valid
        valid_classes = ['10', '11', '12', 'dropper', 'unknown']
        if extracted_lead.get('current_class') not in valid_classes:
            issues.append(f"Invalid class: {extracted_lead.get('current_class')}")
            quality_score -= 5
        
        # Check 3: Urgency vs months_to_exam consistency
        # HIGH urgency should NOT have 20+ months to exam
        urgency = extracted_lead.get('urgency_level', 'unknown')
        months = extracted_lead.get('months_to_exam', 0)
        
        if urgency == 'high' and months > 15:
            issues.append(f"Inconsistency: urgency=high but months_to_exam={months}")
            quality_score -= 15
        
        if urgency == 'low' and months < 5:
            issues.append(f"Inconsistency: urgency=low but months_to_exam={months} (very urgent)")
            quality_score -= 10
        
        # Check 4: Tier label vs engagement consistency
        tier = extracted_lead.get('tier_label', 'unknown')
        engagement = extracted_lead.get('engagement_level', 'unknown')
        
        if tier == 'HOT' and engagement == 'low':
            issues.append(f"Inconsistency: HOT lead with low engagement")
            quality_score -= 20
        
        if tier == 'COLD' and engagement == 'high':
            issues.append(f"Inconsistency: COLD lead with high engagement")
            quality_score -= 15
        
        # Check 5: Extraction confidence
        if extracted_lead.get('extraction_confidence') == 'low':
            issues.append("Low extraction confidence — data may be unreliable")
            quality_score -= 10
        
        # Check 6: Extraction success
        if not extracted_lead.get('extraction_success', True):
            issues.append(f"Extraction failed: {extracted_lead.get('extraction_error', 'unknown')}")
            quality_score -= 30
        
        # Final verdict
        quality_score = max(0, quality_score)  # Floor at 0
        is_valid = quality_score >= 60  # Leads below 60 are dropped from dataset
        
        return {
            "conversation_id": extracted_lead.get("conversation_id"),
            "is_valid": is_valid,
            "quality_score": quality_score,
            "issues": issues,
            "issue_count": len(issues)
        }
    
    def validate_batch(self, extracted_leads):
        """Validate a list of leads. Returns list of validation results."""
        results = []
        valid_count = 0
        invalid_count = 0
        
        for lead in extracted_leads:
            result = self.validate(lead)
            results.append(result)
            if result['is_valid']:
                valid_count += 1
            else:
                invalid_count += 1
        
        print(f"\n[Agent 4] QA Validator results:")
        print(f"   ✅ Valid: {valid_count}")
        print(f"   ❌ Invalid: {invalid_count}")
        print(f"   📊 Pass rate: {valid_count/len(extracted_leads)*100:.1f}%")
        
        return results