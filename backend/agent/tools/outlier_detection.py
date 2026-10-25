import pandas as pd
import numpy as np
from typing import Dict, Any, List

def outlier_detection(dataset: pd.DataFrame, metadata: Dict[str, Any], 
                    columns: List[str] = None, method: str = 'iqr') -> Dict[str, Any]:
    """
    Detect outliers in numerical columns.
    Default method: IQR (Interquartile Range)
    """
    try:
        if dataset is None or len(dataset) == 0:
            return {'success': False, 'error': 'Dataset is empty or not loaded'}
        
        # Get numeric columns if not specified
        if columns is None:
            columns = metadata.get('numeric_columns', [])
        
        # Filter to valid numeric columns
        valid_columns = [col for col in columns if col in dataset.columns and 
                        pd.api.types.is_numeric_dtype(dataset[col])]
        
        if not valid_columns:
            return {'success': False, 'error': 'No numerical columns available for outlier detection'}
        
        results = {}
        total_outliers = 0
        
        for col in valid_columns:
            col_data = dataset[col].dropna()
            
            if len(col_data) < 4:
                results[col] = {
                    'column': col,
                    'outliers': [],
                    'count': 0,
                    'message': 'Insufficient data for outlier detection'
                }
                continue
            
            if method == 'iqr':
                outlier_result = _detect_outliers_iqr(col_data)
            elif method == 'zscore':
                outlier_result = _detect_outliers_zscore(col_data)
            else:
                return {'success': False, 'error': f'Unsupported outlier detection method: {method}'}
            
            outlier_result['column'] = col
            results[col] = outlier_result
            total_outliers += outlier_result['count']
        
        return {
            'success': True,
            'operation': 'outlier_detection',
            'method': method,
            'results': results,
            'total_outliers': total_outliers,
            'columns_analyzed': valid_columns
        }
        
    except Exception as e:
        return {'success': False, 'error': f'Outlier detection failed: {str(e)}'}


def _detect_outliers_iqr(series: pd.Series) -> Dict[str, Any]:
    """Detect outliers using IQR method"""
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = series[(series < lower_bound) | (series > upper_bound)]
    
    return {
        'method': 'iqr',
        'lower_bound': float(lower_bound),
        'upper_bound': float(upper_bound),
        'count': len(outliers),
        'outliers': outliers.tolist()[:50],  # Limit to first 50 outliers
        'percentage': float(len(outliers) / len(series) * 100)
    }


def _detect_outliers_zscore(series: pd.Series, threshold: float = 3.0) -> Dict[str, Any]:
    """Detect outliers using Z-score method"""
    mean = series.mean()
    std = series.std()
    
    if std == 0:
        return {
            'method': 'zscore',
            'count': 0,
            'outliers': [],
            'message': 'Standard deviation is zero, cannot use z-score method'
        }
    
    z_scores = np.abs((series - mean) / std)
    outliers = series[z_scores > threshold]
    
    return {
        'method': 'zscore',
        'threshold': threshold,
        'count': len(outliers),
        'outliers': outliers.tolist()[:50],
        'percentage': float(len(outliers) / len(series) * 100)
    }


def remove_outliers(dataset: pd.DataFrame, column: str, method: str = 'iqr') -> Dict[str, Any]:
    """Remove outliers from a specific column"""
    try:
        if column not in dataset.columns:
            return {'success': False, 'error': f'Column {column} not found'}
        
        if not pd.api.types.is_numeric_dtype(dataset[column]):
            return {'success': False, 'error': f'Column {column} is not numerical'}
        
        result_dataset = dataset.copy()
        original_count = len(result_dataset)
        
        if method == 'iqr':
            Q1 = result_dataset[column].quantile(0.25)
            Q3 = result_dataset[column].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            result_dataset = result_dataset[
                (result_dataset[column] >= lower_bound) & 
                (result_dataset[column] <= upper_bound)
            ]
        
        elif method == 'zscore':
            mean = result_dataset[column].mean()
            std = result_dataset[column].std()
            
            if std > 0:
                z_scores = np.abs((result_dataset[column] - mean) / std)
                result_dataset = result_dataset[z_scores <= 3.0]
        
        removed_count = original_count - len(result_dataset)
        
        return {
            'success': True,
            'operation': 'remove_outliers',
            'column': column,
            'method': method,
            'original_count': original_count,
            'final_count': len(result_dataset),
            'removed_count': removed_count,
            'dataset_shape': result_dataset.shape
        }
        
    except Exception as e:
        return {'success': False, 'error': f'Outlier removal failed: {str(e)}'}


def winsorize(dataset: pd.DataFrame, column: str, lower_percentile: float = 0.05, 
              upper_percentile: float = 0.95) -> Dict[str, Any]:
    """
    Winsorize data by replacing extreme values with percentiles.
    Less extreme than removing outliers.
    """
    try:
        if column not in dataset.columns:
            return {'success': False, 'error': f'Column {column} not found'}
        
        if not pd.api.types.is_numeric_dtype(dataset[column]):
            return {'success': False, 'error': f'Column {column} is not numerical'}
        
        result_dataset = dataset.copy()
        
        lower_limit = result_dataset[column].quantile(lower_percentile)
        upper_limit = result_dataset[column].quantile(upper_percentile)
        
        original_mean = result_dataset[column].mean()
        
        result_dataset[column] = result_dataset[column].clip(lower=lower_limit, upper=upper_limit)
        
        modified_count = (
            (dataset[column] < lower_limit) | (dataset[column] > upper_limit)
        ).sum()
        
        return {
            'success': True,
            'operation': 'winsorize',
            'column': column,
            'lower_limit': float(lower_limit),
            'upper_limit': float(upper_limit),
            'modified_count': int(modified_count),
            'original_mean': float(original_mean),
            'new_mean': float(result_dataset[column].mean())
        }
        
    except Exception as e:
        return {'success': False, 'error': f'Winsorization failed: {str(e)}'}