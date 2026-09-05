import unittest
import pandas as pd
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from agent.agent import DataPilotAgent
from data.dataset_manager import dataset_manager
from ml.intent_classifier import intent_classifier

class TestDataPilotAgent(unittest.TestCase):
    """Test cases for DataPilot Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = DataPilotAgent()
        
        # Create sample dataset
        sample_data = pd.DataFrame({
            'Name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie'],
            'Age': [30, 28, 35, 32, 45],
            'Salary': [65000, 52000, 58000, 70000, 55000],
            'Experience': [5, 3, 7, 6, 15],
            'Department': ['IT', 'HR', 'Sales', 'IT', 'HR']
        })
        
        # Load dataset into manager
        dataset_manager.current_dataset = sample_data
        dataset_manager.dataset_metadata = {
            'rows': 5,
            'columns': 5,
            'numeric_columns': ['Age', 'Salary', 'Experience'],
            'categorical_columns': ['Name', 'Department'],
            'column_names': ['Name', 'Age', 'Salary', 'Experience', 'Department']
        }
    
    def tearDown(self):
        """Clean up test fixtures"""
        dataset_manager.clear_dataset()
    
    def test_agent_observe(self):
        """Test agent observation step"""
        observation = self.agent._observe("What is the average salary?")
        
        self.assertIn('dataset_loaded', observation)
        self.assertTrue(observation['dataset_loaded'])
        self.assertIn('rows', observation)
        self.assertIn('columns', observation)
    
    def test_agent_observe_no_dataset(self):
        """Test agent observation when no dataset is loaded"""
        dataset_manager.clear_dataset()
        observation = self.agent._observe("What is the average salary?")
        
        self.assertFalse(observation['dataset_loaded'])
        self.assertIn('error', observation)
    
    def test_interpret_question(self):
        """Test question interpretation using ML classifier"""
        result = self.agent._interpret_question("What is the average salary?")
        
        self.assertIn('intent', result)
        self.assertIn('confidence', result)
        self.assertIn('question', result)
    
    def test_select_tool(self):
        """Test tool selection by agent"""
        result = self.agent._select_tool('summary_statistics')
        
        self.assertIn('success', result)
        if result['success']:
            self.assertIn('selected_tool', result)
            self.assertIn('parameters', result)
            self.assertIn('candidate_tools', result)
    
    def test_select_tool_invalid_intent(self):
        """Test tool selection with invalid intent"""
        result = self.agent._select_tool('invalid_intent')
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_validate_tool_selection_correlation(self):
        """Test validation for correlation analysis tool selection"""
        metadata = dataset_manager.get_metadata()
        validation = self.agent._validate_tool_selection(
            'correlation_analysis',
            {'dataset': dataset_manager.get_dataset()},
            metadata
        )
        
        self.assertTrue(validation['valid'])
    
    def test_validate_tool_selection_insufficient_numeric(self):
        """Test validation with insufficient numeric columns"""
        metadata = {
            'numeric_columns': ['Salary'],  # Only one numeric column
            'rows': 10
        }
        validation = self.agent._validate_tool_selection(
            'correlation_analysis',
            {'dataset': True},
            metadata
        )
        
        self.assertFalse(validation['valid'])
        self.assertIn('requires at least 2', validation['reason'])
    
    def test_validate_tool_selection_insufficient_rows(self):
        """Test validation with insufficient rows for ML"""
        metadata = {
            'numeric_columns': ['Age', 'Salary'],
            'rows': 5  # Less than 10
        }
        validation = self.agent._validate_tool_selection(
            'machine_learning',
            {'dataset': True},
            metadata
        )
        
        self.assertFalse(validation['valid'])
        self.assertIn('requires at least 10', validation['reason'])
    
    def test_extract_parameters_summary_statistics(self):
        """Test parameter extraction for summary statistics"""
        metadata = dataset_manager.get_metadata()
        parameters = self.agent._extract_parameters('summary_statistics', metadata)
        
        self.assertIn('dataset', parameters)
        self.assertIn('metadata', parameters)
        self.assertIn('columns', parameters)
    
    def test_extract_parameters_correlation(self):
        """Test parameter extraction for correlation analysis"""
        metadata = dataset_manager.get_metadata()
        parameters = self.agent._extract_parameters('correlation_analysis', metadata)
        
        self.assertIn('dataset', parameters)
        self.assertIn('metadata', parameters)
        self.assertIn('columns', parameters)
    
    def test_generate_response(self):
        """Test response generation"""
        result = {'operation': 'mean', 'value': 50000}
        validation = {'success': True, 'message': 'Valid'}
        
        response = self.agent._generate_response("What is the average salary?", result, validation)
        
        self.assertIn('explanation', response)
        self.assertIn('result', response)
    
    def test_generate_response_with_error(self):
        """Test response generation with validation error"""
        result = {'value': 50000}
        validation = {'success': False, 'message': 'Invalid result'}
        
        response = self.agent._generate_response("What is the average salary?", result, validation)
        
        self.assertIn('explanation', response)
        self.assertIn('could not be completed', response['explanation'].lower())
    
    def test_explain_result(self):
        """Test result explanation generation"""
        result = {
            'operation': 'mean',
            'column': 'Salary',
            'value': 50000,
            'interpretation': 'Average salary is moderate'
        }
        
        explanation = self.agent._explain_result(result)
        
        self.assertIsInstance(explanation, str)
        self.assertIn('mean', explanation.lower())
    
    def test_handle_error(self):
        """Test error handling"""
        error_msg = "Test error"
        result = self.agent._handle_error(error_msg)
        
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], error_msg)
        self.assertIn('trace', result)
    
    def test_analyze_pipeline(self):
        """Test complete analysis pipeline"""
        result = self.agent.analyze("What is the average salary?")
        
        self.assertIn('success', result)
        self.assertIn('question', result)
        self.assertIn('intent', result)
        self.assertIn('confidence', result)
        self.assertIn('trace', result)
    
    def test_analyze_pipeline_no_dataset(self):
        """Test analysis pipeline when no dataset is loaded"""
        dataset_manager.clear_dataset()
        result = self.agent.analyze("What is the average salary?")
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)

if __name__ == '__main__':
    unittest.main()