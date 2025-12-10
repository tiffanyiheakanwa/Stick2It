"""
Simple Flask API for Procrastination Predictions
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from predict import ProcrastinationPredictor
import traceback
from recommender import AdaptiveRecommender
from progress import ProgressTracker



app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Initialize predictor (load model once at startup)
try:
    predictor = ProcrastinationPredictor()
    print("✅ Prediction model loaded")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    predictor = None

# Initialize (add after predictor)
try:
    recommender = AdaptiveRecommender()
    progress_tracker = ProgressTracker()
    print("✅ Recommender and tracker loaded")
except Exception as e:
    print(f"❌ Error: {e}")
    recommender = None
    progress_tracker = None

# Add these new routes

@app.route('/recommendations/<int:student_id>', methods=['GET'])
def get_recommendations(student_id):
    """Get personalized recommendations"""
    if not recommender:
        return jsonify({'error': 'Recommender not loaded'}), 500
    
    try:
        limit = request.args.get('limit', 5, type=int)
        result = recommender.recommend(student_id, limit=limit)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/progress/start', methods=['POST'])
def start_content():
    """Mark content as started"""
    if not progress_tracker:
        return jsonify({'error': 'Tracker not loaded'}), 500
    
    try:
        data = request.get_json()
        student_id = data['student_id']
        content_id = data['content_id']
        
        result = progress_tracker.start_content(student_id, content_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/progress/complete', methods=['POST'])
def complete_content():
    """Mark content as completed"""
    if not progress_tracker:
        return jsonify({'error': 'Tracker not loaded'}), 500
    
    try:
        data = request.get_json()
        student_id = data['student_id']
        content_id = data['content_id']
        time_spent = data.get('time_spent', 0)
        
        result = progress_tracker.complete_content(student_id, content_id, time_spent)
        
        # Get fresh recommendations after completion
        new_recs = recommender.recommend(student_id, limit=5)
        result['new_recommendations'] = new_recs
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/progress/<int:student_id>', methods=['GET'])
def get_progress(student_id):
    """Get student progress stats"""
    if not progress_tracker:
        return jsonify({'error': 'Tracker not loaded'}), 500
    
    try:
        stats = progress_tracker.get_stats(student_id)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500    

@app.route('/', methods=['GET'])
def home():
    """API health check"""
    return jsonify({
        'status': 'online',
        'message': 'Procrastination Prediction API',
        'version': '1.0',
        'model_loaded': predictor is not None
    })

@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict procrastination risk from features
    
    Request body (JSON):
    {
        "last_minute_ratio": 0.6,
        "engagement_intensity": 15.5,
        "deadline_pressure": 2.5,
        "login_consistency": 1.2,
        "early_starter": 0,
        "completion_rate": 0.4,
        "activity_span": 45.0
    }
    """
    if not predictor:
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        # Get features from request
        features = request.get_json()
        
        # Validate required features
        required_features = [
            'last_minute_ratio', 'engagement_intensity', 'deadline_pressure',
            'login_consistency', 'early_starter', 'completion_rate', 'activity_span'
        ]
        
        for feature in required_features:
            if feature not in features:
                return jsonify({'error': f'Missing required feature: {feature}'}), 400
        
        # Make prediction
        result = predictor.predict_risk(features)
        
        return jsonify({
            'success': True,
            'prediction': result
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/predict/<int:student_id>', methods=['GET'])
def predict_student(student_id):
    """
    Predict risk for a student from database
    
    Example: GET /predict/11391
    """
    if not predictor:
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        result = predictor.predict_from_database(student_id)
        
        return jsonify({
            'success': True,
            'student_id': student_id,
            'prediction': result
        })
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/batch-predict', methods=['POST'])
def batch_predict():
    """
    Predict for multiple students at once
    
    Request body (JSON):
    {
        "student_ids": [11391, 28400, 30268]
    }
    """
    if not predictor:
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        data = request.get_json()
        student_ids = data.get('student_ids', [])
        
        if not student_ids:
            return jsonify({'error': 'No student_ids provided'}), 400
        
        results = []
        for student_id in student_ids:
            try:
                prediction = predictor.predict_from_database(student_id)
                results.append({
                    'student_id': student_id,
                    'success': True,
                    'prediction': prediction
                })
            except Exception as e:
                results.append({
                    'student_id': student_id,
                    'success': False,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'results': results,
            'total': len(results)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("\n🚀 Starting Procrastination Prediction API...")
    print("📍 API will be available at: http://localhost:5000")
    print("\nEndpoints:")
    print("  GET  /                    - Health check")
    print("  POST /predict             - Predict from features")
    print("  GET  /predict/<student_id> - Predict from database")
    print("  POST /batch-predict       - Batch predictions")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)