import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from agent.tools.summary_statistics import summary_statistics, calculate_mean
from agent.tools.correlation import correlation_analysis, pairwise_correlation
from agent.tools.distribution import distribution_analysis
from agent.tools.outlier_detection import outlier_detection

class TestAnalysisTools(unittest.TestCase):
    """Test cases for Analysis Tools"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create sample dataset
        self.sample_data = pd.DataFrame({
            'Name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie'],
            'Age': [30, 28, 35, 32, 45],
            'Salary': [65000, 52000, 58000, 70000, 55000],
            'Experience': [5, 3, 7, 6, 15],
            'Department': ['IT', 'HR', 'Sales', 'IT', 'HR']
        })
        
        self.sample_metadata = {
            'rows': 5,
            'columns': 5,
            'numeric_columns': ['Age', 'Salary', 'Experience'],
            'categorical_columns': ['Name', 'Department']
        }
    
    def test_summary_statistics(self):
        """Test summary statistics calculation"""
        result = summary_statistics(self.sample_data, self.sample_metadata)
        
        self.assertTrue(result['success'])
        self.assertIn('results', result)
        self.assertIn('operation', result)
        self.assertEqual(result['operation'], 'summary_statistics')
    
    def test_summary_statistics_with_grouping(self):
        """Test summary statistics with grouping"""
        result = summary_statistics(
            self.sample_data, 
            self.sample_metadata,
            group_by='Department'
        )
        
        self.assertTrue(result['success'])
        self.assertTrue(result['grouped'])
    
    def test_calculate_mean(self):
        """Test mean calculation for specific column"""
        result = calculate_mean(self.sample_data, 'Salary')
        
        self.assertIn('operation', result)
        self.assertEqual(result['operation'], 'mean')
        self.assertIn('value', result)
        self.assertIsInstance(result['value'], (int, float))
    
    def test_correlation_analysis(self):
        """Test correlation analysis"""
        result = correlation_analysis(self.sample_data, self.sample_metadata)
        
        self.assertTrue(result['success'])
        self.assertIn('correlation_matrix', result)
        self.assertIn('correlations', result)
        self.assertIn('method', result)
        self.assertEqual(result['method'], 'pearson')
    
    def test_correlation_analysis_insufficient_columns(self):
        """Test correlation analysis with insufficient columns"""
        single_col_data = self.sample_data[['Salary']]
        single_col_metadata = {
            'numeric_columns': ['Salary']
        }
        
        result = correlation_analysis(single_col_data, single_col_metadata)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_pairwise_correlation(self):
        """Test pairwise correlation between two columns"""
        result = pairwise_correlation(self.sample_data, 'Age', 'Salary')
        
        self.assertTrue(result['success'])
        self.assertIn('correlation', result)
        self.assertIn('interpretation', result)
        self.assertIn('column_x', result)
        self.assertIn('column_y', result)
    
    def test_distribution_analysis(self):
        """Test distribution analysis"""
        result = distribution_analysis(self.sample_data, self.sample_metadata)
        
        self.assertTrue(result['success'])
        self.assertIn('results', result)
        self.assertIn('columns_analyzed', result)
    
    def test_distribution_analysis_statistics(self):
        """Test that distribution analysis returns proper statistics"""
        result = distribution_analysis(self.sample_data, self.sample_metadata)
        
        for col_result in result['results'].values():
            self.assertIn('mean', col_result)
            self.assertIn('median', col_result)
            self.assertIn('std', col_result)
            self.assertIn('skewness', col_result)
    
    def test_outlier_detection_iqr(self):
        """Test outlier detection using IQR method"""
        # Add some outliers
        data_with_outliers = self.sample_data.copy()
        data_with_outliers.loc[len(data_with_outliers)] = ['Outlier', 100, 200000, 50, 'IT']
        
        metadata_with_outliers = {
            'numeric_columns': ['Age', 'Salary', 'Experience']
        }
        
        result = outlier_detection(data_with_outliers, metadata_with_outliers, method='iqr')
        
        self.assertTrue(result['success'])
        self.assertIn('results', result)
        self.assertIn('total_outliers', result)
        self.assertEqual(result['method'], 'iqr')
    
    def test_outlier_detection_zscore(self):
        """Test outlier detection using Z-score method"""
        result = outlier_detection(self.sample_data, self.sample_metadata, method='zscore')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['method'], 'zscore')
    
    def test_outlier_detection_bounds(self):
        """Test that outlier detection returns proper bounds"""
        result = outlier_detection(self.sample_data, self.sample_metadata)
        
        for col_result in result['results'].values():
            if col_result['count'] > 0:
                self.assertIn('lower_bound', col_result)
                self.assertIn('upper_bound', col_result)
    
    def test_empty_dataset_handling(self):
        """Test tools handle empty datasets properly"""
        empty_data = pd.DataFrame()
        empty_metadata = {'numeric_columns': []}
        
        result = summary_statistics(empty_data, empty_metadata)
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_missing_column_handling(self):
        """Test tools handle missing columns properly"""
        result = calculate_mean(self.sample_data, 'NonExistentColumn')
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)

if __name__ == '__main__':
    unittest.main()