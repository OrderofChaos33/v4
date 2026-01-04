"""Tests for Classification Service"""

import pytest
from src.services.classifier import ClassificationService
from src.models.gl_entry import GLEntry, ClassificationType


def test_classify_cogs_entry():
    """Test classification of COGS entry"""
    entry = GLEntry(
        account_number="5000",
        account_name="Product Costs",
        description="Wholesale flower purchase",
        amount=5000.00
    )
    
    classification = ClassificationService.classify_entry(entry)
    
    assert classification.classification == ClassificationType.COGS
    assert classification.confidence_score >= 70
    assert "COGS" in classification.rationale


def test_classify_deductible_entry():
    """Test classification of deductible entry"""
    entry = GLEntry(
        account_number="7000",
        account_name="Rent Expense",
        description="Monthly rent payment",
        amount=3000.00
    )
    
    classification = ClassificationService.classify_entry(entry)
    
    assert classification.classification == ClassificationType.DEDUCTIBLE
    assert classification.confidence_score >= 60


def test_classify_non_deductible_entry():
    """Test classification of non-deductible entry"""
    entry = GLEntry(
        account_number="8000",
        account_name="Marketing",
        description="Social media advertising",
        amount=2000.00
    )
    
    classification = ClassificationService.classify_entry(entry)
    
    assert classification.classification == ClassificationType.NON_DEDUCTIBLE
    assert classification.confidence_score >= 60


def test_classify_ambiguous_entry():
    """Test classification of ambiguous entry"""
    entry = GLEntry(
        account_number="9999",
        account_name="Miscellaneous",
        description="Various expenses",
        amount=500.00
    )
    
    classification = ClassificationService.classify_entry(entry)
    
    # Should default to non-deductible with low confidence
    assert classification.classification == ClassificationType.NON_DEDUCTIBLE
    assert classification.confidence_score < 70
    assert classification.needs_review is True


def test_calculate_summary():
    """Test summary calculation"""
    from src.models.analysis import ExpenseClassification
    
    classifications = [
        ExpenseClassification(
            account_number="5000",
            account_name="COGS",
            amount=10000.00,
            classification=ClassificationType.COGS,
            confidence_score=90.0,
            rationale="Test",
            needs_review=False
        ),
        ExpenseClassification(
            account_number="7000",
            account_name="Rent",
            amount=5000.00,
            classification=ClassificationType.DEDUCTIBLE,
            confidence_score=85.0,
            rationale="Test",
            needs_review=False
        ),
        ExpenseClassification(
            account_number="8000",
            account_name="Marketing",
            amount=3000.00,
            classification=ClassificationType.NON_DEDUCTIBLE,
            confidence_score=80.0,
            rationale="Test",
            needs_review=False
        ),
    ]
    
    summary = ClassificationService.calculate_summary(classifications)
    
    assert summary["total_expenses"] == 18000.00
    assert summary["cogs"] == 10000.00
    assert summary["deductible"] == 5000.00
    assert summary["non_deductible"] == 3000.00
    assert summary["avg_confidence"] == 85.0
    assert summary["items_needing_review"] == 0
