import joblib
import numpy as np
from typing import Dict, Any, Optional
import os

def _default_model_path() -> str:
    """Resolve the intent model relative to the backend directory, not the CWD."""
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(backend_dir, "models", "datapilot_intent_svm.joblib")


class IntentClassifier:
    """ML Intent Classifier using TF-IDF + Linear SVM"""
    
    def __init__(self, model_path: str = None):
        self.model = None
        self.vectorizer = None
        self.model_path = model_path or _default_model_path()
        self.intents = [
            "summary_statistics",
            "correlation_analysis", 
            "distribution_analysis",
            "feature_engineering",
            "data_preprocessing",
            "outlier_detection",
            "machine_learning"
        ]
        
    def load_model(self) -> bool:
        """Load the trained ML model (scikit-learn Pipeline)"""
        try:
            if os.path.exists(self.model_path):
                model_data = joblib.load(self.model_path)
                
                # The saved model is a complete scikit-learn Pipeline
                # containing TfidfVectorizer and LinearSVC
                self.model = model_data
                self.vectorizer = None  # Vectorizer is part of the pipeline
                
                print(f"Model loaded successfully from {self.model_path}")
                print(f"Model type: {type(self.model)}")
                return True
            else:
                print(f"Warning: Model file not found at {self.model_path}")
                return False
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False
    
    def predict(self, question: str) -> Dict[str, Any]:
        """Predict intent from natural language question using scikit-learn Pipeline"""
        if self.model is None:
            return self._fallback_prediction(question)
        
        try:
            # The model is a scikit-learn Pipeline that contains both
            # TfidfVectorizer and LinearSVC, so we pass raw text directly
            prediction = self.model.predict([question])[0]
            
            # Get decision function values (NOT probabilities)
            # LinearSVC decision_function values are not probabilities
            decision_scores = self.model.decision_function([question])[0]
            
            # Calculate normalized confidence score from decision values
            confidence = self._calculate_confidence(decision_scores)
            
            return {
                'intent': prediction,
                'confidence': confidence,
                'question': question,
                'model_loaded': True,
                'fallback_used': False
            }
            
        except Exception as e:
            print(f"Prediction error: {str(e)}")
            return self._fallback_prediction(question)
    
    def _calculate_confidence(self, decision_scores: np.ndarray) -> float:
        """
        Calculate normalized confidence from decision scores.
        NOTE: This is NOT a calibrated probability.
        LinearSVC decision_function values are not probabilities.
        This is a normalized score for relative confidence ranking.
        """
        # Normalize using softmax-like approach on decision scores
        exp_scores = np.exp(decision_scores - np.max(decision_scores))
        normalized_scores = exp_scores / np.sum(exp_scores)
        
        # Return the max normalized score
        confidence = float(np.max(normalized_scores))
        
        # Clip to valid range
        confidence = max(0.0, min(1.0, confidence))
        
        return confidence
    
    def _fallback_prediction(self, question: str) -> Dict[str, Any]:
        """Fallback prediction when model is not available"""
        # Simple keyword-based fallback
        question_lower = question.lower()
        
        keywords = {
            'summary_statistics': ['average', 'mean', 'median', 'sum', 'count', 'minimum', 'maximum', 'std'],
            'correlation_analysis': ['correlation', 'relationship', 'related', 'between', 'vs'],
            'distribution_analysis': ['distribution', 'histogram', 'spread', 'range'],
            'feature_engineering': ['create', 'new column', 'transform', 'feature'],
            'data_preprocessing': ['missing', 'handle', 'clean', 'preprocess', 'prepare'],
            'outlier_detection': ['outlier', 'unusual', 'anomaly', 'detect'],
            'machine_learning': ['predict', 'classify', 'regression', 'model', 'train']
        }
        
        scores = {intent: 0 for intent in self.intents}
        
        for intent, words in keywords.items():
            for word in words:
                if word in question_lower:
                    scores[intent] += 1
        
        predicted_intent = max(scores, key=scores.get)
        confidence = min(1.0, scores[predicted_intent] / 3.0)  # Normalize
        
        return {
            'intent': predicted_intent,
            'confidence': confidence,
            'question': question,
            'model_loaded': False,
            'fallback_used': True
        }
    
    def get_intents(self) -> list:
        """Get list of supported intents"""
        return self.intents.copy()


# Global instance
intent_classifier = IntentClassifier()