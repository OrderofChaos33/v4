"""GL Entry and Classification Type Models"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ClassificationType(str, Enum):
    """Expense classification types per IRS 280E"""
    COGS = "Cost of Goods Sold"
    DEDUCTIBLE = "Deductible Operating Expense"
    NON_DEDUCTIBLE = "Non-Deductible (280E)"


class GLEntry(BaseModel):
    """General Ledger Entry"""
    account_number: str = Field(..., description="GL account number")
    account_name: str = Field(..., description="GL account name")
    description: Optional[str] = Field(None, description="Transaction description")
    amount: float = Field(..., description="Transaction amount")
    date: Optional[str] = Field(None, description="Transaction date")
    vendor: Optional[str] = Field(None, description="Vendor/payee name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "account_number": "5000",
                "account_name": "Product Costs",
                "description": "Wholesale flower purchase",
                "amount": 5000.00,
                "date": "2024-01-15",
                "vendor": "Grower Co"
            }
        }
