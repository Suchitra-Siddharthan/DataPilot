import pandas as pd
import numpy as np
from typing import Dict, Any, List
from scipy import stats

def distribution_analysis(dataset: pd.DataFrame, metadata: Dict[str, Any], 
                        columns: List[str] = None) -> Dict[str, Any]:
    """
    Analyze distribution of numerical columns.
    Includes histograms, descriptive statistics, and skewness.
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
            return {'success': False, 'error': 'No numerical columns available for distribution analysis'}
        
        results = {}
        
        for col in valid_columns:
            col_data = dataset[col].dropna()
            
            if len(col_data) == 0:
                continue
            
            # Calculate distribution statistics
            dist_stats = {
                'column': col,
                'count': len(col_data),
                'mean': float(col_data.mean()),
                'median': float(col_data.median()),
                'std': float(col_data.std()),
                'min': float(col_data.min()),
                'max': float(col_data.max()),
                'q25': float(col_data.quantile(0.25)),
                'q75': float(col_data.quantile(0.75)),
                'iqr': float(col_data.quantile(0.75) - col_data.quantile(0.25)),
                'skewness': float(stats.skew(col_data)) if len(col_data) > 3 else 0.0,
                'kurtosis': float(stats.kurtosis(col_data)) if len(col_data) > 3 else 0.0,
                'range': float(col_data.max() - col_data.min())
            }
            
            # Interpret skewness
            skewness = dist_stats['skewness']
            if skewness > 1:
                skew_interpretation = "highly right-skewed"
            elif skewness > 0.5:
                skew_interpretation = "moderately right-skewed"
            elif skewness < -1:
                skew_interpretation = "highly left-skewed"
            elif skewness < -0.5:
                skew_interpretation = "moderately left-skewed"
            else:
                skew_interpretation = "approximately symmetric"
            
            dist_stats['skewness_interpretation'] = skew_interpretation
            
            results[col] = dist_stats
        
        return {
            'success': True,
            'operation': 'distribution_analysis',
            'results': results,
            'columns_analyzed': valid_columns
        }
        
    except Exception as e:
        return {'success': False, 'error': f'Distribution analysis failed: {str(e)}'}


def histogram_data(dataset: pd.DataFrame, column: str, bins: int = 10) -> Dict[str, Any]:
    """Generate histogram data for a column"""
    try:
        if column not in dataset.columns:
            return {'success': False, 'error': f'Column {column} not found'}
        
        if not pd.api.types.is_numeric_dtype(dataset[column]):
            return {'success': False, 'error': f'Column {column} is not numerical'}
        
        col_data = dataset[column].dropna()
        
        if len(col_data) == 0:
            return {'success': False, 'error': f'Column {column} has no valid data'}
        
        # Calculate histogram
        hist, bin_edges = np.histogram(col_data, bins=bins)
        
        # Create bin ranges
        bin_ranges = []
        for i in range(len(bin_edges) - 1):
            bin_ranges.append({
                'range': f"{bin_edges[i]:.2f}-{bin_edges[i+1]:.2f}",
                'count': int(hist[i]),
                'frequency': float(hist[i] / len(col_data))
            })
        
        return {
            'operation': 'histogram',
            'column': column,
            'bins': bin_ranges,
            'total_count': len(col_data),
            'bin_count': bins
        }
        
    except Exception as e:
        return {'success': False, 'error': f'Histogram generation failed: {str(e)}'}


def percentiles(dataset: pd.DataFrame, column: str, percentiles: List[float] = None) -> Dict[str, Any]:
    """Calculate percentiles for a column"""
    try:
        if column not in dataset.columns:
            return {'success': False, 'error': f'Column {column} not found'}
        
        if percentiles is None:
            percentiles = [5, 10, 25, 50, 75, 90, 95]
        
        col_data = dataset[column].dropna()
        
        if len(col_data) == 0:
            return {'success': False, 'error': f'Column {column} has no valid data'}
        
        percentile_values = {
            f'p{p}': float(col_data.quantile(p/100)) 
            for p in percentiles
        }
        
        return {
            'operation': 'percentiles',
            'column': column,
            'percentiles': percentile_values
        }
        
    except Exception as e:
        return {'success': False, 'error': f'Percentile calculation failed: {str(e)}'}