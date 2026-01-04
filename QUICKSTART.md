# Quick Start Guide

Get started with the 280E MVP in 3 simple steps!

## Step 1: Install

```bash
# Clone repository
git clone https://github.com/OrderofChaos33/v4.git
cd v4

# Quick start (runs tests and starts server)
chmod +x start.sh
./start.sh
```

## Step 2: Analyze

Open a new terminal and run:

```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -F "file=@examples/sample_gl.csv" \
  -F "state=CA" \
  -F "tax_year=2024"
```

Save the `analysis_id` from the response.

## Step 3: Download Reports

```bash
# Replace {analysis_id} with your actual ID
curl "http://localhost:8000/api/report/{analysis_id}/pdf" -o report.pdf
curl "http://localhost:8000/api/report/{analysis_id}/csv" -o report.csv
```

Open `report.pdf` to see your audit-ready 280E classification report!

## What You Get

✅ **Executive Summary** - Total expenses by category
✅ **Tax Impact Analysis** - Estimated tax consequences  
✅ **Detailed Breakdown** - Every line item classified
✅ **Confidence Scores** - Know which items to review
✅ **Legal Disclaimer** - Appropriate for CPA review

## Next Steps

1. Replace `examples/sample_gl.csv` with your own GL export
2. Review the PDF report with your CPA
3. Use the CSV export for tax preparation
4. Check items flagged for review

## API Documentation

Visit http://localhost:8000/docs for interactive API documentation.

## Support

- 📖 Full documentation in `README.md`
- 🔧 Setup guide: `docs/SETUP.md`
- 💡 Examples: `docs/EXAMPLES.md`
- 🚀 Deployment: `docs/DEPLOYMENT.md`

## Requirements

- Python 3.9+
- 2GB RAM minimum
- Modern web browser

---

**Ready in under 5 minutes!**
