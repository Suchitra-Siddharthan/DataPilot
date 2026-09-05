import unittest
import pandas as pd
import sys
import os
import tempfile

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from data.dataset_manager import DatasetManager

class TestDatasetManager(unittest.TestCase):
    """Test cases for Dataset Manager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = DatasetManager()
        
        # Create a sample CSV file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        sample_data = """Name,Age,Department,Salary,Experience
John,30,IT,65000,5
Jane,28,HR,52000,3
Bob,35,Sales,58000,7
Alice,32,IT,70000,6
Charlie,45,HR,55000,15"""
        self.temp_file.write(sample_data)
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_load_dataset(self):
        """Test loading a CSV dataset"""
        result = self.manager.load_dataset(self.temp_file.name)
        
        self.assertTrue(result['success'])
        self.assertIn('dataset_id', result)
        self.assertIn('metadata', result)
        self.assertIsNotNone(self.manager.current_dataset)
    
    def test_metadata_extraction(self):
        """Test metadata extraction from dataset"""
        self.manager.load_dataset(self.temp_file.name)
        metadata = self.manager.get_metadata()
        
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata['rows'], 5)
        self.assertEqual(metadata['columns'], 5)
        self.assertIn('column_names', metadata)
        self.assertIn('numeric_columns', metadata)
        self.assertIn('categorical_columns', metadata)
    
    def test_numeric_column_detection(self):
        """Test detection of numeric columns"""
        self.manager.load_dataset(self.temp_file.name)
        numeric_cols = self.manager.get_numeric_columns()
        
        self.assertIsInstance(numeric_cols, list)
        self.assertIn('Age', numeric_cols)
        self.assertIn('Salary', numeric_cols)
        self.assertIn('Experience', numeric_cols)
    
    def test_categorical_column_detection(self):
        """Test detection of categorical columns"""
        self.manager.load_dataset(self.temp_file.name)
        categorical_cols = self.manager.get_categorical_columns()
        
        self.assertIsInstance(categorical_cols, list)
        self.assertIn('Department', categorical_cols)
        self.assertIn('Name', categorical_cols)
    
    def test_missing_values_detection(self):
        """Test missing values detection"""
        self.manager.load_dataset(self.temp_file.name)
        metadata = self.manager.get_metadata()
        
        self.assertIn('missing_values', metadata)
        # Our sample data has no missing values
        total_missing = sum(metadata['missing_values'].values())
        self.assertEqual(total_missing, 0)
    
    def test_duplicate_rows_detection(self):
        """Test duplicate rows detection"""
        self.manager.load_dataset(self.temp_file.name)
        metadata = self.manager.get_metadata()
        
        self.assertIn('duplicate_rows', metadata)
        self.assertEqual(metadata['duplicate_rows'], 0)
    
    def test_dataset_preview(self):
        """Test dataset preview generation"""
        self.manager.load_dataset(self.temp_file.name)
        preview = self.manager.get_preview(3)
        
        self.assertTrue(preview['success'])
        self.assertEqual(preview['rows_shown'], 3)
        self.assertIn('preview', preview)
    
    def test_clear_dataset(self):
        """Test clearing the dataset"""
        self.manager.load_dataset(self.temp_file.name)
        self.assertIsNotNone(self.manager.current_dataset)
        
        self.manager.clear_dataset()
        self.assertIsNone(self.manager.current_dataset)
        self.assertIsNone(self.manager.get_metadata())
    
    def test_column_validation(self):
        """Test column existence validation"""
        self.manager.load_dataset(self.temp_file.name)
        
        self.assertTrue(self.manager.validate_column_exists('Name'))
        self.assertTrue(self.manager.validate_column_exists('Salary'))
        self.assertFalse(self.manager.validate_column_exists('NonExistent'))
    
    def test_sufficient_data_check(self):
        """Test sufficient data validation"""
        self.manager.load_dataset(self.temp_file.name)
        
        self.assertTrue(self.manager.has_sufficient_data(2))
        self.assertTrue(self.manager.has_sufficient_data(5))
        self.assertFalse(self.manager.has_sufficient_data(10))
    
    def test_load_invalid_file(self):
        """Test loading an invalid file"""
        result = self.manager.load_dataset('nonexistent.csv')
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)

if __name__ == '__main__':
    unittest.main()