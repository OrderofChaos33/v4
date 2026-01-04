"""Report Generator Service - PDF and CSV export generation"""

import io
import csv
from datetime import datetime
from typing import List, BinaryIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from ..models.analysis import AnalysisResult, ExpenseClassification


class ReportGeneratorService:
    """Service for generating audit-ready PDF and CSV reports"""
    
    @staticmethod
    def generate_pdf(analysis: AnalysisResult) -> bytes:
        """
        Generate PDF report for analysis results
        
        Args:
            analysis: AnalysisResult object
            
        Returns:
            PDF file as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        story.append(Paragraph("280E Expense Classification Analysis", title_style))
        story.append(Paragraph(
            f"Analysis ID: {analysis.analysis_id}",
            styles['Normal']
        ))
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.3 * inch))
        
        # Disclaimer
        disclaimer_text = (
            "<b>IMPORTANT DISCLAIMER:</b> This report is provided for decision-support purposes only "
            "and does not constitute tax advice. All classifications should be reviewed by a qualified "
            "tax professional (CPA or tax attorney) familiar with IRS Section 280E and cannabis industry "
            "regulations. The classifications herein are based on automated analysis and may not reflect "
            "your specific circumstances or the latest IRS guidance."
        )
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#e74c3c'),
            borderWidth=1,
            borderColor=colors.HexColor('#e74c3c'),
            borderPadding=10,
            spaceAfter=20
        )
        story.append(Paragraph(disclaimer_text, disclaimer_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", heading_style))
        
        summary = analysis.summary
        summary_data = [
            ['Metric', 'Amount', 'Percentage'],
            ['Total Expenses', f"${summary['total_expenses']:,.2f}", '100.0%'],
            ['Cost of Goods Sold (COGS)', f"${summary['cogs']:,.2f}", f"{summary.get('cogs_percentage', 0):.1f}%"],
            ['Deductible Operating Expenses', f"${summary['deductible']:,.2f}", f"{summary.get('deductible_percentage', 0):.1f}%"],
            ['Non-Deductible (280E)', f"${summary['non_deductible']:,.2f}", f"{summary.get('non_deductible_percentage', 0):.1f}%"],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 1.5*inch, 1*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#ecf0f1')),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # Tax Impact
        story.append(Paragraph("Estimated Tax Impact", heading_style))
        
        tax_data = [
            ['Metric', 'Value'],
            ['Estimated Tax on Non-Deductible Expenses (21%)', f"${summary.get('tax_impact_estimate', 0):,.2f}"],
            ['Potential Tax Savings from Proper Classification', f"${summary.get('potential_savings', 0):,.2f}"],
            ['Average Classification Confidence', f"{summary.get('avg_confidence', 0):.1f}%"],
            ['Items Requiring CPA Review', f"{summary.get('items_needing_review', 0)} ({summary.get('review_percentage', 0):.1f}%)"],
        ]
        
        tax_table = Table(tax_data, colWidths=[4*inch, 2*inch])
        tax_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(tax_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # Key Findings
        story.append(Paragraph("Key Findings & Recommendations", heading_style))
        
        findings = []
        if summary.get('non_deductible_percentage', 0) > 50:
            findings.append(
                "• High percentage of non-deductible expenses detected. Consider restructuring "
                "to allocate more costs to COGS where appropriate."
            )
        
        if summary.get('items_needing_review', 0) > 0:
            findings.append(
                f"• {summary.get('items_needing_review', 0)} items flagged for CPA review due to "
                "low confidence or ambiguous classification."
            )
        
        if summary.get('avg_confidence', 0) < 70:
            findings.append(
                "• Overall confidence is below 70%. Professional review strongly recommended "
                "before finalizing tax return."
            )
        else:
            findings.append(
                "• High overall classification confidence. Review flagged items with your CPA."
            )
        
        findings.append(
            "• Conservative classification approach used per 280E precedent. Some expenses "
            "may be reclassifiable with proper documentation."
        )
        
        for finding in findings:
            story.append(Paragraph(finding, styles['Normal']))
        
        story.append(Spacer(1, 0.3 * inch))
        
        # Page break before detailed table
        story.append(PageBreak())
        
        # Detailed Classification Table
        story.append(Paragraph("Detailed Expense Classification", heading_style))
        story.append(Spacer(1, 0.1 * inch))
        
        # Build table data
        detail_data = [['Acct #', 'Account Name', 'Amount', 'Classification', 'Confidence', 'Review']]
        
        for item in analysis.classifications[:50]:  # Limit to first 50 for PDF
            detail_data.append([
                item.account_number,
                item.account_name[:30],  # Truncate long names
                f"${item.amount:,.2f}",
                item.classification.value[:20],  # Abbreviate
                f"{item.confidence_score:.0f}%",
                "Yes" if item.needs_review else "No"
            ])
        
        if len(analysis.classifications) > 50:
            detail_data.append([
                '', 
                f'... and {len(analysis.classifications) - 50} more items', 
                '', '', '', ''
            ])
        
        detail_table = Table(detail_data, colWidths=[0.7*inch, 2*inch, 1*inch, 1.5*inch, 0.8*inch, 0.6*inch])
        detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
            ('ALIGN', (4, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        story.append(detail_table)
        
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph(
            "<i>Note: Complete detailed data available in accompanying CSV export.</i>",
            styles['Normal']
        ))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.read()
    
    @staticmethod
    def generate_csv(classifications: List[ExpenseClassification]) -> bytes:
        """
        Generate CSV export of classifications
        
        Args:
            classifications: List of ExpenseClassification objects
            
        Returns:
            CSV file as bytes
        """
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        
        # Header
        writer.writerow([
            'Account Number',
            'Account Name',
            'Description',
            'Amount',
            'Classification',
            'Confidence Score',
            'Needs Review',
            'Rationale'
        ])
        
        # Data rows
        for item in classifications:
            writer.writerow([
                item.account_number,
                item.account_name,
                item.description or '',
                f"{item.amount:.2f}",
                item.classification.value,
                f"{item.confidence_score:.1f}",
                'Yes' if item.needs_review else 'No',
                item.rationale
            ])
        
        buffer.seek(0)
        return buffer.getvalue().encode('utf-8')
    
    @staticmethod
    def generate_json(analysis: AnalysisResult) -> bytes:
        """
        Generate machine-readable JSON export
        
        Args:
            analysis: AnalysisResult object
            
        Returns:
            JSON as bytes
        """
        import json
        
        # Convert to dict for JSON serialization
        data = analysis.model_dump()
        return json.dumps(data, indent=2).encode('utf-8')
