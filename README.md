# 280E Expense Classification Tool

Automated expense classification for cannabis operators per IRS Code Section 280E

## Overview

This is a backend-first SaaS MVP that helps cannabis operators classify general ledger (GL) expenses according to IRS 280E rules. The tool ingests GL data from CSV exports (QuickBooks, NetSuite, etc.), applies deterministic rules based on 280E precedent and post-rescheduling guidance, and generates audit-ready deduction analysis reports.

### Key Features

- **CSV Upload & Parsing**: Accepts GL exports from common accounting systems
- **Automated Classification**: Classifies expenses as:
  - COGS (Cost of Goods Sold - Deductible)
  - Deductible operating expenses
  - Non-deductible per 280E
- **Confidence Scoring**: Assigns 0-100% confidence scores to each classification
- **Audit Trail**: Tracks detailed rationale for each classification decision
- **CPA Review Flags**: Automatically flags ambiguous or low-confidence items
- **Multiple Report Formats**: 
  - PDF (audit-ready with executive summary, financial analysis, and detailed tables)
  - CSV (machine-readable export)
  - JSON (programmatic access)
- **Manual Override Support**: Allows users to override classifications
- **Web Interface**: Minimal upload → review → download workflow
- **Stateless Design**: No persistent storage required for MVP
- **Mock LLM**: Placeholder for future LLM integration for ambiguous classifications

### Important Disclaimer

⚠️ **This tool provides decision-support only and does not constitute tax advice, legal advice, or accounting services.** All classifications should be reviewed by a qualified tax professional before filing. The estimated tax impact is illustrative only and actual tax liability may vary.

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/OrderofChaos33/v4.git
cd v4
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

1. Start the FastAPI server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. Open your browser and navigate to:
```
http://localhost:8000
```

3. Upload your GL CSV file and fill in the required information:
   - Company name (optional)
   - State of operation
   - Entity structure
   - Tax year/period
   - Schedule status (Schedule I for current 280E rules, Schedule III for post-rescheduling)

4. Review the classification results and download reports in your preferred format

### API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### API Endpoints

- `POST /api/upload` - Upload and process GL CSV file
- `GET /api/session/{session_id}` - Retrieve classification results
- `POST /api/session/{session_id}/override` - Override a classification
- `GET /api/session/{session_id}/report/pdf` - Download PDF report
- `GET /api/session/{session_id}/report/csv` - Download CSV export
- `GET /api/session/{session_id}/report/json` - Download JSON export
- `GET /health` - Health check endpoint

## CSV File Format

The tool accepts CSV files with the following columns (column names are case-insensitive and flexible):

**Required columns:**
- `date` (or `transaction_date`, `trans_date`, `posting_date`)
- `account_code` (or `account_number`, `account`, `acct_code`, `gl_account`)
- `account_name` (or `account_description`, `account_desc`, `acct_name`)
- `description` (or `memo`, `desc`, `transaction_description`)
- `amount` (or `debit`, `credit`, `total`, `net_amount`)

**Optional columns:**
- `category` (or `type`, `expense_type`, `class`)

See `sample_gl.csv` for an example file format.

## Classification Logic

### IRS 280E Rules

IRS Code Section 280E prohibits businesses trafficking in Schedule I or II controlled substances from deducting ordinary business expenses, **except for Cost of Goods Sold (COGS)**.

### Classification Categories

1. **COGS (Deductible)**
   - Direct costs attributable to inventory production/purchase
   - Examples: inventory purchases, cultivation labor, growing supplies, packaging materials
   - Account codes: 5000-5099 series

2. **Deductible Operating Expenses**
   - Allowed for non-cannabis portions of business or post-rescheduling
   - Examples: rent, utilities (if properly allocated)

3. **Non-Deductible (280E)**
   - General business expenses for Schedule I/II businesses
   - Examples: administrative salaries, marketing, professional fees, insurance

### Confidence Scoring

- **High confidence (80-100%)**: Clear classification based on account codes or strong keyword matches
- **Medium confidence (60-79%)**: Moderate keyword matches, may need review
- **Low confidence (<60%)**: Ambiguous, requires CPA review

## Project Structure

```
v4/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── models/                 # Pydantic data models
│   │   ├── __init__.py
│   │   ├── gl_entry.py
│   │   ├── classification_result.py
│   │   └── report_data.py
│   └── services/               # Business logic
│       ├── __init__.py
│       ├── gl_parser.py        # CSV parsing
│       ├── classification_engine.py  # 280E classification
│       ├── report_generator.py # PDF generation
│       └── export_service.py   # CSV/JSON export
├── templates/
│   └── index.html              # Web interface
├── static/                     # Static assets
├── sample_gl.csv               # Sample GL data
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Testing

### Manual Testing

1. Use the provided `sample_gl.csv` file to test the application
2. Upload through the web interface at `http://localhost:8000`
3. Verify classification results and download reports

### Sample Test Case

```bash
# Start the server
uvicorn app.main:app --reload

# In another terminal, test with curl
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@sample_gl.csv" \
  -F "state=California" \
  -F "entity_structure=Single Entity" \
  -F "tax_year=2024" \
  -F "company_name=Test Company"
```

## Security Considerations

- **No credentials storage**: Stateless design, no user accounts
- **Input validation**: All inputs validated via Pydantic models
- **File type restrictions**: Only CSV files accepted
- **Secure file handling**: Files processed in memory, not permanently stored
- **CORS enabled**: For development; restrict in production
- **No sensitive data logging**: Classification logic doesn't log sensitive financial details

## Future Enhancements (TODOs)

### High Priority
- [ ] Real LLM integration (OpenAI, Anthropic) for ambiguous classifications
- [ ] Persistent storage (database) for session management
- [ ] User authentication and multi-tenant support
- [ ] Batch processing for large GL files
- [ ] Enhanced validation and error handling
- [ ] Unit and integration tests

### Medium Priority
- [ ] Support for multi-entity structures with allocation rules
- [ ] State-specific tax calculations and compliance rules
- [ ] Comparison reports (year-over-year, pre/post rescheduling)
- [ ] Export to tax software formats (e.g., ProSeries, Lacerte)
- [ ] CPA collaboration features (comments, approvals)
- [ ] Advanced filtering and search in web interface

### Low Priority
- [ ] Integration with QuickBooks/NetSuite APIs (direct connection)
- [ ] METRC integration for inventory tracking
- [ ] Forecasting and scenario planning
- [ ] Mobile-responsive design improvements
- [ ] Multi-language support
- [ ] Advanced analytics dashboard

### Infrastructure
- [ ] Containerization (Docker)
- [ ] CI/CD pipeline
- [ ] Automated testing suite
- [ ] Production deployment guide (AWS, GCP, Azure)
- [ ] Monitoring and logging setup
- [ ] Rate limiting and API throttling
- [ ] Database migrations (when persistent storage added)

## Technical Stack

- **Backend**: FastAPI (Python)
- **Data Processing**: Pandas
- **PDF Generation**: ReportLab
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Validation**: Pydantic
- **Server**: Uvicorn (ASGI)

## Contributing

This is an MVP. Contributions are welcome! Please ensure:
- Code follows PEP 8 style guidelines
- All new features include appropriate documentation
- Security best practices are maintained
- Disclaimer language is preserved

## License

See LICENSE.txt for details.

## Support

For questions or issues, please open an issue on GitHub.

---

**Remember**: This tool is for decision-support only. Always consult with qualified tax professionals before making tax-related decisions.