"""Classification result data model."""
from typing import List, Dict
from pydantic import BaseModel, Field
from .gl_entry import GLEntry


class ClassificationResult(BaseModel):
    """Results of GL classification process."""
    entries: List[GLEntry] = Field(default_factory=list)
    summary: Dict[str, float] = Field(default_factory=dict)
    total_amount: float = 0.0
    cogs_total: float = 0.0
    deductible_total: float = 0.0
    non_deductible_total: float = 0.0
    needs_review_count: int = 0
    estimated_tax_impact: float = 0.0
    
    def calculate_summary(self, tax_rate: float = 0.21):
        """Calculate summary statistics."""
        self.total_amount = sum(entry.amount for entry in self.entries)
        self.cogs_total = sum(
            entry.amount for entry in self.entries
            if (entry.override_classification or entry.classification) == "COGS"
        )
        self.deductible_total = sum(
            entry.amount for entry in self.entries
            if (entry.override_classification or entry.classification) == "Deductible"
        )
        self.non_deductible_total = sum(
            entry.amount for entry in self.entries
            if (entry.override_classification or entry.classification) == "Non-Deductible"
        )
        self.needs_review_count = sum(
            1 for entry in self.entries if entry.needs_review
        )
        
        # Tax impact: tax saved on deductible amounts
        deductible_total = self.cogs_total + self.deductible_total
        self.estimated_tax_impact = deductible_total * tax_rate
        
        self.summary = {
            "total_expenses": self.total_amount,
            "cogs": self.cogs_total,
            "deductible_operating": self.deductible_total,
            "non_deductible": self.non_deductible_total,
            "total_deductible": deductible_total,
            "estimated_tax_savings": self.estimated_tax_impact,
            "needs_review": self.needs_review_count
        }
