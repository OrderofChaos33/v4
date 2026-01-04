# Example Usage Guide

This guide demonstrates common use cases for the 280E Expense Reclassification API.

## Prerequisites

Ensure the server is running:
```bash
./start.sh
# OR
python -m uvicorn src.api.main:app --reload
```

## Example 1: Basic Analysis

Analyze your GL data:

```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -F "file=@examples/sample_gl.csv" \
  -F "state=CA" \
  -F "entity_structure=single-entity" \
  -F "tax_year=2024"
```

**Response:**
```json
{
  "analysis_id": "abc-123-def-456",
  "summary": {
    "total_expenses": 84950.00,
    "cogs": 40200.00,
    "deductible": 16450.00,
    "non_deductible": 28300.00,
    "avg_confidence": 86.0,
    "items_needing_review": 0
  },
  "total_items": 20,
  "message": "Analysis complete. Use analysis_id to retrieve reports."
}
```

Save the `analysis_id` for retrieving reports.

## Example 2: Download Reports

### PDF Report (for CPA)

```bash
curl "http://localhost:8000/api/report/abc-123-def-456/pdf" \
  --output report.pdf
```

### CSV Export (detailed data)

```bash
curl "http://localhost:8000/api/report/abc-123-def-456/csv" \
  --output report.csv
```

### JSON Export (machine-readable)

```bash
curl "http://localhost:8000/api/report/abc-123-def-456/json" \
  --output report.json
```

## Example 3: Python Script

```python
import requests
import json

# 1. Upload and analyze
files = {'file': open('examples/sample_gl.csv', 'rb')}
data = {
    'state': 'CA',
    'entity_structure': 'single-entity',
    'tax_year': '2024'
}

response = requests.post(
    'http://localhost:8000/api/analyze',
    files=files,
    data=data
)

result = response.json()
analysis_id = result['analysis_id']
print(f"Analysis ID: {analysis_id}")
print(f"Total Expenses: ${result['summary']['total_expenses']:,.2f}")
print(f"COGS: ${result['summary']['cogs']:,.2f}")
print(f"Deductible: ${result['summary']['deductible']:,.2f}")
print(f"Non-Deductible: ${result['summary']['non_deductible']:,.2f}")
print(f"Tax Impact: ${result['summary']['tax_impact_estimate']:,.2f}")

# 2. Download PDF
pdf_response = requests.get(
    f'http://localhost:8000/api/report/{analysis_id}/pdf'
)
with open('report.pdf', 'wb') as f:
    f.write(pdf_response.content)
print("PDF saved to report.pdf")

# 3. Get full analysis
analysis = requests.get(
    f'http://localhost:8000/api/report/{analysis_id}'
).json()

# Show items needing review
review_items = [
    c for c in analysis['classifications'] 
    if c['needs_review']
]
if review_items:
    print(f"\n{len(review_items)} items need CPA review:")
    for item in review_items:
        print(f"  - {item['account_name']}: ${item['amount']:,.2f}")
        print(f"    Confidence: {item['confidence_score']}%")
else:
    print("\nNo items flagged for review")
```

## Example 4: Understanding Classifications

The API classifies expenses into three categories:

### Cost of Goods Sold (COGS) - Deductible ✅

```csv
Account Number,Account Name,Description,Amount
5000,Product Purchase,Wholesale flower,10000.00
5010,Packaging,Product containers,2000.00
5020,Labels,Compliance labels,500.00
```

### Deductible Operating Expenses ⚠️

```csv
Account Number,Account Name,Description,Amount
7000,Rent,Facility rent,5000.00
7100,Utilities,Electric and water,1500.00
7200,Insurance,Business insurance,2500.00
7300,Professional Fees,CPA services,3000.00
```

### Non-Deductible (280E) ❌

```csv
Account Number,Account Name,Description,Amount
8000,Marketing,Social media ads,4000.00
8100,Salaries,Retail staff,12000.00
8200,Benefits,Health insurance,3500.00
8300,Travel,Conference,2000.00
```

## Example 5: Multi-State Operation

For multi-state operations, analyze each state separately:

```bash
# California operation
curl -X POST "http://localhost:8000/api/analyze" \
  -F "file=@gl_ca.csv" \
  -F "state=CA" \
  -F "tax_year=2024"

# Colorado operation
curl -X POST "http://localhost:8000/api/analyze" \
  -F "file=@gl_co.csv" \
  -F "state=CO" \
  -F "tax_year=2024"
```

## Example 6: Review Items with Low Confidence

```python
# Get analysis
analysis = requests.get(
    f'http://localhost:8000/api/report/{analysis_id}'
).json()

# Filter by confidence threshold
low_confidence = [
    c for c in analysis['classifications']
    if c['confidence_score'] < 75
]

# Export for CPA review
import csv
with open('review_items.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'account_number', 'account_name', 'amount', 
        'classification', 'confidence_score', 'rationale'
    ])
    writer.writeheader()
    writer.writerows(low_confidence)

print(f"Exported {len(low_confidence)} items for CPA review")
```

## Example 7: Interpreting Tax Impact

```python
summary = result['summary']

print("\n280E Tax Impact Analysis:")
print("=" * 50)
print(f"Total Expenses: ${summary['total_expenses']:,.2f}")
print(f"\nBreakdown:")
print(f"  COGS (Deductible):        ${summary['cogs']:,.2f} ({summary['cogs_percentage']:.1f}%)")
print(f"  Operating (Deductible):   ${summary['deductible']:,.2f} ({summary['deductible_percentage']:.1f}%)")
print(f"  280E Non-Deductible:      ${summary['non_deductible']:,.2f} ({summary['non_deductible_percentage']:.1f}%)")
print(f"\nEstimated Tax Impact:")
print(f"  Additional Tax (21%):     ${summary['tax_impact_estimate']:,.2f}")
print(f"  Potential Savings:        ${summary['potential_savings']:,.2f}")
print(f"\nConfidence Metrics:")
print(f"  Average Confidence:       {summary['avg_confidence']:.1f}%")
print(f"  Items Needing Review:     {summary['items_needing_review']} ({summary['review_percentage']:.1f}%)")
```

## Example 8: Cleanup

Delete analysis after downloading reports:

```bash
curl -X DELETE "http://localhost:8000/api/report/abc-123-def-456"
```

**Response:**
```json
{
  "message": "Analysis deleted successfully"
}
```

## Tips

1. **Use descriptive account names** - Better account names lead to higher confidence scores
2. **Include descriptions** - Transaction descriptions improve classification accuracy
3. **Review flagged items** - Always have a CPA review items with confidence < 70%
4. **Conservative approach** - The system defaults to non-deductible when uncertain
5. **State-specific rules** - Future versions will include state-specific classification rules

## Troubleshooting

### CSV Upload Fails

- Ensure CSV is UTF-8 encoded
- Check that required columns are present: Account Number, Account Name, Amount
- Remove special characters from headers
- Try the sample CSV first: `examples/sample_gl.csv`

### Low Confidence Scores

- Add more descriptive account names
- Include transaction descriptions
- Use standard account numbering (5000s for COGS, 7000s for operating)

### PDF Generation Issues

- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check server logs for errors: `/tmp/server.log`

## Next Steps

1. Review the generated PDF with your CPA
2. Address any flagged items
3. Use the detailed CSV for tax preparation
4. Consult with a tax professional for final classification decisions

**Remember:** This tool provides decision-support only. All classifications should be reviewed by a qualified tax professional before use in tax filings.
