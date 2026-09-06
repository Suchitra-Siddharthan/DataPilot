import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder

def machine_learning(dataset: pd.DataFrame, metadata: Dict[str, Any], 
                    target_column: str = None, task_type: str = None,
                    algorithm: str = 'random_forest',
                    feature_columns: List[str] = None) -> Dict[str, Any]:
    """
    Perform machine learning analysis.
    Automatically detects task type (classification/regression) if not specified.
    """
    try:
        if dataset is None or len(dataset) == 0:
            return {'success': False, 'error': 'Dataset is empty or not loaded'}
        
        if target_column is None:
            # Try to infer target column
            target_column = _infer_target_column(dataset, metadata)
            if target_column is None:
                return {
                    'success': False,
                    'error': "No suitable target column could be inferred. Please provide an explicit target column (e.g. a binary 'churn' or 'left' column) for employee churn/leave predictions."
                }
        
        if target_column not in dataset.columns:
            return {'success': False, 'error': f'Target column {target_column} not found in dataset'}
        
        # Prepare data
        X, y, feature_columns, target_encoder = _prepare_data(
            dataset, target_column, feature_columns
        )
        
        if X is None or y is None:
            return {'success': False, 'error': 'Failed to prepare data for machine learning'}
        
        # Detect task type if not specified
        if task_type is None:
            task_type = _detect_task_type(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model based on task type and algorithm
        if task_type == 'classification':
            result = _train_classification_model(
                X, y, X_train, X_test, y_train, y_test, algorithm,
                feature_columns, target_encoder
            )
        else:
            result = _train_regression_model(
                X, y, X_train, X_test, y_train, y_test, algorithm,
                feature_columns
            )
        
        result['target_column'] = target_column
        result['task_type'] = task_type
        result['algorithm'] = algorithm
        result['feature_columns'] = feature_columns
        prediction_dataset = dataset.copy()
        prediction_dataset['prediction'] = result['predictions']
        result['prediction_dataset'] = prediction_dataset.where(
            pd.notnull(prediction_dataset), None
        ).to_dict(orient='records')
        
        return result
        
    except Exception as e:
        return {'success': False, 'error': f'Machine learning analysis failed: {str(e)}'}


def _infer_target_column(dataset: pd.DataFrame, metadata: Dict[str, Any]) -> Optional[str]:
    """Try to infer target column from dataset"""
    # Prefer explicit churn/leave-like columns (explicit names)
    churn_keywords = ['churn', 'left', 'leaving', 'attrition', 'resigned', 'turnover', 'left_company']
    potential_targets = [col for col in dataset.columns if any(k in col.lower() for k in churn_keywords)]

    if potential_targets:
        return potential_targets[0]

    # Otherwise prefer low-cardinality columns (likely targets)
    total = len(dataset)
    low_cardinality = []
    for col in dataset.columns:
        try:
            nunique = int(dataset[col].nunique(dropna=True))
        except Exception:
            nunique = 0
        if nunique <= 10 or (total > 0 and (nunique / total) < 0.05):
            low_cardinality.append(col)

    if low_cardinality:
        return low_cardinality[0]

    # No good target found - do NOT fallback to an arbitrary column like the last column.
    return None


def _detect_task_type(target: pd.Series) -> str:
    """Detect if task is classification or regression"""
    # Accept array-like inputs (numpy arrays, pandas Series)
    try:
        # If target is a pandas Series use nunique, otherwise fall back to numpy
        if hasattr(target, 'nunique'):
            unique_values = int(target.nunique())
            total = len(target)
        else:
            import numpy as _np
            unique_values = int(_np.unique(target).size)
            total = int(len(target))

        # If few unique values relative to total, likely classification
        if unique_values <= 10 or (total > 0 and (unique_values / total) < 0.05):
            return 'classification'
        else:
            return 'regression'
    except Exception:
        # Conservative default to classification on failure
        return 'classification'


def _prepare_data(dataset: pd.DataFrame, target_column: str,
                  requested_features: List[str] = None) -> tuple:
    """Prepare features and target for ML"""
    # Drop target column from features
    feature_columns = [col for col in dataset.columns if col != target_column]
    if requested_features:
        feature_columns = [col for col in requested_features if col in feature_columns]

    # Select only numeric features for simplicity
    numeric_features = dataset[feature_columns].select_dtypes(include=[np.number]).columns.tolist()
    
    if not numeric_features:
        return None, None, []
    
    X = dataset[numeric_features].fillna(0)  # Simple imputation
    y = dataset[target_column].fillna(dataset[target_column].mode()[0] if dataset[target_column].dtype == 'object' else 0)
    
    # Encode target if categorical
    target_encoder = None
    if not pd.api.types.is_numeric_dtype(y):
        target_encoder = LabelEncoder()
        y = target_encoder.fit_transform(y.astype(str))
    
    return X, y, numeric_features, target_encoder


def _train_classification_model(X, y, X_train, X_test, y_train, y_test,
                               algorithm: str, feature_columns: List[str],
                               target_encoder: Optional[LabelEncoder]) -> Dict[str, Any]:
    """Train classification model"""
    if algorithm == 'logistic_regression':
        model = LogisticRegression(max_iter=1000, random_state=42)
    else:  # random_forest
        model = RandomForestClassifier(n_estimators=100, random_state=42)
    
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    
    # Get feature importance if available
    feature_importance = {}
    if hasattr(model, 'feature_importances_'):
        for feat, imp in zip(feature_columns, model.feature_importances_):
            feature_importance[feat] = float(imp)

    model.fit(X, y)
    predictions = model.predict(X)
    if target_encoder is not None:
        predictions = target_encoder.inverse_transform(predictions.astype(int))
    predictions = [str(value) if target_encoder is not None else value for value in predictions]
    
    return {
        'success': True,
        'operation': 'classification',
        'model_type': algorithm,
        'accuracy': float(accuracy),
        'feature_importance': feature_importance,
        'predictions': predictions,
        'test_samples': len(y_test),
        'training_samples': len(y_train)
    }


def _train_regression_model(X, y, X_train, X_test, y_train, y_test, algorithm: str,
                            feature_columns: List[str]) -> Dict[str, Any]:
    """Train regression model"""
    if algorithm == 'linear_regression':
        model = LinearRegression()
    else:  # random_forest
        model = RandomForestRegressor(n_estimators=100, random_state=42)
    
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    # Get feature importance if available
    feature_importance = {}
    if hasattr(model, 'feature_importances_'):
        for feat, imp in zip(feature_columns, model.feature_importances_):
            feature_importance[feat] = float(imp)
    elif hasattr(model, 'coef_'):
        for feat, coef in zip(feature_columns, model.coef_):
            feature_importance[feat] = float(coef)

    model.fit(X, y)
    predictions = model.predict(X)
    
    return {
        'success': True,
        'operation': 'regression',
        'model_type': algorithm,
        'mse': float(mse),
        'r2_score': float(r2),
        'feature_importance': feature_importance,
        'predictions': [float(value) for value in predictions],
        'test_samples': len(y_test),
        'training_samples': len(y_train)
    }


def predict_target(dataset: pd.DataFrame, target_column: str, 
                  new_data: pd.DataFrame = None) -> Dict[str, Any]:
    """
    Make predictions using a trained model.
    This is a placeholder - in production, you'd need to save/load trained models.
    """
    try:
        # This would require model persistence functionality
        # For now, return a message indicating the need for model persistence
        return {
            'success': False,
            'error': 'Model persistence not implemented. Train and save models first.',
            'note': 'To enable predictions, implement model saving/loading functionality'
        }
    except Exception as e:
        return {'success': False, 'error': f'Prediction failed: {str(e)}'}