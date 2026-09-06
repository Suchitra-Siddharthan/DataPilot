import pandas as pd
import numpy as np
from typing import Dict, Any, List

def feature_engineering(dataset: pd.DataFrame, metadata: Dict[str, Any], 
                       operation: str = None, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Perform safe feature engineering operations.
    Only predefined transformations are allowed.
    """
    try:
        if dataset is None or len(dataset) == 0:
            return {'success': False, 'error': 'Dataset is empty or not loaded'}
        
        if parameters is None:
            parameters = {}
        
        if operation is None:
            return {'success': False, 'error': 'No operation specified for feature engineering'}
        
        result_dataset = dataset.copy()
        transformations = []
        
        # Safe predefined operations
        if operation == 'create_sum':
            columns = parameters.get('columns', [])
            new_column = parameters.get('new_column', 'sum_column')
            
            if len(columns) < 2:
                return {'success': False, 'error': 'Sum operation requires at least 2 columns'}
            
            valid_columns = [col for col in columns if col in dataset.columns]
            if len(valid_columns) < 2:
                return {'success': False, 'error': 'Invalid columns for sum operation'}
            
            result_dataset[new_column] = result_dataset[valid_columns].sum(axis=1)
            transformations.append(f"Created sum column '{new_column}' from {valid_columns}")
        
        elif operation == 'create_ratio':
            numerator = parameters.get('numerator')
            denominator = parameters.get('denominator')
            new_column = parameters.get('new_column', 'ratio_column')
            
            if not numerator or not denominator:
                return {'success': False, 'error': 'Ratio operation requires numerator and denominator'}
            
            if numerator not in dataset.columns or denominator not in dataset.columns:
                return {'success': False, 'error': 'Invalid columns for ratio operation'}
            
            # Avoid division by zero
            result_dataset[new_column] = result_dataset[numerator] / (result_dataset[denominator] + 1e-8)
            transformations.append(f"Created ratio column '{new_column}' as {numerator}/{denominator}")
        
        elif operation == 'bin_column':
            column = parameters.get('column')
            bins = parameters.get('bins', 5)
            new_column = parameters.get('new_column', f"{column}_binned")
            
            if not column or column not in dataset.columns:
                return {'success': False, 'error': 'Invalid column for binning operation'}
            
            if not pd.api.types.is_numeric_dtype(dataset[column]):
                return {'success': False, 'error': 'Binning requires numerical column'}
            
            result_dataset[new_column] = pd.cut(result_dataset[column], bins=bins, labels=False)
            transformations.append(f"Created binned column '{new_column}' from '{column}' with {bins} bins")
        
        elif operation == 'create_age_group':
            column = parameters.get('column', 'age')
            new_column = parameters.get('new_column', 'age_group')
            
            if column not in dataset.columns:
                return {'success': False, 'error': f'Column {column} not found'}
            
            if not pd.api.types.is_numeric_dtype(dataset[column]):
                return {'success': False, 'error': 'Age grouping requires numerical column'}
            
            # Define age groups
            bins = [0, 18, 25, 35, 50, 65, 100]
            labels = ['0-17', '18-24', '25-34', '35-49', '50-64', '65+']
            
            result_dataset[new_column] = pd.cut(result_dataset[column], bins=bins, labels=labels, right=False)
            transformations.append(f"Created age group column '{new_column}' from '{column}'")
        
        elif operation == 'create_categorical_flag':
            column = parameters.get('column')
            condition = parameters.get('condition', '>')
            value = parameters.get('value')
            new_column = parameters.get('new_column', f"{column}_flag")
            
            if not column or column not in dataset.columns:
                return {'success': False, 'error': 'Invalid column for flag creation'}
            
            if value is None:
                return {'success': False, 'error': 'Value required for flag condition'}
            
            if condition == '>':
                result_dataset[new_column] = (result_dataset[column] > value).astype(int)
            elif condition == '<':
                result_dataset[new_column] = (result_dataset[column] < value).astype(int)
            elif condition == '>=':
                result_dataset[new_column] = (result_dataset[column] >= value).astype(int)
            elif condition == '<=':
                result_dataset[new_column] = (result_dataset[column] <= value).astype(int)
            elif condition == '==':
                result_dataset[new_column] = (result_dataset[column] == value).astype(int)
            else:
                return {'success': False, 'error': f'Unsupported condition: {condition}'}
            
            transformations.append(f"Created flag column '{new_column}' where {column} {condition} {value}")
        
        else:
            return {'success': False, 'error': f'Unsupported feature engineering operation: {operation}'}
        
        return {
            'success': True,
            'operation': 'feature_engineering',
            'transformations': transformations,
            'new_columns': [t.split("'")[1] for t in transformations if "'" in t],
            'dataset_shape': result_dataset.shape,
            'processed_dataset': result_dataset.where(
                pd.notnull(result_dataset), None
            ).to_dict(orient='records')
        }
        
    except Exception as e:
        return {'success': False, 'error': f'Feature engineering failed: {str(e)}'}


def encode_categorical(dataset: pd.DataFrame, column: str, method: str = 'onehot') -> Dict[str, Any]:
    """
    Encode categorical column using safe methods.
    Methods: 'onehot', 'label'
    """
    try:
        if column not in dataset.columns:
            return {'success': False, 'error': f'Column {column} not found'}
        
        if pd.api.types.is_numeric_dtype(dataset[column]):
            return {'success': False, 'error': f'Column {column} is already numerical'}
        
        result_dataset = dataset.copy()
        
        if method == 'onehot':
            # One-hot encoding
            dummies = pd.get_dummies(result_dataset[column], prefix=column)
            result_dataset = pd.concat([result_dataset, dummies], axis=1)
            
            return {
                'success': True,
                'operation': 'onehot_encoding',
                'column': column,
                'new_columns': list(dummies.columns),
                'dataset_shape': result_dataset.shape
            }
        
        elif method == 'label':
            # Label encoding
            unique_values = result_dataset[column].unique()
            label_map = {val: idx for idx, val in enumerate(unique_values)}
            new_column = f"{column}_encoded"
            result_dataset[new_column] = result_dataset[column].map(label_map)
            
            return {
                'success': True,
                'operation': 'label_encoding',
                'column': column,
                'new_column': new_column,
                'label_map': label_map,
                'dataset_shape': result_dataset.shape
            }
        
        else:
            return {'success': False, 'error': f'Unsupported encoding method: {method}'}
        
    except Exception as e:
        return {'success': False, 'error': f'Categorical encoding failed: {str(e)}'}