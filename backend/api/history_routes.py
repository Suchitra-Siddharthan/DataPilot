from flask import Blueprint, request, jsonify
from datetime import datetime
import uuid

history_bp = Blueprint('history', __name__)

# In-memory history storage (in production, use a database)
analysis_history = []

@history_bp.route('', methods=['GET'])
def get_history():
    """Get analysis history"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        # Return most recent analyses
        recent_history = sorted(analysis_history, key=lambda x: x['timestamp'], reverse=True)[:limit]
        
        return jsonify({
            'success': True,
            'history': recent_history,
            'total': len(analysis_history)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get history: {str(e)}'}), 500

@history_bp.route('/<history_id>', methods=['GET'])
def get_history_item(history_id):
    """Get specific history item"""
    try:
        for item in analysis_history:
            if item['id'] == history_id:
                return jsonify({
                    'success': True,
                    'item': item
                }), 200
        
        return jsonify({'success': False, 'error': 'History item not found'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get history item: {str(e)}'}), 500

@history_bp.route('', methods=['POST'])
def save_to_history():
    """Save analysis to history"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Create history item
        history_item = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'question': data.get('question'),
            'intent': data.get('intent'),
            'selected_tool': data.get('selected_tool'),
            'result': data.get('result'),
            'explanation': data.get('explanation'),
            'validation': data.get('validation'),
            'trace': data.get('trace', [])
        }
        
        analysis_history.append(history_item)
        
        return jsonify({
            'success': True,
            'id': history_item['id'],
            'message': 'Analysis saved to history'
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to save to history: {str(e)}'}), 500

@history_bp.route('/<history_id>', methods=['DELETE'])
def delete_history_item(history_id):
    """Delete specific history item"""
    try:
        global analysis_history
        original_count = len(analysis_history)
        
        analysis_history = [item for item in analysis_history if item['id'] != history_id]
        
        if len(analysis_history) < original_count:
            return jsonify({
                'success': True,
                'message': 'History item deleted'
            }), 200
        else:
            return jsonify({'success': False, 'error': 'History item not found'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to delete history item: {str(e)}'}), 500

@history_bp.route('/clear', methods=['DELETE'])
def clear_history():
    """Clear all history"""
    try:
        global analysis_history
        count = len(analysis_history)
        analysis_history = []
        
        return jsonify({
            'success': True,
            'message': f'Cleared {count} history items'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to clear history: {str(e)}'}), 500