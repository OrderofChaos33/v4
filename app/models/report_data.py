"""Report data model."""
from typing import Optional
from pydantic import BaseModel, Field


class ReportData(BaseModel):
    """Input data for report generation."""
    state: str = Field(..., description="State of operation")
    entity_structure: str = Field(..., description="Entity structure")
    tax_year: str = Field(..., description="Tax year/period")
    company_name: Optional[str] = Field("Cannabis Operator", description="Company name")
    federal_tax_rate: float = Field(0.21, ge=0, le=1, description="Federal tax rate")
