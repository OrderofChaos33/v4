"""General Ledger entry data model."""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ClassificationType(str, Enum):
    """Expense classification types per 280E."""
    COGS = "COGS"  # Cost of Goods Sold - Deductible
    DEDUCTIBLE = "Deductible"  # Deductible operating expense
    NON_DEDUCTIBLE = "Non-Deductible"  # Non-deductible per 280E


class GLEntry(BaseModel):
    """Represents a single general ledger entry."""
    date: str = Field(..., description="Transaction date")
    account_code: str = Field(..., description="GL account code")
    account_name: str = Field(..., description="GL account name")
    description: str = Field(..., description="Transaction description")
    amount: float = Field(..., description="Transaction amount")
    category: Optional[str] = Field(None, description="Original GL category")
    
    # Classification fields (populated during processing)
    classification: Optional[ClassificationType] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=100)
    rationale: Optional[str] = None
    needs_review: bool = False
    override_classification: Optional[ClassificationType] = None
    
    class Config:
        use_enum_values = True
