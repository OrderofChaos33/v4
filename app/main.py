"""Main FastAPI application for 280E expense classification."""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import Response, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import json
from pathlib import Path

from .models import ClassificationResult, ReportData, GLEntry, ClassificationType
from .services import GLParser, Classification280E, ReportGenerator, ExportService

# Create FastAPI app
app = FastAPI(
    title="280E Expense Classification API",
    description="Automated expense classification for cannabis operators per IRS 280E",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path(__file__).parent.parent / "static"
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# In-memory storage for session data (stateless for MVP)
session_storage = {}


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main upload page."""
    html_path = Path(__file__).parent.parent / "templates" / "index.html"
    if html_path.exists():
        return FileResponse(html_path)
    return HTMLResponse(content="""
        <html>
            <head><title>280E Classification Tool</title></head>
            <body>
                <h1>280E Expense Classification Tool</h1>
                <p>Upload your GL data to get started.</p>
                <p>API documentation available at <a href="/docs">/docs</a></p>
            </body>
        </html>
    """)


@app.post("/api/upload")
async def upload_gl_file(
    file: UploadFile = File(...),
    state: str = Form(...),
    entity_structure: str = Form(...),
    tax_year: str = Form(...),
    company_name: Optional[str] = Form("Cannabis Operator"),
    schedule_status: Optional[str] = Form("Schedule I")
):
    """
    Upload and parse GL CSV file.
    
    Args:
        file: CSV file containing GL data
        state: State of operation
        entity_structure: Entity structure (single-entity, multi-entity, etc.)
        tax_year: Tax year/period
        company_name: Optional company name
        schedule_status: Schedule status (Schedule I, Schedule III, etc.)
        
    Returns:
        Session ID and parsed entry count
    """
    try:
        # Read file content
        content = await file.read()
        
        # Parse CSV
        parser = GLParser()
        entries = parser.parse_csv(content)
        
        # Classify entries
        classifier = Classification280E(schedule_status=schedule_status)
        classified_entries = classifier.classify_entries(entries)
        
        # Create result object
        result = ClassificationResult(entries=classified_entries)
        result.calculate_summary()
        
        # Create report data
        report_data = ReportData(
            state=state,
            entity_structure=entity_structure,
            tax_year=tax_year,
            company_name=company_name
        )
        
        # Generate session ID (simple counter for MVP)
        session_id = f"session_{len(session_storage) + 1}"
        
        # Store in session
        session_storage[session_id] = {
            'result': result,
            'report_data': report_data
        }
        
        return {
            'session_id': session_id,
            'entry_count': len(entries),
            'summary': result.summary,
            'needs_review_count': result.needs_review_count
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/session/{session_id}")
async def get_session_data(session_id: str):
    """
    Get classification results for a session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Classification results
    """
    if session_id not in session_storage:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = session_storage[session_id]
    result = session['result']
    
    return {
        'entries': [entry.dict() for entry in result.entries],
        'summary': result.summary
    }


@app.post("/api/session/{session_id}/override")
async def override_classification(
    session_id: str,
    entry_index: int = Form(...),
    new_classification: str = Form(...)
):
    """
    Override classification for a specific entry.
    
    Args:
        session_id: Session identifier
        entry_index: Index of entry to override
        new_classification: New classification value
        
    Returns:
        Updated summary
    """
    if session_id not in session_storage:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = session_storage[session_id]
    result = session['result']
    
    if entry_index < 0 or entry_index >= len(result.entries):
        raise HTTPException(status_code=400, detail="Invalid entry index")
    
    try:
        classification = ClassificationType(new_classification)
        result.entries[entry_index].override_classification = classification
        result.calculate_summary()
        
        return {
            'success': True,
            'summary': result.summary
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid classification type")


@app.get("/api/session/{session_id}/report/pdf")
async def download_pdf_report(session_id: str):
    """
    Generate and download PDF report.
    
    Args:
        session_id: Session identifier
        
    Returns:
        PDF file
    """
    if session_id not in session_storage:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = session_storage[session_id]
    result = session['result']
    report_data = session['report_data']
    
    # Generate PDF
    generator = ReportGenerator()
    pdf_bytes = generator.generate_pdf(result, report_data)
    
    # Return as response
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=280e_report_{session_id}.pdf"
        }
    )


@app.get("/api/session/{session_id}/report/csv")
async def download_csv_report(session_id: str):
    """
    Generate and download CSV export.
    
    Args:
        session_id: Session identifier
        
    Returns:
        CSV file
    """
    if session_id not in session_storage:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = session_storage[session_id]
    result = session['result']
    
    # Export to CSV
    exporter = ExportService()
    csv_bytes = exporter.export_to_csv(result)
    
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=280e_export_{session_id}.csv"
        }
    )


@app.get("/api/session/{session_id}/report/json")
async def download_json_report(session_id: str):
    """
    Generate and download JSON export.
    
    Args:
        session_id: Session identifier
        
    Returns:
        JSON file
    """
    if session_id not in session_storage:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = session_storage[session_id]
    result = session['result']
    
    # Export to JSON
    exporter = ExportService()
    json_bytes = exporter.export_to_json(result)
    
    return Response(
        content=json_bytes,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=280e_export_{session_id}.json"
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
