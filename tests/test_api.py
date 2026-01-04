"""Tests for API endpoints"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app
import io


client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "280E Expense Reclassification API" in response.json()["message"]


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_analyze_endpoint_with_valid_csv():
    """Test analyze endpoint with valid CSV"""
    csv_content = b"""Account Number,Account Name,Amount,Description
5000,Product Costs,1000.00,Wholesale purchase
7000,Rent,2000.00,Monthly rent
8000,Marketing,1500.00,Advertising
"""
    
    files = {"file": ("test.csv", io.BytesIO(csv_content), "text/csv")}
    data = {
        "state": "CA",
        "entity_structure": "single-entity",
        "tax_year": "2024"
    }
    
    response = client.post("/api/analyze", files=files, data=data)
    
    assert response.status_code == 200
    result = response.json()
    assert "analysis_id" in result
    assert "summary" in result
    assert result["total_items"] == 3


def test_analyze_endpoint_with_invalid_file():
    """Test analyze endpoint with non-CSV file"""
    files = {"file": ("test.txt", io.BytesIO(b"not a csv"), "text/plain")}
    data = {
        "state": "CA",
        "tax_year": "2024"
    }
    
    response = client.post("/api/analyze", files=files, data=data)
    
    assert response.status_code == 400
    assert "Only CSV files are supported" in response.json()["detail"]


def test_get_analysis_not_found():
    """Test getting non-existent analysis"""
    response = client.get("/api/report/nonexistent")
    assert response.status_code == 404


def test_full_workflow():
    """Test complete workflow from upload to report download"""
    # Upload and analyze
    csv_content = b"""Account Number,Account Name,Amount
5000,Product Costs,5000.00
7000,Rent,3000.00
"""
    
    files = {"file": ("test.csv", io.BytesIO(csv_content), "text/csv")}
    data = {"state": "CA", "tax_year": "2024"}
    
    response = client.post("/api/analyze", files=files, data=data)
    assert response.status_code == 200
    analysis_id = response.json()["analysis_id"]
    
    # Get JSON report
    response = client.get(f"/api/report/{analysis_id}")
    assert response.status_code == 200
    assert response.json()["analysis_id"] == analysis_id
    
    # Get PDF report
    response = client.get(f"/api/report/{analysis_id}/pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    
    # Get CSV report
    response = client.get(f"/api/report/{analysis_id}/csv")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv"
    
    # Delete analysis
    response = client.delete(f"/api/report/{analysis_id}")
    assert response.status_code == 200
    
    # Verify deleted
    response = client.get(f"/api/report/{analysis_id}")
    assert response.status_code == 404
