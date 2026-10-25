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

    def test_distribution_question_selects_only_requested_column_and_histogram(self):
        """A named distribution request should scope both statistics and histogram."""
        selection = self.agent._select_tool(
            'distribution_analysis',
            'Show the distribution of ages'
        )

        self.assertTrue(selection['success'], selection.get('error'))
        self.assertEqual(selection['parameters']['columns'], ['Age'])

        execution = self.agent._execute_tool(
            selection['selected_tool'],
            selection['parameters']
        )
        self.assertTrue(execution['success'], execution.get('error'))
        distribution = execution['result']
        self.assertEqual(distribution['columns_analyzed'], ['Age'])
        self.assertEqual(list(distribution['results']), ['Age'])
        self.assertEqual(len(distribution['visualizations']), 1)
        self.assertEqual(distribution['visualizations'][0]['parameters']['column'], 'Age')
        self.assertTrue(distribution['visualizations'][0]['image'])
        self.assertEqual(
            execution['executed_tools'],
            ['distribution_analysis', 'create_visualization']
        )

        analysis = self.agent.analyze('Show the distribution of ages')
        self.assertTrue(analysis['success'], analysis.get('error'))
        self.assertEqual(
            analysis['selected_tools'],
            ['distribution_analysis', 'create_visualization']
        )
        self.assertEqual(
            analysis['tool_results'][0]['executed_tools'],
            ['distribution_analysis', 'create_visualization']
        )

    def test_distribution_question_for_unknown_column_requests_available_column(self):
        """Unknown requested distribution columns should not widen to all numeric fields."""
        selection = self.agent._select_tool(
            'distribution_analysis',
            'Show the distribution of bonus'
        )

        self.assertFalse(selection['success'])
        self.assertIn('bonus', selection['error'])
        self.assertIn('Age, Salary, Experience', selection['error'])
        self.assertIn('choose an available numerical column', selection['error'])

    def test_distribution_question_can_explicitly_request_all_numeric_columns(self):
        """An explicit all-numeric request should retain multi-column distribution."""
        parameters = self.agent._extract_parameters(
            'distribution_analysis',
            dataset_manager.get_metadata(),
            'Show distributions for all numerical columns'
        )

        self.assertEqual(parameters['columns'], ['Age', 'Salary', 'Experience'])
    
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
        self.assertEqual(result['selected_tools'], ['summary_statistics'])
    
    def test_analyze_pipeline_no_dataset(self):
        """Test analysis pipeline when no dataset is loaded"""
        dataset_manager.clear_dataset()
        result = self.agent.analyze("What is the average salary?")
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_analyze_question_with_summary_and_correlation_tasks(self):
        """Every requested analytical task should execute and be answered."""
        question = (
            "Find the department with the highest average salary and check "
            "the correlation between salary and experience"
        )

        result = self.agent.analyze(question)

        self.assertTrue(result['success'], result.get('error'))
        self.assertEqual(
            result['selected_tools'],
            ['summary_statistics', 'correlation_analysis']
        )
        self.assertEqual(
            [item['tool'] for item in result['tool_results']],
            ['summary_statistics', 'correlation_analysis']
        )

        summary = result['tool_results'][0]['result']
        self.assertEqual(list(summary['results']), ['Salary'])
        department_means = summary['results']['Salary']['statistics']['mean']
        self.assertEqual(summary['results']['Salary']['group_by'], 'Department')
        self.assertEqual(max(department_means, key=department_means.get), 'IT')
        self.assertNotIn('Experience', summary['results'])

        correlation = result['tool_results'][1]['result']
        requested_pair = next(
            item for item in correlation['correlations']
            if {item['column_x'], item['column_y']} == {'Salary', 'Experience'}
        )
        self.assertIsInstance(requested_pair['correlation'], float)
        self.assertIn('highest average', result['explanation'].lower())
        self.assertIn('salary and experience', result['explanation'].lower())

    def test_analyze_question_with_three_requested_tasks(self):
        """Multi-tool execution should include each detected task, not just two."""
        question = (
            "Find the average salary by department, check the correlation "
            "between salary and experience, and show the salary distribution"
        )

        result = self.agent.analyze(question)

        self.assertTrue(result['success'], result.get('error'))
        self.assertEqual(
            set(result['selected_tools']),
            {
                'summary_statistics',
                'correlation_analysis',
                'distribution_analysis',
                'create_visualization'
            }
        )
        result_by_tool = {item['tool']: item['result'] for item in result['tool_results']}
        self.assertTrue(result_by_tool['summary_statistics']['results']['Salary'])
        self.assertTrue(result_by_tool['correlation_analysis']['correlations'])
        self.assertIn('Salary', result_by_tool['distribution_analysis']['results'])

        explanation = result['explanation'].lower()
        self.assertIn('average salary by department', explanation)
        self.assertIn('salary and experience', explanation)
        self.assertIn('salary distribution', explanation)
        self.assertIn('range', explanation)

if __name__ == '__main__':
    unittest.main()