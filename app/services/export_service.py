"""Export service for CSV and JSON formats."""
import json
import csv
import io
from typing import List
from ..models import ClassificationResult, GLEntry


class ExportService:
    """Export classification results to CSV and JSON."""
    
    def export_to_csv(self, result: ClassificationResult) -> bytes:
        """
        Export classification results to CSV.
        
        Args:
            result: Classification results
            
        Returns:
            CSV content as bytes
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Date', 'Account Code', 'Account Name', 'Description', 'Amount',
            'Classification', 'Confidence Score', 'Needs Review', 'Rationale',
            'Override Classification'
        ])
        
        # Write data rows
        for entry in result.entries:
            final_class = entry.override_classification or entry.classification
            writer.writerow([
                entry.date,
                entry.account_code,
                entry.account_name,
                entry.description,
                f'{entry.amount:.2f}',
                final_class.value if final_class else '',
                f'{entry.confidence_score:.1f}' if entry.confidence_score else '',
                'Yes' if entry.needs_review else 'No',
                entry.rationale or '',
                entry.override_classification.value if entry.override_classification else ''
            ])
        
        # Write summary section
        writer.writerow([])
        writer.writerow(['SUMMARY'])
        writer.writerow(['Total Expenses', f'{result.total_amount:.2f}'])
        writer.writerow(['COGS', f'{result.cogs_total:.2f}'])
        writer.writerow(['Deductible Operating', f'{result.deductible_total:.2f}'])
        writer.writerow(['Non-Deductible', f'{result.non_deductible_total:.2f}'])
        writer.writerow(['Estimated Tax Impact', f'{result.estimated_tax_impact:.2f}'])
        writer.writerow(['Entries Needing Review', str(result.needs_review_count)])
        
        # Get CSV content
        csv_content = output.getvalue()
        output.close()
        
        return csv_content.encode('utf-8')
    
    def export_to_json(self, result: ClassificationResult) -> bytes:
        """
        Export classification results to JSON.
        
        Args:
            result: Classification results
            
        Returns:
            JSON content as bytes
        """
        # Convert to dictionary
        data = {
            'summary': result.summary,
            'entries': [
                {
                    'date': entry.date,
                    'account_code': entry.account_code,
                    'account_name': entry.account_name,
                    'description': entry.description,
                    'amount': entry.amount,
                    'classification': (entry.override_classification or entry.classification).value
                        if (entry.override_classification or entry.classification) else None,
                    'confidence_score': entry.confidence_score,
                    'needs_review': entry.needs_review,
                    'rationale': entry.rationale,
                    'override_classification': entry.override_classification.value
                        if entry.override_classification else None
                }
                for entry in result.entries
            ]
        }
        
        # Convert to JSON string with formatting
        json_str = json.dumps(data, indent=2)
        
        return json_str.encode('utf-8')
