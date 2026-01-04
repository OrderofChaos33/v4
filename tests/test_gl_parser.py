"""Tests for GL Parser Service"""

import pytest
from src.services.gl_parser import GLParserService
from src.models.gl_entry import GLEntry


def test_parse_valid_csv():
    """Test parsing valid CSV content"""
    csv_content = b"""Account Number,Account Name,Amount,Description
5000,Product Costs,1000.00,Wholesale purchase
7000,Rent,2000.00,Monthly rent
"""
    
    entries = GLParserService.parse_csv(csv_content)
    
    assert len(entries) == 2
    assert entries[0].account_number == "5000"
    assert entries[0].account_name == "Product Costs"
    assert entries[0].amount == 1000.00
    assert entries[1].account_number == "7000"
    assert entries[1].amount == 2000.00


def test_parse_csv_with_missing_optional_fields():
    """Test parsing CSV with missing optional fields"""
    csv_content = b"""Account Number,Account Name,Amount
5000,Product Costs,1000.00
7000,Rent,2000.00
"""
    
    entries = GLParserService.parse_csv(csv_content)
    
    assert len(entries) == 2
    assert entries[0].description is None
    assert entries[0].vendor is None


def test_parse_empty_csv():
    """Test parsing empty CSV raises error"""
    csv_content = b""
    
    with pytest.raises(ValueError, match="Failed to parse CSV"):
        GLParserService.parse_csv(csv_content)


def test_parse_csv_missing_required_fields():
    """Test parsing CSV with missing required fields raises error"""
    csv_content = b"""Account Number,Description
5000,Some expense
"""
    
    with pytest.raises(ValueError, match="Missing required columns"):
        GLParserService.parse_csv(csv_content)


def test_validate_gl_data():
    """Test GL data validation"""
    entries = [
        GLEntry(account_number="5000", account_name="COGS", amount=1000.00),
        GLEntry(account_number="7000", account_name="Rent", amount=2000.00),
    ]
    
    stats = GLParserService.validate_gl_data(entries)
    
    assert stats["total_entries"] == 2
    assert stats["total_amount"] == 3000.00
    assert stats["unique_accounts"] == 2
