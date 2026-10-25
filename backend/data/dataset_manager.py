import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import os
import uuid

class DatasetManager:
    """Manages dataset loading, inspection, and metadata"""
    
    def __init__(self):
        self.current_dataset = None
        self.dataset_metadata = None
        self.dataset_id = None
        # Use absolute path for upload directory
        self.upload_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
        
        # Create upload directory if it doesn't exist
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)
    
    def load_dataset(self, file_path: str) -> Dict[str, Any]:
        """Load CSV dataset and extract metadata"""
        try:
            # Load CSV
            df = pd.read_csv(file_path)
            
            # Store dataset
            self.current_dataset = df
            self.dataset_id = str(uuid.uuid4())
            
            # Extract metadata and store a JSON-serializable copy
            self.dataset_metadata = self._make_json_serializable(self._extract_metadata(df))
            
            serializable_metadata = self.dataset_metadata
            
            return {
                'success': True,
                'dataset_id': self.dataset_id,
                'metadata': serializable_metadata
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to load dataset: {str(e)}"
            }
    
    def _make_json_serializable(self, obj):
        """Convert numpy types to Python native types for JSON serialization"""
        if isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            val = float(obj)
            if np.isnan(val) or np.isinf(val):
                return None
            return val
        elif isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
            return None
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj
    
    def _extract_metadata(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract comprehensive metadata from dataset"""
        metadata = {
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': list(df.columns),
            'numeric_columns': [],
            'categorical_columns': [],
            'datetime_columns': [],
            'missing_values': {},
            'duplicate_rows': df.duplicated().sum(),
            'column_info': {}
        }
        
        # Analyze each column
        for col in df.columns:
            col_info = {
                'type': str(df[col].dtype),
                'missing_count': df[col].isnull().sum(),
                'unique_count': df[col].nunique(),
                'sample_values': df[col].dropna().head(3).tolist()
            }
            
            # Categorize column type
            if pd.api.types.is_numeric_dtype(df[col]):
                metadata['numeric_columns'].append(col)
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                metadata['datetime_columns'].append(col)
            else:
                metadata['categorical_columns'].append(col)
            
            metadata['missing_values'][col] = int(df[col].isnull().sum())
            metadata['column_info'][col] = col_info
        
        # Convert numpy types to Python native types for JSON serialization
        metadata['duplicate_rows'] = int(metadata['duplicate_rows'])
        for col in metadata['missing_values']:
            metadata['missing_values'][col] = int(metadata['missing_values'][col])
        
        return metadata
    
    def get_dataset(self) -> Optional[pd.DataFrame]:
        """Get current dataset"""
        return self.current_dataset
    
    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """Get current dataset metadata"""
        return self.dataset_metadata
    
    def get_preview(self, n_rows: int = 10) -> Dict[str, Any]:
        """Get preview of dataset"""
        if self.current_dataset is None:
            return {'success': False, 'error': 'No dataset loaded'}
        
        try:
            preview_df = self.current_dataset.head(n_rows)
            records = preview_df.where(pd.notnull(preview_df), None).to_dict(orient='records')
            return {
                'success': True,
                'preview': self._make_json_serializable(records),
                'rows_shown': len(preview_df)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to generate preview: {str(e)}"
            }
    
    def clear_dataset(self):
        """Clear current dataset"""
        self.current_dataset = None
        self.dataset_metadata = None
        self.dataset_id = None
    
    def validate_column_exists(self, column_name: str) -> bool:
        """Check if column exists in dataset"""
        if self.current_dataset is None:
            return False
        return column_name in self.current_dataset.columns
    
    def get_numeric_columns(self) -> List[str]:
        """Get list of numeric columns"""
        if self.dataset_metadata is None:
            return []
        return self.dataset_metadata.get('numeric_columns', [])
    
    def get_categorical_columns(self) -> List[str]:
        """Get list of categorical columns"""
        if self.dataset_metadata is None:
            return []
        return self.dataset_metadata.get('categorical_columns', [])
    
    def has_sufficient_data(self, min_rows: int = 2) -> bool:
        """Check if dataset has sufficient rows for analysis"""
        if self.current_dataset is None:
            return False
        return len(self.current_dataset) >= min_rows


# Global instance
dataset_manager = DatasetManager()