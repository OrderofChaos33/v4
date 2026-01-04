"""GL Parser Service - CSV ingestion and normalization"""

import csv
import io
from typing import List, Dict, Any
import pandas as pd
from ..models.gl_entry import GLEntry


class GLParserService:
    """Service for parsing and normalizing GL data from CSV"""
    
    # Expected column mappings (flexible)
    COLUMN_MAPPINGS = {
        'account_number': ['account_number', 'account', 'acct_num', 'acct', 'account #'],
        'account_name': ['account_name', 'name', 'description', 'acct_name', 'account_desc'],
        'description': ['description', 'memo', 'desc', 'transaction_description', 'detail'],
        'amount': ['amount', 'debit', 'credit', 'total', 'value'],
        'date': ['date', 'transaction_date', 'trans_date', 'posting_date'],
        'vendor': ['vendor', 'payee', 'supplier', 'vendor_name']
    }
    
    @staticmethod
    def _normalize_column_name(col: str) -> str:
        """Normalize column name to lowercase and remove special chars"""
        return col.lower().strip().replace(' ', '_').replace('-', '_')
    
    @staticmethod
    def _find_column_mapping(headers: List[str]) -> Dict[str, str]:
        """Map CSV columns to our standard fields"""
        normalized_headers = {GLParserService._normalize_column_name(h): h for h in headers}
        mapping = {}
        
        for field, possible_names in GLParserService.COLUMN_MAPPINGS.items():
            for possible_name in possible_names:
                normalized_possible = GLParserService._normalize_column_name(possible_name)
                if normalized_possible in normalized_headers:
                    mapping[field] = normalized_headers[normalized_possible]
                    break
        
        return mapping
    
    @staticmethod
    def parse_csv(file_content: bytes) -> List[GLEntry]:
        """
        Parse CSV file content and return list of GLEntry objects
        
        Args:
            file_content: Raw CSV file bytes
            
        Returns:
            List of GLEntry objects
            
        Raises:
            ValueError: If required fields are missing or data is invalid
        """
        try:
            # Try to read as CSV
            df = pd.read_csv(io.BytesIO(file_content))
        except Exception as e:
            raise ValueError(f"Failed to parse CSV: {str(e)}")
        
        if df.empty:
            raise ValueError("CSV file is empty")
        
        # Map columns
        column_mapping = GLParserService._find_column_mapping(df.columns.tolist())
        
        # Check required fields
        required_fields = ['account_number', 'account_name', 'amount']
        missing_fields = [f for f in required_fields if f not in column_mapping]
        if missing_fields:
            raise ValueError(
                f"Missing required columns: {missing_fields}. "
                f"Found columns: {df.columns.tolist()}"
            )
        
        # Parse entries
        entries = []
        for idx, row in df.iterrows():
            try:
                entry_data = {}
                for field, csv_col in column_mapping.items():
                    value = row[csv_col]
                    # Handle NaN values
                    if pd.isna(value):
                        entry_data[field] = None if field not in required_fields else ""
                    else:
                        entry_data[field] = value
                
                # Ensure account_number is string
                if entry_data.get('account_number') is not None:
                    entry_data['account_number'] = str(entry_data['account_number'])
                
                # Ensure amount is numeric
                if entry_data.get('amount') is not None:
                    entry_data['amount'] = float(entry_data['amount'])
                else:
                    continue  # Skip entries without amount
                
                # Convert date to string if present
                if entry_data.get('date') is not None:
                    entry_data['date'] = str(entry_data['date'])
                
                # Create GLEntry
                entry = GLEntry(**entry_data)
                entries.append(entry)
                
            except Exception as e:
                # Log but continue - we'll be lenient with malformed rows
                print(f"Warning: Skipping row {idx}: {str(e)}")
                continue
        
        if not entries:
            raise ValueError("No valid entries found in CSV")
        
        return entries
    
    @staticmethod
    def validate_gl_data(entries: List[GLEntry]) -> Dict[str, Any]:
        """
        Validate GL data and return summary statistics
        
        Args:
            entries: List of GLEntry objects
            
        Returns:
            Dictionary with validation results and stats
        """
        stats = {
            "total_entries": len(entries),
            "total_amount": sum(e.amount for e in entries),
            "unique_accounts": len(set(e.account_number for e in entries)),
            "date_range": None,
            "has_descriptions": sum(1 for e in entries if e.description) / len(entries) * 100,
            "has_vendors": sum(1 for e in entries if e.vendor) / len(entries) * 100,
        }
        
        # Calculate date range if dates available
        dates_with_values = [e.date for e in entries if e.date]
        if dates_with_values:
            stats["date_range"] = {
                "min": min(dates_with_values),
                "max": max(dates_with_values)
            }
        
        return stats
