# 280E Expense Reclassification MVP

Automated IRS 280E expense classification and audit-ready deduction reporting for cannabis operators.

## Overview

This SaaS MVP helps cannabis operators classify general ledger expenses according to IRS Section 280E regulations, generating audit-ready reports with quantified financial impact. The system uses deterministic rules based on 280E precedent and IRS guidance, with mock LLM assistance for ambiguous cases.

## Features

- **GL Data Parsing**: Upload CSV exports from QuickBooks/NetSuite
- **Automated Classification**: Classify expenses as COGS, Deductible, or Non-Deductible per 280E
- **Confidence Scoring**: Each classification includes 0-100% confidence score
- **Audit Trail**: Track rationale/explanation for every classification decision
- **CPA Review Flags**: Automatic flagging of low-confidence or ambiguous items
- **PDF Reports**: Executive summary with before/after analysis and tax impact
- **Machine-Readable Exports**: CSV and JSON formats for further analysis
- **Conservative Approach**: Defaults to non-deductible when uncertain

## Quick Start

### Prerequisites

- Python 3.9+
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/OrderofChaos33/v4.git
cd v4
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

Start the FastAPI server:

```bash
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API documentation (Swagger UI): `http://localhost:8000/docs`

### Usage

#### 1. Prepare Your GL Export

Export your general ledger data as a CSV file with these columns:
- `Account Number` (required)
- `Account Name` (required)
- `Amount` (required)
- `Description` (optional but recommended)
- `Date` (optional)
- `Vendor` (optional)

See `examples/sample_gl.csv` for a sample format.

#### 2. Analyze Expenses

Use the API to analyze your GL data:

```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -F "file=@examples/sample_gl.csv" \
  -F "state=CA" \
  -F "entity_structure=single-entity" \
  -F "tax_year=2024"
```

Response:
```json
{
  "analysis_id": "abc-123-def-456",
  "summary": {
    "total_expenses": 85450.00,
    "cogs": 39700.00,
    "deductible": 14150.00,
    "non_deductible": 31600.00,
    "avg_confidence": 82.5,
    "items_needing_review": 3
  },
  "total_items": 20,
  "message": "Analysis complete. Use analysis_id to retrieve reports."
}
```

#### 3. Download Reports

**PDF Report** (Executive Summary):
```bash
curl "http://localhost:8000/api/report/{analysis_id}/pdf" --output report.pdf
```

**CSV Export** (Detailed Data):
```bash
curl "http://localhost:8000/api/report/{analysis_id}/csv" --output report.csv
```

**JSON Export** (Machine-Readable):
```bash
curl "http://localhost:8000/api/report/{analysis_id}/json" --output report.json
```

## API Endpoints

### POST /api/analyze
Upload GL CSV and get classification analysis

**Parameters:**
- `file`: CSV file (multipart/form-data)
- `state`: State of operation (form field)
- `entity_structure`: Entity type (form field, default: "single-entity")
- `tax_year`: Tax year (form field)

**Returns:** Analysis summary with analysis_id

### GET /api/report/{analysis_id}
Get full analysis results as JSON

### GET /api/report/{analysis_id}/pdf
Download PDF report

### GET /api/report/{analysis_id}/csv
Download CSV export

### GET /api/report/{analysis_id}/json
Download machine-readable JSON

### DELETE /api/report/{analysis_id}
Delete analysis results (cleanup)

## Classification Logic

### Cost of Goods Sold (COGS)
- Direct product costs
- Inventory purchases
- Packaging and labels
- Cultivation/production costs
- Raw materials
- Direct production labor

**Deductible** ✅

### Deductible Operating Expenses
- Rent/lease payments
- Utilities
- Insurance
- Professional fees (legal, accounting)
- Depreciation
- Bank fees and interest
- Equipment maintenance
- Licenses and permits
- Property taxes

**May be deductible** ⚠️ (consult CPA)

### Non-Deductible (280E Restricted)
- Marketing and advertising
- Salaries and wages (non-production)
- Employee benefits
- Travel and entertainment
- Consulting fees
- Vehicle expenses
- Training and development

**Non-deductible** ❌

## Confidence Scoring

- **90-100%**: High confidence, clear keyword/pattern match
- **70-89%**: Medium confidence, likely correct but review recommended
- **Below 70%**: Low confidence, requires CPA review

All items below 70% confidence are automatically flagged for review.

## Report Contents

### PDF Report Includes:
1. **Executive Summary**: Totals by category with percentages
2. **Tax Impact Analysis**: Estimated tax consequences
3. **Key Findings**: Actionable recommendations
4. **Detailed Classification Table**: Line-by-line breakdown (first 50 items)
5. **Legal Disclaimer**: Decision-support notice

### CSV Export Includes:
- All classifications with full details
- Confidence scores
- Review flags
- Rationale for each classification

## Architecture

```
src/
├── api/
│   └── main.py           # FastAPI application and routes
├── models/
│   ├── gl_entry.py       # GL entry and classification types
│   └── analysis.py       # Request/response models
├── services/
│   ├── gl_parser.py      # CSV parsing and normalization
│   ├── classifier.py     # 280E classification engine
│   └── report_generator.py  # PDF/CSV/JSON generation
└── utils/                # Helper utilities

examples/
└── sample_gl.csv         # Sample GL data for testing

tests/
└── ...                   # Test suite (TBD)
```

## Testing

Test the application with the sample data:

```bash
# Start server
python -m uvicorn src.api.main:app --reload

# In another terminal, test with sample data
curl -X POST "http://localhost:8000/api/analyze" \
  -F "file=@examples/sample_gl.csv" \
  -F "state=CA" \
  -F "tax_year=2024"
```

## Security & Privacy

- No persistent storage by default (in-memory only)
- Temporary file handling with automatic cleanup
- No external API calls (mock LLM)
- CORS configured (adjust for production)
- Stateless architecture
- No PHI/PII collection

## Limitations & Disclaimers

⚠️ **IMPORTANT**: This tool provides **decision-support only** and does NOT constitute tax advice.

- All classifications should be reviewed by a qualified CPA or tax attorney
- Rules are based on current 280E interpretation and may not reflect latest guidance
- Conservative classification approach may not maximize deductions
- Mock LLM logic (real AI can be integrated later)
- Single-entity focus (multi-entity requires enhancement)
- No payroll, inventory, METRC, or compliance features

## TODOs for Iteration

### High Priority
- [ ] Real LLM integration (OpenAI, Anthropic) for ambiguous cases
- [ ] Persistent database storage (PostgreSQL/MongoDB)
- [ ] User authentication and multi-tenant support
- [ ] Manual override/review interface
- [ ] Enhanced state-specific rules
- [ ] Multi-entity structure support

### Medium Priority
- [ ] Batch processing for large GL files
- [ ] Historical comparison reports
- [ ] More sophisticated COGS allocation rules
- [ ] Integration with QuickBooks/NetSuite APIs
- [ ] Email report delivery
- [ ] Audit log export

### Low Priority
- [ ] Web-based UI for upload/review
- [ ] Advanced analytics dashboard
- [ ] Tax form pre-population (Schedule C, 1120)
- [ ] CPA collaboration features
- [ ] Scenario modeling ("what-if" analysis)

## Development

Run tests:
```bash
pytest
```

Code formatting:
```bash
black src/
```

Linting:
```bash
pylint src/
```

## Production Deployment

For production deployment:

1. Set up environment variables in `.env` file
2. Configure database connection
3. Enable authentication/authorization
4. Set proper CORS origins
5. Use production ASGI server (gunicorn + uvicorn workers)
6. Enable HTTPS
7. Set up monitoring and logging
8. Implement rate limiting
9. Add file size limits

Example production run:
```bash
gunicorn src.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

## Support

For issues or questions:
- Create an issue in GitHub
- Review API documentation at `/docs`
- Check example data in `examples/`

## License

See LICENSE.txt for details.

## Compliance Notice

This software is designed to assist with tax compliance but does not replace professional tax advice. Cannabis operators should consult with qualified tax professionals familiar with IRS Section 280E and current regulatory guidance. Classifications are estimates based on automated analysis and may not reflect specific circumstances or the latest IRS interpretations.