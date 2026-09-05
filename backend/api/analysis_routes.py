from flask import Blueprint, request, jsonify

try:
    from ..agent.agent import datapilot_agent
    from ..ml.intent_classifier import intent_classifier
    from ..data.dataset_manager import dataset_manager
except ImportError:
    from agent.agent import datapilot_agent
    from ml.intent_classifier import intent_classifier
    from data.dataset_manager import dataset_manager

analysis_bp = Blueprint('analysis', __name__)

# Note: ML classifier is initialized in app.py

@analysis_bp.route('', methods=['POST'])
def analyze():
    """Perform natural language data analysis"""
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({'success': False, 'error': 'No question provided'}), 400
        
        question = data['question']
        
        # Check if dataset is loaded
        if dataset_manager.get_dataset() is None:
            return jsonify({
                'success': False,
                'error': 'No dataset loaded. Please upload a dataset first.'
            }), 400
        
        # Perform analysis using the agent
        result = datapilot_agent.analyze(question)
        
        if result['success']:
            # Include both legacy keys (tool/answer) and frontend keys (selected_tool/explanation)
            return jsonify({
                'success': True,
                'question': result['question'],
                'intent': result['intent'],
                'tool': result['selected_tool'],
                'selected_tool': result['selected_tool'],
                'answer': result['explanation'],
                'explanation': result['explanation'],
                'status': 'success',
                'confidence': result['confidence'],
                'result': result['result'],
                'validation': result['validation'],
                'trace': result['trace']
            }), 200
        else:
            return jsonify({
                'success': False,
                'status': 'error',
                'error': result['error'],
                'trace': result.get('trace', [])
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'error',
            'error': f'Analysis failed: {str(e)}'
        }), 500

@analysis_bp.route('/intents', methods=['GET'])
def get_intents():
    """Get available intents"""
    try:
        intents = intent_classifier.get_intents()
        return jsonify({
            'success': True,
            'intents': intents
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get intents: {str(e)}'}), 500

@analysis_bp.route('/predict_intent', methods=['POST'])
def predict_intent_only():
    """Predict intent without performing full analysis"""
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({'success': False, 'error': 'No question provided'}), 400
        
        question = data['question']
        prediction = intent_classifier.predict(question)
        
        return jsonify({
            'success': True,
            'prediction': prediction
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Intent prediction failed: {str(e)}'}), 500

@analysis_bp.route('/tools', methods=['GET'])
def get_tools():
    """Get available analysis tools"""
    try:
        try:
            from ..agent.tool_registry import tool_registry
        except ImportError:
            from agent.tool_registry import tool_registry
        
        tools = tool_registry.list_tools()
        return jsonify({
            'success': True,
            'tools': tools
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get tools: {str(e)}'}), 500