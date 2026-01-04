"""CSV parser for general ledger data."""
import pandas as pd
from typing import List
import io
from ..models import GLEntry


class GLParser:
    """Parse and normalize general ledger data from CSV."""
    
    # Common column name mappings
    COLUMN_MAPPINGS = {
        'date': ['date', 'transaction_date', 'trans_date', 'posting_date'],
        'account_code': ['account_code', 'account_number', 'account', 'acct_code', 'gl_account'],
        'account_name': ['account_name', 'account_description', 'account_desc', 'acct_name'],
        'description': ['description', 'memo', 'desc', 'transaction_description', 'trans_desc'],
        'amount': ['amount', 'debit', 'credit', 'total', 'net_amount'],
        'category': ['category', 'type', 'expense_type', 'class']
    }
    
    def __init__(self):
        pass
    
    def parse_csv(self, file_content: bytes) -> List[GLEntry]:
        """
        Parse CSV file content into list of GLEntry objects.
        
        Args:
            file_content: Raw bytes of CSV file
            
        Returns:
            List of parsed GLEntry objects
        """
        # Read CSV into DataFrame
        df = pd.read_csv(io.BytesIO(file_content))
        
        # Normalize column names
        df = self._normalize_columns(df)
        
        # Validate required columns
        self._validate_columns(df)
        
        # Clean and standardize data
        df = self._clean_data(df)
        
        # Convert to GLEntry objects
        entries = []
        for _, row in df.iterrows():
            entry = GLEntry(
                date=str(row['date']),
                account_code=str(row['account_code']),
                account_name=str(row['account_name']),
                description=str(row['description']),
                amount=float(row['amount']),
                category=str(row['category']) if pd.notna(row.get('category')) else None
            )
            entries.append(entry)
        
        return entries
    
    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column names to standard format."""
        # Convert all column names to lowercase for matching
        df.columns = df.columns.str.lower().str.strip()
        
        # Map columns to standard names
        column_mapping = {}
        for standard_name, variants in self.COLUMN_MAPPINGS.items():
            for col in df.columns:
                if col in variants:
                    column_mapping[col] = standard_name
                    break
        
        df = df.rename(columns=column_mapping)
        return df
    
    def _validate_columns(self, df: pd.DataFrame):
        """Validate that required columns are present."""
        required_columns = ['date', 'account_code', 'account_name', 'description', 'amount']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(
                f"Missing required columns: {', '.join(missing_columns)}. "
                f"Available columns: {', '.join(df.columns)}"
            )
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize data."""
        # Remove rows with null amounts
        df = df.dropna(subset=['amount'])
        
        # Convert amounts to float, handling currency symbols
        if df['amount'].dtype == 'object':
            df['amount'] = df['amount'].astype(str).str.replace('$', '').str.replace(',', '')
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        
        # Remove rows with invalid amounts
        df = df.dropna(subset=['amount'])
        
        # Take absolute value of amounts (expenses should be positive)
        df['amount'] = df['amount'].abs()
        
        # Fill missing values in other columns
        df['account_code'] = df['account_code'].fillna('UNKNOWN')
        df['account_name'] = df['account_name'].fillna('Unknown Account')
        df['description'] = df['description'].fillna('No description')
        
        return df
