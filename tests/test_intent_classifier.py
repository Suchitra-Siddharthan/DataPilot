import unittest
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ml.intent_classifier import IntentClassifier

class TestIntentClassifier(unittest.TestCase):
    """Test cases for ML Intent Classifier"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.classifier = IntentClassifier()
    
    def test_fallback_prediction_summary_statistics(self):
        """Test fallback prediction for summary statistics intent"""
        question = "What is the average salary?"
        result = self.classifier._fallback_prediction(question)
        
        self.assertIn('intent', result)
        self.assertIn('confidence', result)
        self.assertIn('question', result)
        self.assertEqual(result['question'], question)
        self.assertTrue(result['fallback_used'])
    
    def test_fallback_prediction_correlation(self):
        """Test fallback prediction for correlation analysis intent"""
        question = "Is salary related to experience?"
        result = self.classifier._fallback_prediction(question)
        
        self.assertIn('intent', result)
        self.assertIn('correlation', result['intent'].lower())
    
    def test_fallback_prediction_distribution(self):
        """Test fallback prediction for distribution analysis intent"""
        question = "Show the distribution of salaries"
        result = self.classifier._fallback_prediction(question)
        
        self.assertIn('intent', result)
        self.assertIn('distribution', result['intent'].lower())
    
    def test_fallback_prediction_feature_engineering(self):
        """Test fallback prediction for feature engineering intent"""
        question = "Create a new age group column"
        result = self.classifier._fallback_prediction(question)
        
        self.assertIn('intent', result)
        self.assertIn('feature', result['intent'].lower())
    
    def test_fallback_prediction_preprocessing(self):
        """Test fallback prediction for data preprocessing intent"""
        question = "Handle missing values in the dataset"
        result = self.classifier._fallback_prediction(question)
        
        self.assertIn('intent', result)
        self.assertIn('preprocess', result['intent'].lower())
    
    def test_fallback_prediction_outlier_detection(self):
        """Test fallback prediction for outlier detection intent"""
        question = "Find unusual salary values"
        result = self.classifier._fallback_prediction(question)
        
        self.assertIn('intent', result)
        self.assertIn('outlier', result['intent'].lower())
    
    def test_fallback_prediction_machine_learning(self):
        """Test fallback prediction for machine learning intent"""
        question = "Predict customer churn"
        result = self.classifier._fallback_prediction(question)
        
        self.assertIn('intent', result)
        self.assertIn('machine_learning', result['intent'].lower())
    
    def test_get_intents(self):
        """Test getting list of supported intents"""
        intents = self.classifier.get_intents()
        
        self.assertIsInstance(intents, list)
        self.assertEqual(len(intents), 7)
        self.assertIn('summary_statistics', intents)
        self.assertIn('correlation_analysis', intents)
    
    def test_confidence_calculation(self):
        """Test confidence score calculation from decision scores"""
        import numpy as np
        
        decision_scores = np.array([1.5, 0.8, -0.3, -1.2])
        confidence = self.classifier._calculate_confidence(decision_scores)
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_predict_without_model(self):
        """Test prediction when model is not loaded"""
        question = "What is the average salary?"
        result = self.classifier.predict(question)
        
        self.assertIn('intent', result)
        self.assertIn('confidence', result)
        self.assertIn('question', result)
        self.assertFalse(result.get('model_loaded', True))

if __name__ == '__main__':
    unittest.main()