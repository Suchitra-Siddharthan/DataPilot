import pandas as pd
import numpy as np
from typing import Dict, Any, List

def data_preprocessing(dataset: pd.DataFrame, metadata: Dict[str, Any], 
                     operation: str = None, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Perform safe data preprocessing operations.
    Includes missing value handling, duplicate detection, and type inspection.
    """
    try:
        if dataset is None or len(dataset) == 0:
            return {'success': False, 'error': 'Dataset is empty or not loaded'}
        
        if parameters is None:
            parameters = {}
        
        if operation is None:
            return {'success': False, 'error': 'No operation specified for preprocessing'}
        
        result_dataset = dataset.copy()
        operations_performed = []
        
        if operation == 'handle_missing':
            method = parameters.get('method', 'mean')
            columns = parameters.get('columns', [])
            
            if not columns:
                # Handle all columns with missing values
                columns = dataset.columns[dataset.isnull().any()].tolist()
            
            for col in columns:
                if col not in dataset.columns:
                    continue
                
                missing_count = dataset[col].isnull().sum()
                if missing_count == 0:
                    continue
                
                if pd.api.types.is_numeric_dtype(dataset[col]):
                    if method == 'mean':
                        fill_value = dataset[col].mean()
                    elif method == 'median':
                        fill_value = dataset[col].median()
                    elif method == 'mode':
                        fill_value = dataset[col].mode()[0] if not dataset[col].mode().empty else 0
                    elif method == 'zero':
                        fill_value = 0
                    else:
                        fill_value = dataset[col].mean()  # default
                    
                    result_dataset[col] = result_dataset[col].fillna(fill_value)
                    operations_performed.append(f"Filled {missing_count} missing values in '{col}' with {method}")
                
                else:
                    # For categorical columns, use mode or 'Unknown'
                    if method == 'mode':
                        fill_value = dataset[col].mode()[0] if not dataset[col].mode().empty else 'Unknown'
                    else:
                        fill_value = 'Unknown'
                    
                    result_dataset[col] = result_dataset[col].fillna(fill_value)
                    operations_performed.append(f"Filled {missing_count} missing values in '{col}' with '{fill_value}'")
        
        elif operation == 'remove_duplicates':
            subset = parameters.get('subset')
            keep = parameters.get('keep', 'first')
            
            original_count = len(result_dataset)
            result_dataset = result_dataset.drop_duplicates(subset=subset, keep=keep)
            removed_count = original_count - len(result_dataset)
            
            operations_performed.append(f"Removed {removed_count} duplicate rows")
        
        elif operation == 'inspect_types':
            type_info = {}
            for col in dataset.columns:
                type_info[col] = {
                    'dtype': str(dataset[col].dtype),
                    'is_numeric': pd.api.types.is_numeric_dtype(dataset[col]),
                    'is_categorical': pd.api.types.is_categorical_dtype(dataset[col]) or dataset[col].dtype == 'object',
                    'is_datetime': pd.api.types.is_datetime64_any_dtype(dataset[col])
                }
            
            return {
                'success': True,
                'operation': 'type_inspection',
                'type_info': type_info,
                'operations_performed': operations_performed
            }
        
        elif operation == 'detect_missing':
            missing_info = {}
            for col in dataset.columns:
                missing_count = dataset[col].isnull().sum()
                if missing_count > 0:
                    missing_info[col] = {
                        'missing_count': int(missing_count),
                        'missing_percentage': float(missing_count / len(dataset) * 100)
                    }
            
            return {
                'success': True,
                'operation': 'missing_detection',
                'missing_info': missing_info,
                'total_missing': sum(info['missing_count'] for info in missing_info.values()),
                'operations_performed': operations_performed
            }
        
        elif operation == 'standardize':
            columns = parameters.get('columns', [])
            if not columns:
                columns = metadata.get('numeric_columns', [])
            
            for col in columns:
                if col in dataset.columns and pd.api.types.is_numeric_dtype(dataset[col]):
                    mean = dataset[col].mean()
                    std = dataset[col].std()
                    if std > 0:
                        result_dataset[col] = (dataset[col] - mean) / std
                        operations_performed.append(f"Standardized column '{col}'")
        
        elif operation == 'normalize':
            columns = parameters.get('columns', [])
            if not columns:
                columns = metadata.get('numeric_columns', [])
            
            for col in columns:
                if col in dataset.columns and pd.api.types.is_numeric_dtype(dataset[col]):
                    min_val = dataset[col].min()
                    max_val = dataset[col].max()
                    if max_val > min_val:
                        result_dataset[col] = (dataset[col] - min_val) / (max_val - min_val)
                        operations_performed.append(f"Normalized column '{col}' to [0,1] range")

        elif operation == 'comprehensive':
            # Run a sequence of safe cleaning steps: remove empty rows/cols, convert likely-numeric,
            # remove duplicates, then handle missing values using the provided method.
            method = parameters.get('method', 'mean')

            # Remove completely empty rows
            orig_rows = len(result_dataset)
            result_dataset = result_dataset.dropna(how='all')
            rows_removed = orig_rows - len(result_dataset)
            if rows_removed > 0:
                operations_performed.append(f"Removed {rows_removed} completely empty rows")

            # Remove completely empty columns
            orig_cols = len(result_dataset.columns)
            result_dataset = result_dataset.dropna(axis=1, how='all')
            cols_removed = orig_cols - len(result_dataset.columns)
            if cols_removed > 0:
                operations_performed.append(f"Removed {cols_removed} completely empty columns")

            # Convert object-like numeric columns when majority converts
            for col in list(result_dataset.columns):
                if result_dataset[col].dtype == 'object':
                    converted = pd.to_numeric(result_dataset[col], errors='coerce')
                    # avoid division by zero
                    if len(result_dataset) > 0 and (converted.notna().sum() / len(result_dataset)) > 0.8:
                        result_dataset[col] = converted
                        operations_performed.append(f"Converted column '{col}' to numeric")

            # Remove duplicates
            original_count = len(result_dataset)
            result_dataset = result_dataset.drop_duplicates()
            removed_count = original_count - len(result_dataset)
            if removed_count > 0:
                operations_performed.append(f"Removed {removed_count} duplicate rows")

            # Handle missing values using same logic as 'handle_missing'
            missing_cols = parameters.get('columns', [])
            if not missing_cols:
                missing_cols = result_dataset.columns[result_dataset.isnull().any()].tolist()

            for col in missing_cols:
                if col not in result_dataset.columns:
                    continue
                missing_count = result_dataset[col].isnull().sum()
                if missing_count == 0:
                    continue

                if pd.api.types.is_numeric_dtype(result_dataset[col]):
                    if method == 'mean':
                        fill_value = result_dataset[col].mean()
                    elif method == 'median':
                        fill_value = result_dataset[col].median()
                    elif method == 'mode':
                        fill_value = result_dataset[col].mode()[0] if not result_dataset[col].mode().empty else 0
                    elif method == 'zero':
                        fill_value = 0
                    else:
                        fill_value = result_dataset[col].mean()

                    # assign back to avoid SettingWithCopy issues
                    result_dataset[col] = result_dataset[col].fillna(fill_value)
                    operations_performed.append(f"Filled {missing_count} missing values in '{col}' with {method}")
                else:
                    if method == 'mode':
                        fill_value = result_dataset[col].mode()[0] if not result_dataset[col].mode().empty else 'Unknown'
                    else:
                        fill_value = 'Unknown'
                    result_dataset[col] = result_dataset[col].fillna(fill_value)
                    operations_performed.append(f"Filled {missing_count} missing values in '{col}' with '{fill_value}'")

            # If nothing was performed, explicitly report that no changes were necessary
            if not operations_performed:
                operations_performed.append('Checked for completely empty rows: none found')
                operations_performed.append('Checked for completely empty columns: none found')
                operations_performed.append('Checked for duplicate rows: none found')
                operations_performed.append('Checked for missing values: none found')
                operations_performed.append('Checked object columns for numeric conversion: no changes required')
        
        else:
            return {'success': False, 'error': f'Unsupported preprocessing operation: {operation}'}
        
        response = {
            'success': True,
            'operation': 'data_preprocessing',
            'operations_performed': operations_performed,
            'dataset_shape': result_dataset.shape,
            'original_shape': dataset.shape
        }

        if not operations_performed:
            if operation == 'handle_missing':
                response['message'] = '✅ No missing values found — preprocessing not required.'
            else:
                response['message'] = '✅ No preprocessing required. The dataset was checked and no missing values, duplicate records, or other issues requiring preprocessing were found.'

        # Attach processed dataset records when preprocessing actually changed the dataframe.
        # Keep operations_performed as the human-readable log, but do not require it to be non-empty
        # in order to include a processed dataset for a real transformation.
        try:
            changed = not result_dataset.equals(dataset)
            if changed:
                response['processed_dataset'] = result_dataset.where(pd.notnull(result_dataset), None).to_dict(orient='records')
        except Exception:
            pass

        return response
        
    except Exception as e:
        return {'success': False, 'error': f'Data preprocessing failed: {str(e)}'}


def clean_dataset(dataset: pd.DataFrame) -> Dict[str, Any]:
    """
    Perform basic dataset cleaning.
    - Remove completely empty rows
    - Remove completely empty columns
    - Handle obvious data types
    """
    try:
        if dataset is None or len(dataset) == 0:
            return {'success': False, 'error': 'Dataset is empty or not loaded'}
        
        result_dataset = dataset.copy()
        operations = []
        
        original_rows = len(result_dataset)
        original_cols = len(result_dataset.columns)
        
        # Remove completely empty rows
        result_dataset.dropna(how='all', inplace=True)
        rows_removed = original_rows - len(result_dataset)
        if rows_removed > 0:
            operations.append(f"Removed {rows_removed} completely empty rows")
        
        # Remove completely empty columns
        result_dataset.dropna(axis=1, how='all', inplace=True)
        cols_removed = original_cols - len(result_dataset.columns)
        if cols_removed > 0:
            operations.append(f"Removed {cols_removed} completely empty columns")
        
        # Convert obvious numeric columns
        for col in result_dataset.columns:
            if result_dataset[col].dtype == 'object':
                # Try to convert to numeric
                try:
                    converted = pd.to_numeric(result_dataset[col], errors='coerce')
                    # If conversion was mostly successful
                    if converted.notna().sum() / len(result_dataset) > 0.8:
                        result_dataset[col] = converted
                        operations.append(f"Converted column '{col}' to numeric")
                except:
                    pass
        
        return {
            'success': True,
            'operation': 'clean_dataset',
            'operations': operations,
            'final_shape': result_dataset.shape,
            'original_shape': (original_rows, original_cols)
        }
        
    except Exception as e:
        return {'success': False, 'error': f'Dataset cleaning failed: {str(e)}'}