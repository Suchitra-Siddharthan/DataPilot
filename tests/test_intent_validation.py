import unittest
import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

# Change to backend directory for relative imports
original_dir = os.getcwd()
os.chdir(backend_path)

from agent.agent import DataPilotAgent
from data.dataset_manager import dataset_manager
import pandas as pd

class TestIntentValidation(unittest.TestCase):
    """Test cases for intent validation layer"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Store original directory
        self.original_dir = original_dir
        
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
        # Restore original directory
        os.chdir(self.original_dir)
    
    def test_correlation_question_validation(self):
        """Test that correlation questions are correctly validated"""
        correlation_questions = [
            "Is salary related to experience?",
            "Find the correlation between age and income",
            "What is the relationship between salary and experience?"
        ]
        
        for question in correlation_questions:
            result = self.agent._interpret_question(question)
            print(f"Question: {question}")
            print(f"Predicted intent: {result['intent']}")
            self.assertEqual(result['intent'], 'correlation_analysis', 
                           f"Failed for question: {question}")
    
    def test_outlier_question_validation(self):
        """Test that outlier detection questions are correctly validated"""
        outlier_questions = [
            "Find unusual salary values",
            "Detect outliers in the age column",
            "Identify unusual values in salary"
        ]
        
        for question in outlier_questions:
            result = self.agent._interpret_question(question)
            print(f"Question: {question}")
            print(f"Predicted intent: {result['intent']}")
            self.assertEqual(result['intent'], 'outlier_detection',
                           f"Failed for question: {question}")
    
    def test_summary_statistics_question(self):
        """Test that summary statistics questions are correctly classified"""
        summary_questions = [
            "What is the average salary?",
            "Find the median age",
            "Calculate the mean salary"
        ]
        
        for question in summary_questions:
            result = self.agent._interpret_question(question)
            print(f"Question: {question}")
            print(f"Predicted intent: {result['intent']}")
            self.assertEqual(result['intent'], 'summary_statistics',
                           f"Failed for question: {question}")
    
    def test_distribution_question(self):
        """Test that distribution analysis questions are correctly classified"""
        distribution_questions = [
            "Show the distribution of salaries",
            "Display the salary distribution",
            "Show the age distribution"
        ]
        
        for question in distribution_questions:
            result = self.agent._interpret_question(question)
            print(f"Question: {question}")
            print(f"Predicted intent: {result['intent']}")
            self.assertEqual(result['intent'], 'distribution_analysis',
                           f"Failed for question: {question}")
    
    def test_preprocessing_question(self):
        """Test that preprocessing questions are correctly classified"""
        preprocessing_questions = [
            "Handle missing values",
            "Clean the dataset",
            "Prepare the data for analysis"
        ]
        
        for question in preprocessing_questions:
            result = self.agent._interpret_question(question)
            print(f"Question: {question}")
            print(f"Predicted intent: {result['intent']}")
            self.assertEqual(result['intent'], 'data_preprocessing',
                           f"Failed for question: {question}")
    
    def test_feature_engineering_question(self):
        """Test that feature engineering questions are correctly classified"""
        feature_questions = [
            "Create a new age group column",
            "Transform the salary column",
            "Add a new feature for age groups"
        ]
        
        for question in feature_questions:
            result = self.agent._interpret_question(question)
            print(f"Question: {question}")
            print(f"Predicted intent: {result['intent']}")
            self.assertEqual(result['intent'], 'feature_engineering',
                           f"Failed for question: {question}")
    
    def test_machine_learning_question(self):
        """Test that machine learning questions are correctly classified"""
        ml_questions = [
            "Predict customer churn",
            "Build a classification model",
            "Train a regression model"
        ]
        
        for question in ml_questions:
            result = self.agent._interpret_question(question)
            print(f"Question: {question}")
            print(f"Predicted intent: {result['intent']}")
            self.assertEqual(result['intent'], 'machine_learning',
                           f"Failed for question: {question}")
    
    def test_validation_override_flag(self):
        """Test that validation override is properly flagged"""
        # This question should trigger validation override
        result = self.agent._interpret_question("Is salary related to experience?")
        
        # Check if validation override occurred
        if result.get('validation_override'):
            self.assertIn('original_svm_intent', result)
            print(f"Validation override occurred: {result['original_svm_intent']} -> {result['intent']}")
    
    def test_no_validation_for_ambiguous_questions(self):
        """Test that ambiguous questions use SVM prediction without override"""
        # Questions that should rely on SVM
        ambiguous_questions = [
            "Analyze the data",
            "Tell me about the dataset",
            "Give me insights"
        ]
        
        for question in ambiguous_questions:
            result = self.agent._interpret_question(question)
            # Should not have validation override for ambiguous questions
            self.assertFalse(result.get('validation_override', False),
                           f"Unexpected validation override for: {question}")

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)