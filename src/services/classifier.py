"""Classification Service - 280E expense classification engine"""

from typing import List, Dict, Tuple
import re
from ..models.gl_entry import GLEntry, ClassificationType
from ..models.analysis import ExpenseClassification


class ClassificationService:
    """Service for classifying expenses per IRS 280E"""
    
    # COGS-related keywords (high confidence)
    COGS_KEYWORDS = {
        'high': [
            'product', 'inventory', 'cost of goods', 'cogs', 'wholesale',
            'raw material', 'packaging', 'labels', 'cultivation', 'grow',
            'harvest', 'trim', 'cure', 'flower', 'concentrate', 'extract',
            'purchase', 'merchandise', 'production', 'manufacturing'
        ],
        'medium': [
            'supplies', 'materials', 'freight in', 'shipping in', 
            'direct labor', 'production labor'
        ]
    }
    
    # Deductible keywords (post-rescheduling guidance allows more deductions)
    DEDUCTIBLE_KEYWORDS = {
        'high': [
            'rent', 'lease', 'utilities', 'insurance', 'depreciation',
            'professional fees', 'legal', 'accounting', 'audit',
            'bank fees', 'interest', 'repairs', 'maintenance',
            'licenses', 'permits', 'taxes', 'property tax'
        ],
        'medium': [
            'office', 'supplies', 'equipment', 'software', 'technology',
            'telecommunications', 'internet', 'phone'
        ]
    }
    
    # Non-deductible keywords (280E restrictions)
    NON_DEDUCTIBLE_KEYWORDS = {
        'high': [
            'marketing', 'advertising', 'promotion', 'branding',
            'salaries', 'wages', 'payroll', 'compensation', 'bonus',
            'benefits', 'health insurance', '401k', 'consulting',
            'travel', 'entertainment', 'meals', 'training',
            'research', 'development', 'community', 'donation'
        ],
        'medium': [
            'commission', 'sales expense', 'delivery', 'distribution',
            'vehicle', 'auto', 'fuel', 'mileage'
        ]
    }
    
    # Account number patterns (common QuickBooks/NetSuite ranges)
    ACCOUNT_RANGES = {
        'cogs': [(5000, 5999), (6000, 6999)],  # Typical COGS range
        'operating': [(7000, 7999), (8000, 8999)],  # Operating expenses
    }
    
    @staticmethod
    def _check_keywords(text: str, keyword_dict: Dict[str, List[str]]) -> Tuple[bool, str, float]:
        """
        Check if text contains keywords and return match level
        
        Returns:
            (matched, confidence_level, base_confidence)
        """
        if not text:
            return False, 'none', 0.0
        
        text_lower = text.lower()
        
        # Check high confidence keywords first
        for keyword in keyword_dict.get('high', []):
            if keyword in text_lower:
                return True, 'high', 90.0
        
        # Check medium confidence keywords
        for keyword in keyword_dict.get('medium', []):
            if keyword in text_lower:
                return True, 'medium', 70.0
        
        return False, 'none', 0.0
    
    @staticmethod
    def _check_account_range(account_number: str, range_type: str) -> bool:
        """Check if account number falls in typical range"""
        try:
            acct_num = int(re.sub(r'[^0-9]', '', account_number))
            ranges = ClassificationService.ACCOUNT_RANGES.get(range_type, [])
            return any(start <= acct_num <= end for start, end in ranges)
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def _mock_llm_classification(entry: GLEntry) -> Tuple[ClassificationType, float, str]:
        """
        Mock LLM classification for ambiguous cases
        In production, this would call a real LLM API
        
        Returns:
            (classification, confidence, reasoning)
        """
        # For now, use conservative default
        return (
            ClassificationType.NON_DEDUCTIBLE,
            50.0,
            "Ambiguous classification - flagged for CPA review (mock LLM)"
        )
    
    @staticmethod
    def classify_entry(entry: GLEntry) -> ExpenseClassification:
        """
        Classify a single GL entry per 280E rules
        
        Args:
            entry: GLEntry to classify
            
        Returns:
            ExpenseClassification with confidence score and rationale
        """
        # Combine text fields for analysis
        combined_text = f"{entry.account_name} {entry.description or ''}"
        
        # Track best match
        best_classification = None
        best_confidence = 0.0
        best_rationale = ""
        
        # Check COGS keywords
        cogs_match, cogs_level, cogs_conf = ClassificationService._check_keywords(
            combined_text, ClassificationService.COGS_KEYWORDS
        )
        
        if cogs_match:
            # Check account range for additional confidence
            if ClassificationService._check_account_range(entry.account_number, 'cogs'):
                cogs_conf += 5.0
            
            if cogs_conf > best_confidence:
                best_classification = ClassificationType.COGS
                best_confidence = min(cogs_conf, 95.0)
                best_rationale = (
                    f"Direct product cost - qualifies as COGS under 280E. "
                    f"Keyword match ({cogs_level} confidence). "
                    "COGS are deductible for cannabis businesses."
                )
        
        # Check deductible keywords
        deduct_match, deduct_level, deduct_conf = ClassificationService._check_keywords(
            combined_text, ClassificationService.DEDUCTIBLE_KEYWORDS
        )
        
        if deduct_match and deduct_conf > best_confidence:
            best_classification = ClassificationType.DEDUCTIBLE
            best_confidence = min(deduct_conf, 85.0)
            best_rationale = (
                f"Ordinary and necessary business expense ({deduct_level} confidence). "
                "May be deductible post-rescheduling or as indirect COGS allocation. "
                "Consult CPA for final determination."
            )
        
        # Check non-deductible keywords
        non_deduct_match, non_deduct_level, non_deduct_conf = ClassificationService._check_keywords(
            combined_text, ClassificationService.NON_DEDUCTIBLE_KEYWORDS
        )
        
        if non_deduct_match and non_deduct_conf > best_confidence:
            best_classification = ClassificationType.NON_DEDUCTIBLE
            best_confidence = min(non_deduct_conf, 85.0)
            best_rationale = (
                f"Operating expense subject to 280E restrictions ({non_deduct_level} confidence). "
                "Not deductible for cannabis businesses under current 280E interpretation."
            )
        
        # If no clear match, use mock LLM for ambiguous cases
        if best_classification is None or best_confidence < 60.0:
            llm_class, llm_conf, llm_reason = ClassificationService._mock_llm_classification(entry)
            
            # Be conservative - default to non-deductible with low confidence
            if best_classification is None:
                best_classification = ClassificationType.NON_DEDUCTIBLE
                best_confidence = 40.0
                best_rationale = (
                    "No clear classification match. Conservative default: non-deductible. "
                    "Requires CPA review for proper classification."
                )
        
        # Flag for review if confidence is low
        needs_review = best_confidence < 70.0
        
        return ExpenseClassification(
            account_number=entry.account_number,
            account_name=entry.account_name,
            description=entry.description,
            amount=entry.amount,
            classification=best_classification,
            confidence_score=round(best_confidence, 1),
            rationale=best_rationale,
            needs_review=needs_review
        )
    
    @staticmethod
    def classify_entries(entries: List[GLEntry]) -> List[ExpenseClassification]:
        """
        Classify multiple GL entries
        
        Args:
            entries: List of GLEntry objects
            
        Returns:
            List of ExpenseClassification objects
        """
        return [ClassificationService.classify_entry(entry) for entry in entries]
    
    @staticmethod
    def calculate_summary(classifications: List[ExpenseClassification]) -> dict:
        """
        Calculate summary statistics for classified expenses
        
        Args:
            classifications: List of ExpenseClassification objects
            
        Returns:
            Dictionary with summary statistics
        """
        if not classifications:
            return {
                "total_expenses": 0.0,
                "cogs": 0.0,
                "deductible": 0.0,
                "non_deductible": 0.0,
                "avg_confidence": 0.0,
                "items_needing_review": 0,
                "tax_impact_estimate": 0.0
            }
        
        cogs_total = sum(
            c.amount for c in classifications 
            if c.classification == ClassificationType.COGS
        )
        deductible_total = sum(
            c.amount for c in classifications 
            if c.classification == ClassificationType.DEDUCTIBLE
        )
        non_deductible_total = sum(
            c.amount for c in classifications 
            if c.classification == ClassificationType.NON_DEDUCTIBLE
        )
        
        total_expenses = sum(c.amount for c in classifications)
        avg_confidence = sum(c.confidence_score for c in classifications) / len(classifications)
        items_needing_review = sum(1 for c in classifications if c.needs_review)
        
        # Estimate tax impact (assuming 21% federal corporate rate)
        # Non-deductible expenses increase taxable income
        tax_impact = non_deductible_total * 0.21
        
        return {
            "total_expenses": round(total_expenses, 2),
            "cogs": round(cogs_total, 2),
            "deductible": round(deductible_total, 2),
            "non_deductible": round(non_deductible_total, 2),
            "cogs_percentage": round((cogs_total / total_expenses * 100) if total_expenses > 0 else 0, 1),
            "deductible_percentage": round((deductible_total / total_expenses * 100) if total_expenses > 0 else 0, 1),
            "non_deductible_percentage": round((non_deductible_total / total_expenses * 100) if total_expenses > 0 else 0, 1),
            "avg_confidence": round(avg_confidence, 1),
            "items_needing_review": items_needing_review,
            "review_percentage": round((items_needing_review / len(classifications) * 100), 1),
            "tax_impact_estimate": round(tax_impact, 2),
            "potential_savings": round((cogs_total + deductible_total) * 0.21, 2)
        }
