"""
Simple test script to verify 280E classification functionality
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models import GLEntry, ClassificationResult, ReportData, ClassificationType
from app.services import GLParser, Classification280E, ReportGenerator, ExportService


def test_gl_parser():
    """Test CSV parsing"""
    print("Testing GL Parser...")
    
    parser = GLParser()
    sample_csv = Path(__file__).parent / "sample_gl.csv"
    
    with open(sample_csv, 'rb') as f:
        content = f.read()
    
    entries = parser.parse_csv(content)
    print(f"✓ Parsed {len(entries)} entries from sample CSV")
    
    # Verify first entry
    assert entries[0].account_code == "5010"
    assert "Cannabis" in entries[0].description
    print(f"✓ First entry: {entries[0].account_name} - ${entries[0].amount}")
    
    return entries


def test_classification(entries):
    """Test 280E classification engine"""
    print("\nTesting Classification Engine...")
    
    classifier = Classification280E(schedule_status="Schedule I")
    classified_entries = classifier.classify_entries(entries)
    
    print(f"✓ Classified {len(classified_entries)} entries")
    
    # Check classifications
    cogs_count = sum(1 for e in classified_entries if e.classification == ClassificationType.COGS)
    deductible_count = sum(1 for e in classified_entries if e.classification == ClassificationType.DEDUCTIBLE)
    non_deductible_count = sum(1 for e in classified_entries if e.classification == ClassificationType.NON_DEDUCTIBLE)
    
    print(f"  - COGS: {cogs_count} entries")
    print(f"  - Deductible: {deductible_count} entries")
    print(f"  - Non-Deductible: {non_deductible_count} entries")
    
    # Check confidence scores
    high_conf = sum(1 for e in classified_entries if e.confidence_score >= 80)
    print(f"  - High confidence (≥80%): {high_conf} entries")
    
    # Show a few examples
    print("\nSample Classifications:")
    for entry in classified_entries[:3]:
        print(f"  • {entry.account_name}: {entry.classification.value} ({entry.confidence_score:.0f}%)")
        print(f"    Rationale: {entry.rationale[:80]}...")
    
    return classified_entries


def test_classification_result(entries):
    """Test classification result calculations"""
    print("\nTesting Classification Result...")
    
    result = ClassificationResult(entries=entries)
    result.calculate_summary()
    
    print(f"✓ Total expenses: ${result.total_amount:,.2f}")
    print(f"  - COGS: ${result.cogs_total:,.2f}")
    print(f"  - Deductible: ${result.deductible_total:,.2f}")
    print(f"  - Non-Deductible: ${result.non_deductible_total:,.2f}")
    print(f"  - Estimated tax impact: ${result.estimated_tax_impact:,.2f}")
    print(f"  - Items needing review: {result.needs_review_count}")
    
    return result


def test_pdf_generation(result):
    """Test PDF report generation"""
    print("\nTesting PDF Report Generation...")
    
    report_data = ReportData(
        state="California",
        entity_structure="Single Entity",
        tax_year="2024",
        company_name="Test Cannabis Company"
    )
    
    generator = ReportGenerator()
    pdf_bytes = generator.generate_pdf(result, report_data)
    
    print(f"✓ Generated PDF report: {len(pdf_bytes):,} bytes")
    
    # Save to file
    output_path = Path(__file__).parent / "test_report.pdf"
    with open(output_path, 'wb') as f:
        f.write(pdf_bytes)
    print(f"✓ Saved to {output_path}")
    
    return pdf_bytes


def test_csv_export(result):
    """Test CSV export"""
    print("\nTesting CSV Export...")
    
    exporter = ExportService()
    csv_bytes = exporter.export_to_csv(result)
    
    print(f"✓ Generated CSV export: {len(csv_bytes):,} bytes")
    
    # Save to file
    output_path = Path(__file__).parent / "test_export.csv"
    with open(output_path, 'wb') as f:
        f.write(csv_bytes)
    print(f"✓ Saved to {output_path}")
    
    return csv_bytes


def test_json_export(result):
    """Test JSON export"""
    print("\nTesting JSON Export...")
    
    exporter = ExportService()
    json_bytes = exporter.export_to_json(result)
    
    print(f"✓ Generated JSON export: {len(json_bytes):,} bytes")
    
    # Save to file
    output_path = Path(__file__).parent / "test_export.json"
    with open(output_path, 'wb') as f:
        f.write(json_bytes)
    print(f"✓ Saved to {output_path}")
    
    return json_bytes


def main():
    """Run all tests"""
    print("=" * 70)
    print("280E CLASSIFICATION SYSTEM - FUNCTIONALITY TEST")
    print("=" * 70)
    
    try:
        # Test each component
        entries = test_gl_parser()
        classified_entries = test_classification(entries)
        result = test_classification_result(classified_entries)
        test_pdf_generation(result)
        test_csv_export(result)
        test_json_export(result)
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print("\nGenerated test files:")
        print("  - test_report.pdf")
        print("  - test_export.csv")
        print("  - test_export.json")
        print("\nYou can now start the server with:")
        print("  uvicorn app.main:app --reload")
        print("\nOr use the startup script:")
        print("  ./run.sh")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
