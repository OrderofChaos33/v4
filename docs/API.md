# API Documentation

## Overview

The 280E Expense Reclassification API provides RESTful endpoints for analyzing cannabis operator GL data and generating audit-ready reports.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently no authentication required (add for production).

## Endpoints

### 1. Root / Health Check

#### GET /

Returns API information.

**Response:**
```json
{
  "message": "280E Expense Reclassification API",
  "version": "0.1.0",
  "endpoints": {
    "analyze": "/api/analyze",
    "report_pdf": "/api/report/{analysis_id}/pdf",
    "report_csv": "/api/report/{analysis_id}/csv",
    "report_json": "/api/report/{analysis_id}/json"
  }
}
```

#### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

---

### 2. Analyze Expenses

#### POST /api/analyze

Upload GL CSV file and receive classification analysis.

**Content-Type:** `multipart/form-data`

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| file | File | Yes | CSV file with GL data |
| state | String | Yes | State of operation (e.g., "CA") |
| entity_structure | String | No | Entity structure (default: "single-entity") |
| tax_year | String | Yes | Tax year (e.g., "2024") |

**Example Request (curl):**

```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -F "file=@/path/to/gl_data.csv" \
  -F "state=CA" \
  -F "entity_structure=single-entity" \
  -F "tax_year=2024"
```

**Example Request (Python):**

```python
import requests

files = {'file': open('gl_data.csv', 'rb')}
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
print(f"Analysis ID: {result['analysis_id']}")
```

**Response (200 OK):**

```json
{
  "analysis_id": "abc-123-def-456",
  "summary": {
    "total_expenses": 85450.00,
    "cogs": 39700.00,
    "deductible": 14150.00,
    "non_deductible": 31600.00,
    "cogs_percentage": 46.5,
    "deductible_percentage": 16.6,
    "non_deductible_percentage": 36.9,
    "avg_confidence": 82.5,
    "items_needing_review": 3,
    "review_percentage": 15.0,
    "tax_impact_estimate": 6636.00,
    "potential_savings": 11308.50
  },
  "total_items": 20,
  "message": "Analysis complete. Use analysis_id to retrieve reports."
}
```

**Error Responses:**

- `400 Bad Request`: Invalid CSV format or missing required fields
- `500 Internal Server Error`: Server processing error

---

### 3. Get Analysis Results

#### GET /api/report/{analysis_id}

Retrieve full analysis results as JSON.

**Path Parameters:**
- `analysis_id` (string): Unique analysis identifier

**Example Request:**

```bash
curl "http://localhost:8000/api/report/abc-123-def-456"
```

**Response (200 OK):**

```json
{
  "analysis_id": "abc-123-def-456",
  "request": {
    "state": "CA",
    "entity_structure": "single-entity",
    "tax_year": "2024"
  },
  "classifications": [
    {
      "account_number": "5000",
      "account_name": "Cost of Goods Sold - Flower",
      "description": "Wholesale flower purchase Q1",
      "amount": 15000.00,
      "classification": "Cost of Goods Sold",
      "confidence_score": 95.0,
      "rationale": "Direct product cost - qualifies as COGS under 280E...",
      "needs_review": false
    }
  ],
  "summary": { ... }
}
```

**Error Responses:**
- `404 Not Found`: Analysis ID not found

---

### 4. Download PDF Report

#### GET /api/report/{analysis_id}/pdf

Generate and download PDF report.

**Path Parameters:**
- `analysis_id` (string): Unique analysis identifier

**Example Request:**

```bash
curl "http://localhost:8000/api/report/abc-123-def-456/pdf" \
  --output report.pdf
```

**Response:**
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename=280e_analysis_{analysis_id}.pdf`

**Error Responses:**
- `404 Not Found`: Analysis ID not found
- `500 Internal Server Error`: PDF generation failed

---

### 5. Download CSV Export

#### GET /api/report/{analysis_id}/csv

Generate and download CSV export with detailed classifications.

**Path Parameters:**
- `analysis_id` (string): Unique analysis identifier

**Example Request:**

```bash
curl "http://localhost:8000/api/report/abc-123-def-456/csv" \
  --output report.csv
```

**Response:**
- Content-Type: `text/csv`
- Content-Disposition: `attachment; filename=280e_analysis_{analysis_id}.csv`

**CSV Format:**

```csv
Account Number,Account Name,Description,Amount,Classification,Confidence Score,Needs Review,Rationale
5000,Product Costs,Purchase,5000.00,Cost of Goods Sold,95.0,No,"Direct product cost..."
```

**Error Responses:**
- `404 Not Found`: Analysis ID not found

---

### 6. Download JSON Export

#### GET /api/report/{analysis_id}/json

Generate and download machine-readable JSON export.

**Path Parameters:**
- `analysis_id` (string): Unique analysis identifier

**Example Request:**

```bash
curl "http://localhost:8000/api/report/abc-123-def-456/json" \
  --output report.json
```

**Response:**
- Content-Type: `application/json`
- Complete analysis results with all details

**Error Responses:**
- `404 Not Found`: Analysis ID not found

---

### 7. Delete Analysis

#### DELETE /api/report/{analysis_id}

Delete analysis results from memory (cleanup).

**Path Parameters:**
- `analysis_id` (string): Unique analysis identifier

**Example Request:**

```bash
curl -X DELETE "http://localhost:8000/api/report/abc-123-def-456"
```

**Response (200 OK):**

```json
{
  "message": "Analysis deleted successfully"
}
```

**Error Responses:**
- `404 Not Found`: Analysis ID not found

---

## CSV Input Format

### Required Columns

- `Account Number`: GL account number (string)
- `Account Name`: Account description (string)
- `Amount`: Transaction amount (numeric)

### Optional Columns

- `Description`: Transaction description (string)
- `Date`: Transaction date (string, any format)
- `Vendor`: Vendor/payee name (string)

### Column Name Flexibility

The parser accepts various column name formats:
- Case insensitive
- Spaces or underscores
- Abbreviated names

Examples of accepted names:
- Account Number: `account_number`, `account`, `acct_num`, `acct`, `account #`
- Account Name: `account_name`, `name`, `description`, `acct_name`
- Amount: `amount`, `debit`, `credit`, `total`, `value`

### Sample CSV

```csv
Account Number,Account Name,Description,Amount,Date,Vendor
5000,Product Costs,Wholesale purchase,5000.00,2024-01-15,Grower Co
7000,Rent,Monthly rent,3000.00,2024-01-01,Landlord LLC
8000,Marketing,Social ads,2000.00,2024-01-10,Ad Agency
```

---

## Classification Types

### Cost of Goods Sold (COGS)
Deductible expenses directly related to product costs.

**Examples:**
- Product purchases
- Inventory costs
- Packaging materials
- Direct production labor
- Cultivation costs

### Deductible Operating Expenses
May be deductible based on allocation or post-rescheduling guidance.

**Examples:**
- Rent and utilities
- Insurance
- Professional fees
- Depreciation
- Bank fees

### Non-Deductible (280E)
Operating expenses subject to 280E restrictions.

**Examples:**
- Marketing and advertising
- Non-production salaries
- Employee benefits
- Travel and entertainment
- Consulting fees

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message description"
}
```

### Common Error Codes

- `400 Bad Request`: Invalid input data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Rate Limiting

Currently no rate limiting (implement for production).

---

## Interactive Documentation

Visit these URLs when the server is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Both provide interactive API testing and detailed schema documentation.

---

## Support

For issues or questions, refer to the main [README.md](../README.md) or create a GitHub issue.
