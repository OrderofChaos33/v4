"""FastAPI main application"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid
from typing import Optional
import tempfile
import os

from ..models.analysis import AnalysisRequest, AnalysisResult
from ..services.gl_parser import GLParserService
from ..services.classifier import ClassificationService
from ..services.report_generator import ReportGeneratorService

app = FastAPI(
    title="280E Expense Reclassification API",
    description="Automated 280E expense classification for cannabis operators",
    version="0.1.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for analysis results (temporary - use database in production)
analysis_store = {}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "280E Expense Reclassification API",
        "version": "0.1.0",
        "endpoints": {
            "analyze": "/api/analyze",
            "report_pdf": "/api/report/{analysis_id}/pdf",
            "report_csv": "/api/report/{analysis_id}/csv",
            "report_json": "/api/report/{analysis_id}/json"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/api/analyze")
async def analyze_expenses(
    file: UploadFile = File(..., description="GL CSV file"),
    state: str = Form(..., description="State of operation"),
    entity_structure: str = Form(default="single-entity", description="Entity structure"),
    tax_year: str = Form(..., description="Tax year")
):
    """
    Analyze GL expenses and classify per 280E rules
    
    Returns analysis result with classification details
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="Only CSV files are supported"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Parse GL data
        try:
            entries = GLParserService.parse_csv(file_content)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to parse CSV: {str(e)}"
            )
        
        # Classify entries
        classifications = ClassificationService.classify_entries(entries)
        
        # Calculate summary
        summary = ClassificationService.calculate_summary(classifications)
        
        # Create analysis result
        analysis_id = str(uuid.uuid4())
        request_data = AnalysisRequest(
            state=state,
            entity_structure=entity_structure,
            tax_year=tax_year
        )
        
        result = AnalysisResult(
            analysis_id=analysis_id,
            request=request_data,
            classifications=classifications,
            summary=summary
        )
        
        # Store result (in production, use database)
        analysis_store[analysis_id] = result
        
        return {
            "analysis_id": analysis_id,
            "summary": summary,
            "total_items": len(classifications),
            "message": "Analysis complete. Use analysis_id to retrieve reports."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/api/report/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get full analysis results as JSON"""
    if analysis_id not in analysis_store:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    result = analysis_store[analysis_id]
    return result


@app.get("/api/report/{analysis_id}/pdf")
async def get_pdf_report(analysis_id: str):
    """Generate and download PDF report"""
    if analysis_id not in analysis_store:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    try:
        result = analysis_store[analysis_id]
        pdf_bytes = ReportGeneratorService.generate_pdf(result)
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=280e_analysis_{analysis_id}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate PDF: {str(e)}"
        )


@app.get("/api/report/{analysis_id}/csv")
async def get_csv_report(analysis_id: str):
    """Generate and download CSV export"""
    if analysis_id not in analysis_store:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    try:
        result = analysis_store[analysis_id]
        csv_bytes = ReportGeneratorService.generate_csv(result.classifications)
        
        return Response(
            content=csv_bytes,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=280e_analysis_{analysis_id}.csv"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate CSV: {str(e)}"
        )


@app.get("/api/report/{analysis_id}/json")
async def get_json_report(analysis_id: str):
    """Generate and download JSON export"""
    if analysis_id not in analysis_store:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    try:
        result = analysis_store[analysis_id]
        json_bytes = ReportGeneratorService.generate_json(result)
        
        return Response(
            content=json_bytes,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=280e_analysis_{analysis_id}.json"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate JSON: {str(e)}"
        )


@app.delete("/api/report/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """Delete analysis results (cleanup)"""
    if analysis_id not in analysis_store:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    del analysis_store[analysis_id]
    return {"message": "Analysis deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
