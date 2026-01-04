"""Analysis request and result models"""

from typing import List, Optional
from pydantic import BaseModel, Field
from .gl_entry import ClassificationType


class AnalysisRequest(BaseModel):
    """Request for expense analysis"""
    state: str = Field(..., description="State(s) of operation", examples=["CA"])
    entity_structure: str = Field(
        default="single-entity",
        description="Entity structure type",
        examples=["single-entity", "multi-entity"]
    )
    tax_year: str = Field(..., description="Tax year/period", examples=["2024"])
    
    class Config:
        json_schema_extra = {
            "example": {
                "state": "CA",
                "entity_structure": "single-entity",
                "tax_year": "2024"
            }
        }


class ExpenseClassification(BaseModel):
    """Classification result for a single expense"""
    account_number: str
    account_name: str
    description: Optional[str] = None
    amount: float
    classification: ClassificationType
    confidence_score: float = Field(..., ge=0.0, le=100.0, description="Confidence 0-100%")
    rationale: str = Field(..., description="Explanation for classification")
    needs_review: bool = Field(default=False, description="Flagged for CPA review")
    
    class Config:
        json_schema_extra = {
            "example": {
                "account_number": "5000",
                "account_name": "Product Costs",
                "description": "Wholesale flower purchase",
                "amount": 5000.00,
                "classification": "Cost of Goods Sold",
                "confidence_score": 95.0,
                "rationale": "Direct product cost - qualifies as COGS under 280E",
                "needs_review": False
            }
        }


class AnalysisResult(BaseModel):
    """Complete analysis result"""
    analysis_id: str
    request: AnalysisRequest
    classifications: List[ExpenseClassification]
    summary: dict = Field(..., description="Summary statistics")
    
    class Config:
        json_schema_extra = {
            "example": {
                "analysis_id": "abc123",
                "request": {
                    "state": "CA",
                    "entity_structure": "single-entity",
                    "tax_year": "2024"
                },
                "classifications": [],
                "summary": {
                    "total_expenses": 100000.00,
                    "cogs": 50000.00,
                    "deductible": 20000.00,
                    "non_deductible": 30000.00,
                    "avg_confidence": 85.0,
                    "items_needing_review": 5
                }
            }
        }
