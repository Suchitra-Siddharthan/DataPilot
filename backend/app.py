from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.dataset_routes import dataset_bp
from api.analysis_routes import analysis_bp
from api.history_routes import history_bp
from agent.tools.register_tools import register_all_tools
from ml.intent_classifier import intent_classifier
from data.dataset_manager import dataset_manager

app = Flask(__name__)
CORS(app)

# Create upload directory if it doesn't exist
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize tools and ML model
register_all_tools()
model_loaded = intent_classifier.load_model()

if model_loaded:
    print("SUCCESS: ML model loaded successfully")
else:
    print("WARNING: ML model not loaded, using fallback predictions")

# Register blueprints
app.register_blueprint(dataset_bp, url_prefix='/api/dataset')
app.register_blueprint(analysis_bp, url_prefix='/api/analyze')
app.register_blueprint(history_bp, url_prefix='/api/history')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'DataPilot API is running'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)