import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from scipy import stats

def correlation_analysis(dataset: pd.DataFrame, metadata: Dict[str, Any], 
                       columns: List[str] = None) -> Dict[str, Any]:
    """
    Perform correlation analysis between numerical columns.
    Uses Pearson correlation by default.
    """
    try:
        if dataset is None or len(dataset) == 0:
            return {'success': False, 'error': 'Dataset is empty or not loaded'}
        
        # Get numeric columns if not specified
        if columns is None:
            columns = metadata.get('numeric_columns', [])
        
        # Filter to only numeric columns that exist
        valid_columns = [col for col in columns if col in dataset.columns and 
                        pd.api.types.is_numeric_dtype(dataset[col])]

        # Exclude true identifier-like columns only by strong name patterns or by
        # near-one-to-one values. Do not drop legitimate analytical numeric fields
        # just because they are mostly unique (e.g., salary, performance score, age).
        id_keywords = ['id', 'employee_id', 'customer_id', 'order_id', 'user_id', 'uid']
        filtered_columns = []
        total_rows = len(dataset)
        for col in valid_columns:
            col_lower = col.lower()
            # Exclude if the column name is clearly an ID field
            if any(k == col_lower or k in col_lower for k in id_keywords):
                continue

            # Exclude only if the column is effectively a unique record identifier,
            # not a meaningful metric. This catches true IDs but preserves metrics
            # that happen to be unique across a dataset.
            try:
                unique_count = int(dataset[col].nunique(dropna=True))
                non_null_count = int(dataset[col].notna().sum())
            except Exception:
                unique_count = 0
                non_null_count = 0

            if total_rows > 0 and non_null_count > 0:
                uniqueness_ratio = unique_count / non_null_count
                if uniqueness_ratio >= 0.99 and unique_count >= max(0.9 * total_rows, 2):
                    # This is almost certainly a row ID-like column, not an analytic metric.
                    if col_lower.endswith('_id') or 'id' in col_lower:
                        continue
                    # A numeric column with every row unique but no clear ID naming is
                    # still potentially a valid analytic variable (e.g., salary), so do
                    # not discard it unless the name strongly indicates an identifier.
                    if any(k in col_lower for k in ['employee', 'customer', 'user', 'order', 'account']):
                        continue
            filtered_columns.append(col)
        valid_columns = filtered_columns
        
        if len(valid_columns) < 2:
            return {'success': False, 'error': f'Correlation analysis requires at least 2 numerical columns, found {len(valid_columns)}'}
        
        # Calculate correlation matrix
        correlation_matrix = dataset[valid_columns].corr()
        
        # Find strongest correlations
        correlations = []
        for i, col1 in enumerate(valid_columns):
            for j, col2 in enumerate(valid_columns):
                if i < j:  # Avoid duplicates and self-correlation
                    corr_value = correlation_matrix.loc[col1, col2]
                    if not np.isnan(corr_value):
                        correlations.append({
                            'column_x': col1,
                            'column_y': col2,
                            'correlation': float(corr_value),
                            'interpretation': _interpret_correlation(corr_value)
                        })
        
        # Sort by absolute correlation value
        correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
        
        return {
            'success': True,
            'operation': 'correlation_analysis',
            'correlation_matrix': correlation_matrix.to_dict(),
            'correlations': correlations,
            'method': 'pearson',
            'columns_analyzed': valid_columns
        }
        
    except Exception as e:
        return {'success': False, 'error': f'Correlation analysis failed: {str(e)}'}


def pairwise_correlation(dataset: pd.DataFrame, column_x: str, column_y: str) -> Dict[str, Any]:
    """Calculate correlation between two specific columns"""
    try:
        if column_x not in dataset.columns or column_y not in dataset.columns:
            return {'success': False, 'error': 'One or both columns not found in dataset'}
        
        if not (pd.api.types.is_numeric_dtype(dataset[column_x]) and 
                pd.api.types.is_numeric_dtype(dataset[column_y])):
            return {'success': False, 'error': 'Both columns must be numerical for correlation analysis'}
        
        # Remove NaN values
        valid_data = dataset[[column_x, column_y]].dropna()
        
        if len(valid_data) < 2:
            return {'success': False, 'error': 'Insufficient data points for correlation calculation'}
        
        # Calculate Pearson correlation
        correlation, p_value = stats.pearsonr(valid_data[column_x], valid_data[column_y])
        
        return {
            'success': True,
            'operation': 'pairwise_correlation',
            'column_x': column_x,
            'column_y': column_y,
            'correlation': float(correlation),
            'p_value': float(p_value),
            'interpretation': _interpret_correlation(correlation),
            'significant': p_value < 0.05
        }
        
    except Exception as e:
        return {'success': False, 'error': f'Pairwise correlation failed: {str(e)}'}


def _interpret_correlation(correlation: float) -> str:
    """Interpret correlation strength"""
    abs_corr = abs(correlation)
    
    if abs_corr >= 0.7:
        strength = "strong"
    elif abs_corr >= 0.5:
        strength = "moderate"
    elif abs_corr >= 0.3:
        strength = "weak"
    else:
        strength = "very weak"
    
    direction = "positive" if correlation > 0 else "negative"
    
    return f"{strength} {direction} relationship"