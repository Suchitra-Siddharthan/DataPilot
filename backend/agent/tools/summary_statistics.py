import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

def summary_statistics(dataset: pd.DataFrame, metadata: Dict[str, Any], 
                      columns: List[str] = None, group_by: str = None) -> Dict[str, Any]:
    """
    Calculate summary statistics for numerical columns.
    
    Operations: mean, median, min, max, std, count, describe
    """
    try:
        if dataset is None or len(dataset) == 0:
            return {'success': False, 'error': 'Dataset is empty or not loaded'}
        
        # Preserve the caller-supplied column selection exactly.
        if columns is None:
            columns = metadata.get('numeric_columns', [])
        else:
            columns = list(columns)
        
        if not columns:
            return {'success': False, 'error': 'No numerical columns available for analysis'}
        
        # Validate columns exist, but do not expand back to all numeric columns.
        valid_columns = [col for col in columns if col in dataset.columns]
        if not valid_columns:
            return {'success': False, 'error': 'No valid columns found in dataset'}
        
        results = {}
        
        if group_by and group_by in dataset.columns:
            # Grouped statistics
            grouped = dataset.groupby(group_by)
            
            for col in valid_columns:
                if pd.api.types.is_numeric_dtype(dataset[col]):
                    group_stats = grouped[col].agg(['mean', 'median', 'min', 'max', 'std', 'count'])
                    results[col] = {
                        'operation': 'grouped_summary',
                        'group_by': group_by,
                        'statistics': group_stats.to_dict(),
                        'type': 'grouped'
                    }
        else:
            # Overall statistics
            for col in valid_columns:
                if pd.api.types.is_numeric_dtype(dataset[col]):
                    col_data = dataset[col].dropna()
                    
                    results[col] = {
                        'operation': 'summary_statistics',
                        'column': col,
                        'mean': float(col_data.mean()),
                        'median': float(col_data.median()),
                        'min': float(col_data.min()),
                        'max': float(col_data.max()),
                        'std': float(col_data.std()) if len(col_data) > 1 else 0.0,
                        'count': int(col_data.count()),
                        'type': 'single'
                    }
        
        return {
            'success': True,
            'results': results,
            'operation': 'summary_statistics',
            'grouped': group_by is not None
        }
        
    except Exception as e:
        return {'success': False, 'error': f'Summary statistics calculation failed: {str(e)}'}


def calculate_mean(dataset: pd.DataFrame, column: str) -> Dict[str, Any]:
    """Calculate mean of a specific column"""
    try:
        if column not in dataset.columns:
            return {'success': False, 'error': f'Column {column} not found'}
        
        mean_value = dataset[column].mean()
        return {
            'operation': 'mean',
            'column': column,
            'value': float(mean_value)
        }
    except Exception as e:
        return {'success': False, 'error': f'Mean calculation failed: {str(e)}'}


def calculate_median(dataset: pd.DataFrame, column: str) -> Dict[str, Any]:
    """Calculate median of a specific column"""
    try:
        if column not in dataset.columns:
            return {'success': False, 'error': f'Column {column} not found'}
        
        median_value = dataset[column].median()
        return {
            'operation': 'median',
            'column': column,
            'value': float(median_value)
        }
    except Exception as e:
        return {'success': False, 'error': f'Median calculation failed: {str(e)}'}


def calculate_describe(dataset: pd.DataFrame, columns: List[str] = None) -> Dict[str, Any]:
    """Generate descriptive statistics using pandas describe()"""
    try:
        if columns is None:
            columns = dataset.select_dtypes(include=[np.number]).columns.tolist()
        
        valid_columns = [col for col in columns if col in dataset.columns]
        if not valid_columns:
            return {'success': False, 'error': 'No valid numeric columns for describe'}
        
        description = dataset[valid_columns].describe()
        
        return {
            'operation': 'describe',
            'columns': valid_columns,
            'statistics': description.to_dict()
        }
    except Exception as e:
        return {'success': False, 'error': f'Describe operation failed: {str(e)}'}