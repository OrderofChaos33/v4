"""PDF report generator using ReportLab."""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime
from typing import List
import io

from ..models import ClassificationResult, ReportData, GLEntry


class ReportGenerator:
    """Generate audit-ready PDF reports for 280E analysis."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Set up custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='CenterHeading',
            parent=self.styles['Heading1'],
            alignment=TA_CENTER
        ))
        self.styles.add(ParagraphStyle(
            name='RightAlign',
            parent=self.styles['Normal'],
            alignment=TA_RIGHT
        ))
        self.styles.add(ParagraphStyle(
            name='Disclaimer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey
        ))
    
    def generate_pdf(
        self,
        result: ClassificationResult,
        report_data: ReportData,
        output_path: str = None
    ) -> bytes:
        """
        Generate PDF report.
        
        Args:
            result: Classification results
            report_data: Report metadata
            output_path: Optional file path to save PDF
            
        Returns:
            PDF content as bytes
        """
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Title page
        story.extend(self._create_title_page(report_data))
        story.append(PageBreak())
        
        # Executive summary
        story.extend(self._create_executive_summary(result, report_data))
        story.append(Spacer(1, 0.3*inch))
        
        # Financial impact summary
        story.extend(self._create_financial_summary(result))
        story.append(Spacer(1, 0.3*inch))
        
        # Risk and confidence analysis
        story.extend(self._create_risk_analysis(result))
        story.append(PageBreak())
        
        # Detailed classification table
        story.extend(self._create_detailed_table(result.entries))
        
        # Disclaimer
        story.append(Spacer(1, 0.3*inch))
        story.extend(self._create_disclaimer())
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        # Optionally save to file
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)
        
        return pdf_bytes
    
    def _create_title_page(self, report_data: ReportData) -> List:
        """Create title page."""
        elements = []
        
        elements.append(Spacer(1, 2*inch))
        elements.append(Paragraph(
            "IRS 280E Expense Classification Analysis",
            self.styles['CenterHeading']
        ))
        elements.append(Spacer(1, 0.5*inch))
        
        elements.append(Paragraph(
            f"<b>Company:</b> {report_data.company_name}",
            self.styles['Normal']
        ))
        elements.append(Paragraph(
            f"<b>Tax Year:</b> {report_data.tax_year}",
            self.styles['Normal']
        ))
        elements.append(Paragraph(
            f"<b>State:</b> {report_data.state}",
            self.styles['Normal']
        ))
        elements.append(Paragraph(
            f"<b>Entity Structure:</b> {report_data.entity_structure}",
            self.styles['Normal']
        ))
        elements.append(Paragraph(
            f"<b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            self.styles['Normal']
        ))
        
        return elements
    
    def _create_executive_summary(self, result: ClassificationResult, report_data: ReportData) -> List:
        """Create executive summary section."""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.styles['Heading1']))
        elements.append(Spacer(1, 0.2*inch))
        
        summary_text = f"""
        This report provides an automated classification of general ledger expenses 
        according to IRS Code Section 280E, which disallows deductions for businesses 
        trafficking in Schedule I or II controlled substances, except for Cost of Goods Sold (COGS).
        <br/><br/>
        <b>Total Expenses Analyzed:</b> ${result.total_amount:,.2f}<br/>
        <b>COGS (Deductible):</b> ${result.cogs_total:,.2f}<br/>
        <b>Other Deductible Expenses:</b> ${result.deductible_total:,.2f}<br/>
        <b>Non-Deductible Expenses:</b> ${result.non_deductible_total:,.2f}<br/>
        <b>Items Flagged for Review:</b> {result.needs_review_count}<br/>
        <br/>
        <b>Estimated Tax Impact:</b> ${result.estimated_tax_impact:,.2f} in potential tax savings
        at a {report_data.federal_tax_rate:.1%} federal tax rate.
        """
        
        elements.append(Paragraph(summary_text, self.styles['Normal']))
        
        return elements
    
    def _create_financial_summary(self, result: ClassificationResult) -> List:
        """Create financial summary table."""
        elements = []
        
        elements.append(Paragraph("Financial Summary", self.styles['Heading2']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Create summary table
        data = [
            ['Category', 'Amount', 'Percentage'],
            ['COGS', f'${result.cogs_total:,.2f}', 
             f'{(result.cogs_total/result.total_amount*100):.1f}%'],
            ['Deductible Operating Expenses', f'${result.deductible_total:,.2f}',
             f'{(result.deductible_total/result.total_amount*100):.1f}%'],
            ['Non-Deductible Expenses', f'${result.non_deductible_total:,.2f}',
             f'{(result.non_deductible_total/result.total_amount*100):.1f}%'],
            ['', '', ''],
            ['Total Expenses', f'${result.total_amount:,.2f}', '100.0%'],
        ]
        
        table = Table(data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('GRID', (0, 0), (-1, -2), 1, colors.black),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(table)
        
        return elements
    
    def _create_risk_analysis(self, result: ClassificationResult) -> List:
        """Create risk and confidence analysis."""
        elements = []
        
        elements.append(Paragraph("Risk & Confidence Analysis", self.styles['Heading2']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Calculate confidence statistics
        high_confidence = sum(1 for e in result.entries if e.confidence_score >= 80)
        medium_confidence = sum(1 for e in result.entries if 60 <= e.confidence_score < 80)
        low_confidence = sum(1 for e in result.entries if e.confidence_score < 60)
        
        risk_text = f"""
        <b>Classification Confidence:</b><br/>
        • High confidence (≥80%): {high_confidence} entries<br/>
        • Medium confidence (60-79%): {medium_confidence} entries<br/>
        • Low confidence (<60%): {low_confidence} entries<br/>
        <br/>
        <b>Review Recommendations:</b><br/>
        {result.needs_review_count} entries have been flagged for CPA review due to 
        lower confidence scores or ambiguous classification.
        <br/><br/>
        <b>Audit Preparedness:</b><br/>
        Each classification includes detailed rationale for IRS audit support. 
        All entries flagged for review should be examined by a qualified tax professional 
        before filing.
        """
        
        elements.append(Paragraph(risk_text, self.styles['Normal']))
        
        return elements
    
    def _create_detailed_table(self, entries: List[GLEntry]) -> List:
        """Create detailed classification table."""
        elements = []
        
        elements.append(Paragraph("Detailed Classification", self.styles['Heading2']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Prepare table data
        data = [['Date', 'Account', 'Description', 'Amount', 'Classification', 'Conf.', 'Review']]
        
        for entry in entries[:50]:  # Limit to first 50 for PDF size
            final_class = entry.override_classification or entry.classification
            data.append([
                entry.date[:10],
                entry.account_code[:15],
                entry.description[:30],
                f'${entry.amount:,.0f}',
                final_class.value if final_class else 'N/A',
                f'{entry.confidence_score:.0f}%' if entry.confidence_score else 'N/A',
                '⚠' if entry.needs_review else '✓'
            ])
        
        if len(entries) > 50:
            data.append(['...', f'{len(entries) - 50} more entries', '', '', '', '', ''])
        
        # Create table
        table = Table(data, colWidths=[0.7*inch, 0.8*inch, 2*inch, 0.8*inch, 1.2*inch, 0.5*inch, 0.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(table)
        
        return elements
    
    def _create_disclaimer(self) -> List:
        """Create disclaimer section."""
        elements = []
        
        disclaimer_text = """
        <b>IMPORTANT DISCLAIMER:</b> This report is provided for informational and 
        decision-support purposes only and does not constitute tax advice, legal advice, 
        or accounting services. The classifications and analysis contained herein are based 
        on automated algorithms and should be reviewed by a qualified tax professional 
        before making any tax-related decisions. The estimated tax impact is illustrative 
        only and actual tax liability may vary based on individual circumstances, changes 
        in tax law, and IRS interpretation. Users are responsible for consulting with 
        their own tax advisors and CPAs to ensure compliance with all applicable tax laws 
        and regulations. No warranty is made regarding the accuracy or completeness of 
        this analysis.
        """
        
        elements.append(Paragraph(disclaimer_text, self.styles['Disclaimer']))
        
        return elements
