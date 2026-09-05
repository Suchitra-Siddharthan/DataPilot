from flask import Blueprint, request, jsonify
import os
import pandas as pd
from werkzeug.utils import secure_filename

try:
    from ..data.dataset_manager import dataset_manager
except ImportError:
    from data.dataset_manager import dataset_manager

dataset_bp = Blueprint('dataset', __name__)

# Configuration
ALLOWED_EXTENSIONS = {'csv'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Get upload folder from environment or use default
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(os.path.dirname(__file__), '..', 'uploads'))

# Ensure upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@dataset_bp.route('/upload', methods=['POST'])
def upload_dataset():
    """Upload CSV dataset"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Only CSV files are allowed'}), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'success': False, 'error': 'File size exceeds 16MB limit'}), 400
        
        # Secure filename
        filename = secure_filename(file.filename)
        
        # Save file with absolute path
        filepath = os.path.abspath(os.path.join(UPLOAD_FOLDER, filename))
        file.save(filepath)
        
        # Load dataset
        result = dataset_manager.load_dataset(filepath)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Upload failed: {str(e)}'}), 500

@dataset_bp.route('/info', methods=['GET'])
def get_dataset_info():
    """Get current dataset information"""
    try:
        metadata = dataset_manager.get_metadata()
        
        if metadata is None:
            return jsonify({'success': False, 'error': 'No dataset loaded'}), 404
        
        return jsonify({
            'success': True,
            'metadata': metadata,
            'dataset_id': dataset_manager.dataset_id
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get dataset info: {str(e)}'}), 500

@dataset_bp.route('/preview', methods=['GET'])
def get_dataset_preview():
    """Get dataset preview"""
    try:
        n_rows = request.args.get('rows', 10, type=int)
        result = dataset_manager.get_preview(n_rows)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get preview: {str(e)}'}), 500

@dataset_bp.route('/clear', methods=['POST'])
def clear_dataset():
    """Clear current dataset"""
    try:
        dataset_manager.clear_dataset()
        return jsonify({'success': True, 'message': 'Dataset cleared'}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to clear dataset: {str(e)}'}), 500

@dataset_bp.route('/columns', methods=['GET'])
def get_columns():
    """Get column information"""
    try:
        metadata = dataset_manager.get_metadata()
        
        if metadata is None:
            return jsonify({'success': False, 'error': 'No dataset loaded'}), 404
        
        return jsonify({
            'success': True,
            'columns': metadata.get('column_names', []),
            'numeric_columns': metadata.get('numeric_columns', []),
            'categorical_columns': metadata.get('categorical_columns', []),
            'datetime_columns': metadata.get('datetime_columns', [])
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get columns: {str(e)}'}), 500