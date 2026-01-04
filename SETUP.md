# 280E Expense Classification Tool - Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
# Option 1: Use the startup script
./run.sh

# Option 2: Run directly with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Access the Application
Open your browser and navigate to: http://localhost:8000

### 4. Test the Application
```bash
# Run the functionality tests
python tests.py
```

## Usage

### Web Interface
1. Upload your GL CSV file
2. Fill in company information (state, entity structure, tax year)
3. Select the cannabis schedule status (Schedule I for current 280E rules)
4. Click "Analyze GL Data"
5. Review the classification results
6. Download reports in PDF, CSV, or JSON format

### API Usage

#### Upload and Classify GL Data
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@sample_gl.csv" \
  -F "state=California" \
  -F "entity_structure=Single Entity" \
  -F "tax_year=2024" \
  -F "company_name=My Cannabis Company"
```

Response:
```json
{
  "session_id": "session_1",
  "entry_count": 30,
  "summary": {
    "total_expenses": 222060.0,
    "cogs": 132200.0,
    "deductible_operating": 13090.0,
    "non_deductible": 76770.0,
    "total_deductible": 145290.0,
    "estimated_tax_savings": 30510.9,
    "needs_review": 13
  },
  "needs_review_count": 13
}
```

#### Retrieve Classification Results
```bash
curl "http://localhost:8000/api/session/session_1"
```

#### Download Reports
```bash
# PDF Report
curl "http://localhost:8000/api/session/session_1/report/pdf" -o report.pdf

# CSV Export
curl "http://localhost:8000/api/session/session_1/report/csv" -o export.csv

# JSON Export
curl "http://localhost:8000/api/session/session_1/report/json" -o export.json
```

#### Override a Classification
```bash
curl -X POST "http://localhost:8000/api/session/session_1/override" \
  -F "entry_index=0" \
  -F "new_classification=Deductible"
```

## CSV File Format

Your GL CSV file should include these columns (column names are flexible):

**Required:**
- Date (or transaction_date, trans_date, posting_date)
- Account Code (or account_number, account, acct_code)
- Account Name (or account_description, account_desc)
- Description (or memo, desc, transaction_description)
- Amount (or debit, credit, total)

**Optional:**
- Category (or type, expense_type, class)

See `sample_gl.csv` for a complete example.

## Classification Logic

### COGS (Deductible)
Expenses directly attributable to inventory production:
- Inventory purchases
- Cultivation labor and supplies
- Growing materials (seeds, clones, nutrients)
- Packaging materials
- Product testing
- Account codes: 5000-5099 series

### Deductible Operating Expenses
Allowed for post-rescheduling or non-cannabis business:
- May include: rent, utilities (if properly allocated)
- Professional fees (with documentation)
- Software and technology

### Non-Deductible (280E)
General business expenses for Schedule I/II businesses:
- Administrative salaries
- Marketing and advertising
- Insurance
- Office supplies
- General operations

## Confidence Scores

- **High (80-100%)**: Clear classification based on account codes or strong indicators
- **Medium (60-79%)**: Moderate confidence, may benefit from review
- **Low (<60%)**: Ambiguous, requires CPA review

Entries with confidence below 80% are automatically flagged for review.

## Reports

### PDF Report Includes:
- Executive summary
- Financial impact analysis
- Before/after deductible totals
- Estimated tax impact
- Confidence and risk analysis
- Detailed classification table
- Audit-ready rationale for each entry
- Legal disclaimer

### CSV Export Includes:
- All GL entries with classifications
- Confidence scores
- Review flags
- Rationale for each classification
- Summary statistics

### JSON Export Includes:
- Machine-readable format
- Complete classification data
- Suitable for integration with other systems

## Security & Privacy

- **Stateless Design**: No persistent storage of financial data
- **In-Memory Processing**: Files are processed and discarded
- **No User Accounts**: No authentication required for MVP
- **Input Validation**: All inputs validated via Pydantic models
- **Secure File Handling**: Only CSV files accepted

## Troubleshooting

### "Module not found" errors
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### CSV parsing errors
Ensure your CSV file has the required columns. Check the sample file for reference.

### Port already in use
Change the port in the startup command:
```bash
uvicorn app.main:app --reload --port 8080
```

### Permission errors on run.sh
Make the script executable:
```bash
chmod +x run.sh
```

## Development

### Project Structure
```
v4/
├── app/
│   ├── main.py              # FastAPI application
│   ├── models/              # Data models
│   └── services/            # Business logic
├── templates/               # HTML templates
├── static/                  # Static assets
├── sample_gl.csv           # Sample data
├── tests.py                # Functionality tests
└── requirements.txt        # Dependencies
```

### Running Tests
```bash
python tests.py
```

This will:
- Parse the sample GL file
- Classify all entries
- Generate PDF, CSV, and JSON reports
- Verify all functionality

### API Documentation
Interactive API docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Production Deployment

For production deployment, consider:

1. **Use a production ASGI server**:
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. **Add authentication** for multi-tenant usage

3. **Implement rate limiting** to prevent abuse

4. **Add persistent storage** (database) for session management

5. **Configure CORS** appropriately for your domain

6. **Set up HTTPS** with SSL certificates

7. **Add monitoring and logging** (e.g., Sentry, DataDog)

8. **Implement file size limits** and validation

9. **Add backup and disaster recovery** procedures

10. **Review and update security settings**

## Support

For issues or questions:
- Check the main README.md for detailed documentation
- Open an issue on GitHub
- Review API documentation at /docs

## Disclaimer

This tool provides decision-support only and does not constitute tax advice. All classifications should be reviewed by a qualified tax professional before filing.
