"""280E classification engine with rule-based logic and mock LLM."""
from typing import List, Tuple
import re
from ..models import GLEntry, ClassificationType


class Classification280E:
    """
    Classify expenses according to IRS 280E rules.
    
    280E disallows deductions for businesses trafficking Schedule I/II controlled substances,
    but allows deduction of COGS. Post-rescheduling (if cannabis moves to Schedule III),
    ordinary business deductions would be allowed.
    """
    
    # COGS-related keywords (directly attributable to production/purchase of inventory)
    COGS_KEYWORDS = [
        'inventory', 'plants', 'seeds', 'clones', 'cultivation', 'grow', 'growing',
        'harvest', 'trim', 'trimming', 'curing', 'packaging material', 'labels',
        'nutrients', 'soil', 'medium', 'propagation', 'direct labor', 'production labor',
        'cost of goods', 'cogs', 'product cost', 'purchase of goods', 'wholesale purchase'
    ]
    
    # Deductible operating expenses (if post-rescheduling, or if not cannabis-related)
    DEDUCTIBLE_KEYWORDS = [
        'rent', 'utilities', 'insurance', 'professional fees', 'legal fees',
        'accounting', 'office supplies', 'software', 'technology', 'telecommunications',
        'marketing', 'advertising', 'consulting', 'bank fees', 'depreciation',
        'repairs and maintenance', 'vehicle', 'travel', 'meals', 'entertainment',
        'training', 'education', 'licenses', 'permits', 'regulatory compliance'
    ]
    
    # Non-deductible under 280E (general business expenses for Schedule I/II businesses)
    NON_DEDUCTIBLE_KEYWORDS = [
        'salaries', 'wages', 'payroll', 'employee benefits', 'health insurance',
        'administrative', 'general operations', 'office rent', 'facility maintenance'
    ]
    
    # Account codes that typically indicate COGS
    COGS_ACCOUNT_PATTERNS = [
        r'^50\d{2}',  # 5000-5099 series
        r'^[Cc][Oo][Gg][Ss]',  # COGS prefix
        r'^[Ii]nv',  # Inventory prefix
    ]
    
    def __init__(self, schedule_status: str = "Schedule I"):
        """
        Initialize classifier.
        
        Args:
            schedule_status: Current schedule status ("Schedule I", "Schedule III", etc.)
        """
        self.schedule_status = schedule_status
        self.is_post_rescheduling = "III" in schedule_status or "3" in schedule_status
    
    def classify_entries(self, entries: List[GLEntry]) -> List[GLEntry]:
        """
        Classify all GL entries.
        
        Args:
            entries: List of GLEntry objects to classify
            
        Returns:
            List of GLEntry objects with classifications
        """
        for entry in entries:
            classification, confidence, rationale = self._classify_entry(entry)
            entry.classification = classification
            entry.confidence_score = confidence
            entry.rationale = rationale
            entry.needs_review = confidence < 80.0
        
        return entries
    
    def _classify_entry(self, entry: GLEntry) -> Tuple[ClassificationType, float, str]:
        """
        Classify a single GL entry.
        
        Returns:
            Tuple of (classification, confidence_score, rationale)
        """
        # Combine text fields for analysis
        text = f"{entry.account_name} {entry.description}".lower()
        account_code = entry.account_code
        
        # Check account code patterns first (high confidence)
        if self._matches_account_pattern(account_code, self.COGS_ACCOUNT_PATTERNS):
            return (
                ClassificationType.COGS,
                95.0,
                "Account code pattern indicates COGS (directly attributable to inventory production)"
            )
        
        # Keyword-based classification
        cogs_score = self._calculate_keyword_score(text, self.COGS_KEYWORDS)
        deductible_score = self._calculate_keyword_score(text, self.DEDUCTIBLE_KEYWORDS)
        non_deductible_score = self._calculate_keyword_score(text, self.NON_DEDUCTIBLE_KEYWORDS)
        
        # If post-rescheduling (Schedule III), most expenses are deductible
        if self.is_post_rescheduling:
            if cogs_score > 0.3:
                return (
                    ClassificationType.COGS,
                    85.0 + (cogs_score * 10),
                    "Direct cost of goods sold (inventory production costs)"
                )
            else:
                return (
                    ClassificationType.DEDUCTIBLE,
                    85.0,
                    "Post-rescheduling: Operating expenses are generally deductible"
                )
        
        # Pre-rescheduling (Schedule I/II) - 280E applies
        if cogs_score > 0.4:
            confidence = 80.0 + (cogs_score * 15)
            return (
                ClassificationType.COGS,
                min(confidence, 95.0),
                "Direct COGS: Deductible under 280E as cost directly attributable to inventory"
            )
        
        if cogs_score > 0.2:
            # Ambiguous - might be COGS
            confidence = 60.0 + (cogs_score * 20)
            return (
                ClassificationType.COGS,
                confidence,
                "Possibly COGS - May need CPA review to determine if directly attributable to inventory"
            )
        
        # Check if clearly deductible (e.g., minimal cannabis business connection)
        if deductible_score > 0.5 and non_deductible_score < 0.2:
            return (
                ClassificationType.DEDUCTIBLE,
                70.0,
                "May be deductible if not directly related to cannabis operations (needs verification)"
            )
        
        # Default to non-deductible under 280E
        if non_deductible_score > 0.3 or deductible_score > 0.2:
            confidence = 75.0 + (non_deductible_score * 15)
            return (
                ClassificationType.NON_DEDUCTIBLE,
                min(confidence, 90.0),
                "General business expense: Non-deductible under 280E for Schedule I/II controlled substance business"
            )
        
        # Ambiguous - use mock LLM
        return self._mock_llm_classify(entry)
    
    def _matches_account_pattern(self, account_code: str, patterns: List[str]) -> bool:
        """Check if account code matches any pattern."""
        for pattern in patterns:
            if re.match(pattern, account_code):
                return True
        return False
    
    def _calculate_keyword_score(self, text: str, keywords: List[str]) -> float:
        """Calculate relevance score based on keyword matches."""
        matches = sum(1 for keyword in keywords if keyword in text)
        return min(matches / 3.0, 1.0)  # Normalize to 0-1 range
    
    def _mock_llm_classify(self, entry: GLEntry) -> Tuple[ClassificationType, float, str]:
        """
        Mock LLM classification for ambiguous entries.
        In production, this would call an actual LLM API.
        """
        # Simple heuristic: look at amount and description length
        if entry.amount > 10000:
            return (
                ClassificationType.COGS,
                55.0,
                "Mock LLM: Large amount may indicate inventory purchase - requires manual review"
            )
        else:
            return (
                ClassificationType.NON_DEDUCTIBLE,
                55.0,
                "Mock LLM: Ambiguous classification - CPA review recommended"
            )
