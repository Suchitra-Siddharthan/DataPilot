from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
import sys
import os
import re

# Handle both relative and absolute imports
try:
    from .state import agent_state
    from .tool_registry import tool_registry
except ImportError:
    from agent.state import agent_state
    from agent.tool_registry import tool_registry

try:
    from ..data.dataset_manager import dataset_manager
    from ..ml.intent_classifier import intent_classifier
except ImportError:
    from data.dataset_manager import dataset_manager
    from ml.intent_classifier import intent_classifier

class DataPilotAgent:
    """ReAct-style AI Agent for data analysis"""
    
    def __init__(self):
        self.state = agent_state
        self.tool_registry = tool_registry
        self.dataset_manager = dataset_manager
        self.intent_classifier = intent_classifier
        if not self.tool_registry.tools:
            try:
                from .tools.register_tools import register_all_tools
            except ImportError:
                from agent.tools.register_tools import register_all_tools
            register_all_tools()
    
    def analyze(self, question: str) -> Dict[str, Any]:
        """Main analysis pipeline - ReAct loop"""
        self.state.reset()
        self.state.start_time = pd.Timestamp.now().isoformat()
        
        try:
            # STEP 1: OBSERVE - Get initial observation
            observation = self._observe(question)
            self.state.update_observation(observation)
            
            # STEP 2: INTERPRET - Get intent from ML classifier
            intent_result = self._interpret_question(question)
            self.state.set_intent(intent_result['intent'], intent_result['confidence'])
            
            # STEP 3: SELECT TOOL - Agent reasoning
            tool_selection = self._select_tool(intent_result['intent'], question)
            
            if not tool_selection['success']:
                return self._handle_error(tool_selection['error'])
            
            self.state.set_candidate_tools(tool_selection['candidate_tools'])
            self.state.select_tool(tool_selection['selected_tool'], tool_selection['parameters'])
            
            # STEP 4: ACT - Execute tool
            action_result = self._execute_tool(tool_selection['selected_tool'], tool_selection['parameters'])
            self.state.set_action_result(action_result)
            
            if not action_result['success']:
                return self._handle_error(action_result['error'])
            
            # STEP 5: VALIDATE - Validate result
            validation_result = self._validate_result(action_result['result'])
            self.state.set_validation_result(validation_result)
            
            # STEP 6: RESPOND - Generate final response
            final_response = self._generate_response(question, action_result['result'], validation_result)
            self.state.set_final_response(final_response)
            
            self.state.end_time = pd.Timestamp.now().isoformat()
            
            return {
                'success': True,
                'question': question,
                'intent': intent_result['intent'],
                'confidence': float(intent_result['confidence']),
                'selected_tool': tool_selection['selected_tool'],
                'result': self._make_json_serializable(action_result['result']),
                'validation': validation_result,
                'explanation': final_response['explanation'],
                'trace': self.state.get_trace()
            }
            
        except Exception as e:
            error_msg = f"Agent analysis failed: {str(e)}"
            self.state.set_error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'trace': self.state.get_trace()
            }
    
    def _observe(self, question: str) -> Dict[str, Any]:
        """Observe current state and environment"""
        dataset = self.dataset_manager.get_dataset()
        metadata = self.dataset_manager.get_metadata()
        
        if dataset is None:
            return {
                'dataset_loaded': False,
                'error': 'No dataset loaded'
            }
        
        self.state.set_dataset_metadata(metadata)
        
        return {
            'dataset_loaded': True,
            'rows': metadata['rows'],
            'columns': metadata['columns'],
            'numeric_columns': metadata['numeric_columns'],
            'categorical_columns': metadata['categorical_columns'],
            'question': question
        }
    
    def _interpret_question(self, question: str) -> Dict[str, Any]:
        """Use ML classifier to interpret question intent with validation layer"""
        # Get SVM prediction
        svm_prediction = self.intent_classifier.predict(question)
        
        # Apply validation layer for obvious patterns
        validated_intent = self._validate_intent_pattern(question, svm_prediction['intent'])
        
        # If validation changed the intent, update the prediction
        if validated_intent != svm_prediction['intent']:
            original_intent = svm_prediction['intent']
            print(f"Intent validation: SVM predicted '{original_intent}', validated to '{validated_intent}'")
            svm_prediction['original_svm_intent'] = original_intent
            svm_prediction['intent'] = validated_intent
            svm_prediction['validation_override'] = True
        
        return svm_prediction
    
    def _validate_intent_pattern(self, question: str, svm_intent: str) -> str:
        """
        Safe validation layer to route obvious questions to correct tools.
        This preserves SVM predictions while handling clear-cut cases.
        """
        question_lower = question.lower()
        
        # Strong correlation indicators
        correlation_keywords = ['correlation', 'correlate', 'relationship', 'related', 'associated', 'connection']
        correlation_between = ['between', 'vs', 'versus', 'and']
        
        # Check for correlation questions
        if (any(keyword in question_lower for keyword in correlation_keywords) and 
            any(keyword in question_lower for keyword in correlation_between)):
            return 'correlation_analysis'
        
        # Strong outlier detection indicators  
        outlier_keywords = ['outlier', 'unusual', 'anomaly', 'anomalies', 'abnormal', 'extreme', 'outliers']
        detect_keywords = ['detect', 'find', 'identify', 'spot', 'locate']
        
        # Check for outlier detection questions
        if (any(keyword in question_lower for keyword in outlier_keywords) and 
            any(keyword in question_lower for keyword in detect_keywords)):
            return 'outlier_detection'
        
        # Distribution indicators (higher priority than summary)
        distribution_keywords = ['distribution', 'distributed', 'distribute', 'histogram', 'spread',
                                 'skewness', 'kurtosis', 'iqr', 'quartile', 'quartiles', 'q1', 'q3', 'range', 'distribution statistics']
        if any(keyword in question_lower for keyword in distribution_keywords):
            if svm_intent != 'distribution_analysis':
                return 'distribution_analysis'
        
        # Feature engineering indicators
        feature_keywords = ['create', 'make', 'transform', 'new column', 'new feature', 'add column']
        if (any(keyword in question_lower for keyword in feature_keywords) and 
            svm_intent != 'feature_engineering'):
            # But not if it's clearly about summary statistics
            summary_specific = ['average', 'mean', 'median', 'sum of', 'total of']
            if not any(keyword in question_lower for keyword in summary_specific):
                return 'feature_engineering'
        
        # Summary statistics indicators (most specific)
        # Include 'summary' and 'statistics' to catch explicit requests
        summary_keywords = ['summary', 'statistics', 'average', 'mean', 'median', 'minimum', 'maximum', 'std', 'standard deviation']
        if any(keyword in question_lower for keyword in summary_keywords):
            if svm_intent != 'summary_statistics':
                return 'summary_statistics'
        
        # Preserve SVM prediction for other cases
        return svm_intent
    
    def _select_tool(self, intent: str, question: str = '') -> Dict[str, Any]:
        """Agent reasoning to select appropriate tool"""
        # Get candidate tools for intent
        candidate_tools = self.tool_registry.get_tools_for_intent(intent)
        
        if not candidate_tools:
            return {
                'success': False,
                'error': f'No tools available for intent: {intent}'
            }
        
        # Prefer the primary analysis tool over visualization helpers
        selected_tool = candidate_tools[0]
        if selected_tool == 'create_visualization' and len(candidate_tools) > 1:
            selected_tool = next((t for t in candidate_tools if t != 'create_visualization'), selected_tool)
        
        # Agent reasoning: check dataset compatibility
        metadata = self.dataset_manager.get_metadata()

        parameters = self._extract_parameters(intent, metadata, question)

        if selected_tool == 'correlation_analysis' and parameters.get('unavailable_columns'):
            unavailable = ', '.join(parameters['unavailable_columns'])
            return {
                'success': False,
                'error': f'Correlation request references unavailable column(s): {unavailable}'
            }

        # Validate tool compatibility with dataset
        validation = self._validate_tool_selection(selected_tool, parameters, metadata)
        
        if not validation['valid']:
            return {
                'success': False,
                'error': validation['reason']
            }
        
        return {
            'success': True,
            'candidate_tools': candidate_tools,
            'selected_tool': selected_tool,
            'parameters': parameters
        }
    
    def _normalize_column_name(self, value: str) -> str:
        """Normalize column names for safe, case-insensitive matching."""
        if value is None:
            return ''
        return re.sub(r'[^a-z0-9]+', ' ', str(value).lower()).strip()

    def _extract_explicit_columns(self, question: str, column_names: list[str]) -> list[str]:
        """Return only actual dataset columns explicitly named by the user."""
        if not question or not column_names:
            return []

        normalized_question = re.sub(r'[^a-z0-9]+', ' ', str(question).lower())
        question_tokens = [token for token in normalized_question.split() if token]
        if not question_tokens:
            return []

        requested = []
        seen = set()
        for col in column_names:
            normalized_col = self._normalize_column_name(col)
            if not normalized_col:
                continue

            col_tokens = [token for token in normalized_col.split() if token]
            if not col_tokens:
                continue

            found = False
            for start in range(len(question_tokens) - len(col_tokens) + 1):
                if question_tokens[start:start + len(col_tokens)] == col_tokens:
                    found = True
                    break

            if found and col not in seen:
                requested.append(col)
                seen.add(col)

        return requested

    def _extract_parameters(self, intent: str, metadata: Dict[str, Any],
                            question: str = '') -> Dict[str, Any]:
        """Extract parameters for tool execution based on intent and metadata"""
        # Convert metadata to JSON-serializable format
        clean_metadata = self._make_json_serializable(metadata) if metadata else {}
        
        parameters = {
            'dataset': self.dataset_manager.get_dataset(),
            'metadata': clean_metadata
        }
        
        # Intent-specific parameter extraction
        if intent == 'summary_statistics':
            numeric_cols = clean_metadata.get('numeric_columns', [])
            explicit_columns = self._extract_explicit_columns(question, numeric_cols)
            if explicit_columns:
                parameters['columns'] = explicit_columns
            elif numeric_cols:
                parameters['columns'] = numeric_cols
        
        elif intent == 'correlation_analysis':
            numeric_cols = clean_metadata.get('numeric_columns', []) or []
            column_names = clean_metadata.get('column_names', []) or numeric_cols
            explicit_columns = self._extract_explicit_columns(question, column_names)
            if explicit_columns:
                parameters['columns'] = [col for col in explicit_columns if col in numeric_cols] or explicit_columns
            elif len(numeric_cols) >= 2:
                parameters['columns'] = numeric_cols
        
        elif intent == 'distribution_analysis':
            numeric_cols = clean_metadata.get('numeric_columns', [])
            explicit_columns = self._extract_explicit_columns(question, numeric_cols)
            if explicit_columns:
                parameters['columns'] = explicit_columns
            elif numeric_cols:
                parameters['columns'] = numeric_cols
        
        elif intent == 'outlier_detection':
            numeric_cols = clean_metadata.get('numeric_columns', [])
            explicit_columns = self._extract_explicit_columns(question, numeric_cols)
            if explicit_columns:
                parameters['columns'] = explicit_columns
            elif numeric_cols:
                parameters['columns'] = numeric_cols
        
        elif intent == 'feature_engineering':
            parameters.update(self._feature_engineering_params(question, clean_metadata))
        
        elif intent == 'data_preprocessing':
            parameters.update(self._preprocessing_params(question, clean_metadata))
        
        return parameters

    def _feature_engineering_params(self, question: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Choose a supported feature-engineering operation from the question."""
        q = (question or '').lower()
        numeric_cols = metadata.get('numeric_columns', []) or []
        column_names = metadata.get('column_names', []) or numeric_cols
        age_col = next((c for c in column_names if 'age' in str(c).lower()), None)
        # Heuristic: detect "X per Y" patterns (e.g. "salary per year of experience")
        if ' per ' in q or 'per ' in q:
            # Try to map common numerator/denominator keywords to actual columns
            num_candidates = [c for c in column_names if any(k in str(c).lower() for k in ['salary', 'pay', 'compensation', 'wage', 'income', 'annual', 'salary_usd'])]
            den_candidates = [c for c in column_names if any(k in str(c).lower() for k in ['experience', 'years', 'tenure', 'service', 'seniority'])]
            # If the question itself mentions the words, prefer those
            if 'salary' in q and 'experience' in q:
                # try to pick explicit matches first
                if num_candidates and den_candidates:
                    return {
                        'operation': 'create_ratio',
                        'parameters': {
                            'numerator': num_candidates[0],
                            'denominator': den_candidates[0]
                        }
                    }
            # Generic per-* phrasing: if we have reasonable numeric candidates, use them
            if num_candidates and den_candidates:
                return {
                    'operation': 'create_ratio',
                    'parameters': {
                        'numerator': num_candidates[0],
                        'denominator': den_candidates[0]
                    }
                }

        if any(k in q for k in ['age group', 'age_group', 'age groups']):
            return {
                'operation': 'create_age_group',
                'parameters': {'column': age_col or 'age'}
            }
        # Also treat explicit "per"/"ratio" words
        if 'ratio' in q and len(numeric_cols) >= 2:
            return {
                'operation': 'create_ratio',
                'parameters': {
                    'numerator': numeric_cols[0],
                    'denominator': numeric_cols[1]
                }
            }
        if 'sum' in q and len(numeric_cols) >= 2:
            return {
                'operation': 'create_sum',
                'parameters': {'columns': numeric_cols[:2], 'new_column': 'sum_column'}
            }
        if 'bin' in q and numeric_cols:
            return {
                'operation': 'bin_column',
                'parameters': {'column': numeric_cols[0]}
            }
        if age_col:
            return {
                'operation': 'create_age_group',
                'parameters': {'column': age_col}
            }
        if len(numeric_cols) >= 2:
            return {
                'operation': 'create_sum',
                'parameters': {'columns': numeric_cols[:2], 'new_column': 'sum_column'}
            }
        if numeric_cols:
            return {
                'operation': 'bin_column',
                'parameters': {'column': numeric_cols[0]}
            }
        return {'operation': 'create_sum', 'parameters': {'columns': numeric_cols}}

    def _preprocessing_params(self, question: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Choose a supported preprocessing operation from the question."""
        q = (question or '').lower()
        # If user requests comprehensive preprocessing, ask the preprocessing tool
        # to run the full pipeline (cleaning, duplicates, missing handling).
        if 'comprehens' in q or 'comprehensive' in q:
            return {'operation': 'comprehensive', 'parameters': {'method': 'mean'}}
        if 'duplicate' in q:
            return {'operation': 'remove_duplicates'}
        if 'standard' in q:
            return {'operation': 'standardize'}
        if 'normal' in q:
            return {'operation': 'normalize'}
        if 'type' in q:
            return {'operation': 'inspect_types'}
        if any(k in q for k in ['missing', 'clean', 'preprocess', 'prepare']):
            return {'operation': 'handle_missing', 'parameters': {'method': 'mean'}}
        missing = metadata.get('missing_values') or {}
        if any((v or 0) > 0 for v in missing.values()):
            return {'operation': 'handle_missing', 'parameters': {'method': 'mean'}}
        return {'operation': 'inspect_types'}
    
    def _make_json_serializable(self, obj):
        """Convert numpy/pandas types to JSON-safe Python natives"""
        if obj is None:
            return None
        if isinstance(obj, dict):
            return {str(k): self._make_json_serializable(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [self._make_json_serializable(item) for item in obj]
        if isinstance(obj, pd.DataFrame):
            return None
        if isinstance(obj, pd.Series):
            return self._make_json_serializable(obj.tolist())
        if isinstance(obj, np.ndarray):
            return self._make_json_serializable(obj.tolist())
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            val = float(obj)
            if np.isnan(val) or np.isinf(val):
                return None
            return val
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
            return None
        return obj
    
    def _validate_tool_selection(self, tool_name: str, parameters: Dict[str, Any], 
                                  metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that selected tool can work with current dataset"""
        # Check if dataset exists
        if parameters.get('dataset') is None:
            return {
                'valid': False,
                'reason': 'No dataset available for analysis'
            }
        
        # Intent-specific validation
        if tool_name in ['correlation_analysis', 'machine_learning']:
            numeric_cols = metadata.get('numeric_columns', [])
            if len(numeric_cols) < 2:
                return {
                    'valid': False,
                    'reason': f'{tool_name} requires at least 2 numerical columns, found {len(numeric_cols)}'
                }
        
        if tool_name == 'machine_learning':
            # Check for sufficient data
            if metadata.get('rows', 0) < 10:
                return {
                    'valid': False,
                    'reason': 'Machine learning requires at least 10 rows of data'
                }
        
        return {
            'valid': True,
            'reason': 'Tool selection validated'
        }
    
    def _execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the selected tool"""
        tool = self.tool_registry.get_tool(tool_name)
        
        if tool is None:
            return {
                'success': False,
                'error': f'Tool not found: {tool_name}'
            }
        
        return tool.execute(**parameters)
    
    def _validate_result(self, result: Any) -> Dict[str, Any]:
        """Validate the analysis result"""
        if result is None:
            return {
                'success': False,
                'message': 'Analysis returned no result'
            }
        
        if isinstance(result, dict) and 'error' in result:
            return {
                'success': False,
                'message': result['error']
            }
        
        return {
            'success': True,
            'message': 'Result validated successfully'
        }
    
    def _generate_response(self, question: str, result: Any, 
                           validation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate human-readable explanation"""
        if not validation['success']:
            return {
                'explanation': f"Analysis could not be completed: {validation['message']}",
                'result': None
            }
        
        # Generate explanation based on result
        if isinstance(result, dict):
            explanation = self._explain_result(result)
        else:
            explanation = "Analysis completed successfully. See results for details."
        
        return {
            'explanation': explanation,
            'result': result
        }
    
    def _explain_result(self, result: Dict[str, Any]) -> str:
        """Generate explanation from result dictionary"""
        explanations = []
        
        if 'operation' in result:
            explanations.append(f"Operation: {result['operation']}")
        
        if 'value' in result:
            explanations.append(f"Result: {result['value']}")
        
        if 'interpretation' in result:
            explanations.append(f"Interpretation: {result['interpretation']}")
        
        if 'statistics' in result:
            explanations.append("Statistics computed successfully")
        
        return '. '.join(explanations) if explanations else "Analysis completed"
    
    def _handle_error(self, error: str) -> Dict[str, Any]:
        """Handle error during analysis"""
        self.state.set_error(error)
        return {
            'success': False,
            'error': error,
            'trace': self.state.get_trace()
        }


# Global instance
datapilot_agent = DataPilotAgent()