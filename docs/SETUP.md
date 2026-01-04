# Setup Guide

## System Requirements

- Python 3.9 or higher
- pip package manager
- 2GB RAM minimum
- 1GB free disk space

## Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/OrderofChaos33/v4.git
cd v4
```

### 2. Create Virtual Environment

**On Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
python -c "import fastapi; import pandas; import reportlab; print('All dependencies installed successfully')"
```

## Running the Application

### Development Mode

Start the server with auto-reload:

```bash
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Production Mode

For production deployment, use gunicorn:

```bash
pip install gunicorn
gunicorn src.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=src --cov-report=html
```

## Troubleshooting

### Import Errors

If you see import errors, ensure you're in the project root directory and the virtual environment is activated.

### Port Already in Use

If port 8000 is in use, specify a different port:

```bash
python -m uvicorn src.api.main:app --reload --port 8001
```

### CSV Parsing Issues

- Ensure CSV is UTF-8 encoded
- Check that required columns are present: Account Number, Account Name, Amount
- Remove any special characters from column names

### PDF Generation Issues

If PDF generation fails, ensure ReportLab is properly installed:

```bash
pip install --force-reinstall reportlab
```

## Configuration

### Environment Variables

Create a `.env` file in the project root (optional):

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# File Upload Limits
MAX_FILE_SIZE_MB=50
```

### CORS Configuration

To restrict CORS origins, edit `src/api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)
```

## Next Steps

1. Review the [README.md](../README.md) for usage instructions
2. Check the [API documentation](http://localhost:8000/docs) after starting the server
3. Try the example workflow with `examples/sample_gl.csv`
4. Review TODOs in README for enhancement opportunities
