"""
AutoAssess - Main Flask Application
Autonomous Programming Assignment Evaluation System
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import threading
import os
from datetime import datetime

from config import Config
from utils.db_connection import db
from services.drive_monitor import DriveMonitor
from services.evaluator import AssignmentEvaluator
from services.report_generator import ReportGenerator

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize services
drive_monitor = DriveMonitor()
evaluator = AssignmentEvaluator()
report_generator = ReportGenerator()

# Global monitoring state
monitoring_thread = None
monitoring_active = False

# Validate configuration on startup
Config.validate()

# ============================================================================
# ROOT ENDPOINT & FRONTEND
# ============================================================================

@app.route('/')
def index():
    """Serve the frontend dashboard"""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'index.html')
    return send_file(frontend_path)

@app.route('/css/<path:filename>')
def serve_css(filename):
    """Serve CSS files"""
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'css', filename)
    return send_file(css_path)

@app.route('/js/<path:filename>')
def serve_js(filename):
    """Serve JavaScript files"""
    js_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'js', filename)
    return send_file(js_path)

@app.route('/api')
def api_info():
    """API information endpoint"""
    return jsonify({
        'message': 'AutoAssess API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'submissions': '/api/submissions',
            'monitoring': '/api/monitor',
            'reports': '/api/reports',
            'statistics': '/api/stats'
        }
    })

# ============================================================================
# SUBMISSIONS ENDPOINTS
# ============================================================================

@app.route('/api/submissions', methods=['GET'])
def get_submissions():
    """Get all submissions with optional filtering"""
    try:
        # Get query parameters
        status = request.args.get('status')
        student_id = request.args.get('student_id')
        limit = int(request.args.get('limit', 100))
        
        # Build query
        query = {}
        if status:
            query['status'] = status
        if student_id:
            query['student_id'] = student_id
        
        # Fetch from database
        submissions = list(db.submissions.find(query).sort('submitted_at', -1).limit(limit))
        
        # Convert ObjectId to string and remove bytes fields
        for sub in submissions:
            sub['_id'] = str(sub['_id'])
            # Remove file_content if it's bytes
            if 'file_content' in sub and isinstance(sub['file_content'], bytes):
                sub['file_content'] = sub['file_content'].decode('utf-8', errors='ignore')[:500]
        
        return jsonify({
            'success': True,
            'count': len(submissions),
            'submissions': submissions
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/submissions/<submission_id>', methods=['GET'])
def get_submission(submission_id):
    """Get specific submission by ID"""
    try:
        from bson.objectid import ObjectId
        
        submission = db.submissions.find_one({'_id': ObjectId(submission_id)})
        
        if not submission:
            return jsonify({
                'success': False,
                'error': 'Submission not found'
            }), 404
        
        submission['_id'] = str(submission['_id'])
        
        # Remove or convert bytes fields
        if 'file_content' in submission and isinstance(submission['file_content'], bytes):
            submission['file_content'] = submission['file_content'].decode('utf-8', errors='ignore')[:500]
        
        return jsonify({
            'success': True,
            'submission': submission
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/submissions/<submission_id>/evaluate', methods=['POST'])
def evaluate_submission(submission_id):
    """Manually trigger evaluation for a submission"""
    try:
        from bson.objectid import ObjectId
        
        submission = db.submissions.find_one({'_id': ObjectId(submission_id)})
        
        if not submission:
            return jsonify({
                'success': False,
                'error': 'Submission not found'
            }), 404
        
        # Evaluate the submission
        assessment = evaluator.evaluate(submission)
        
        # Update submission with assessment
        db.submissions.update_one(
            {'_id': ObjectId(submission_id)},
            {
                '$set': {
                    'assessment': assessment,
                    'status': 'evaluated',
                    'evaluated_at': datetime.utcnow()
                }
            }
        )
        
        return jsonify({
            'success': True,
            'message': 'Evaluation completed',
            'assessment': assessment
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# MONITORING ENDPOINTS
# ============================================================================

@app.route('/api/monitor/start', methods=['POST'])
def start_monitoring():
    """Start Google Drive monitoring"""
    global monitoring_thread, monitoring_active
    
    try:
        if monitoring_active:
            return jsonify({
                'success': False,
                'message': 'Monitoring is already active'
            })
        
        monitoring_active = True
        monitoring_thread = threading.Thread(target=drive_monitor.start_monitoring)
        monitoring_thread.daemon = True
        monitoring_thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Monitoring started successfully'
        })
    
    except Exception as e:
        monitoring_active = False
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/monitor/stop', methods=['POST'])
def stop_monitoring():
    """Stop Google Drive monitoring"""
    global monitoring_active
    
    try:
        if not monitoring_active:
            return jsonify({
                'success': False,
                'message': 'Monitoring is not active'
            })
        
        monitoring_active = False
        drive_monitor.stop_monitoring()
        
        return jsonify({
            'success': True,
            'message': 'Monitoring stopped successfully'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/monitor/status', methods=['GET'])
def get_monitor_status():
    """Get monitoring status"""
    return jsonify({
        'success': True,
        'monitoring_active': monitoring_active,
        'last_check': drive_monitor.last_check_time,
        'files_processed': drive_monitor.files_processed
    })

# ============================================================================
# REPORTS ENDPOINTS
# ============================================================================

@app.route('/api/reports/individual/<submission_id>', methods=['GET'])
def generate_individual_report(submission_id):
    """Generate individual assessment report
    
    Query params:
        format: 'pdf' or 'txt' (default: 'pdf')
    """
    try:
        from bson.objectid import ObjectId
        
        submission = db.submissions.find_one({'_id': ObjectId(submission_id)})
        
        if not submission:
            return jsonify({
                'success': False,
                'error': 'Submission not found'
            }), 404
        
        if submission.get('status') != 'evaluated':
            return jsonify({
                'success': False,
                'error': 'Submission not yet evaluated'
            }), 400
        
        # Get format from query parameter (default: pdf)
        report_format = request.args.get('format', 'pdf')
        
        # Generate report
        report_path = report_generator.generate_individual_report(submission, format=report_format)
        
        return jsonify({
            'success': True,
            'message': 'Report generated successfully',
            'download_url': f'/api/reports/download/{os.path.basename(report_path)}'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/reports/spreadsheet', methods=['GET'])
def generate_spreadsheet():
    """Generate Excel spreadsheet with all assessments"""
    try:
        # Get all evaluated submissions
        submissions = list(db.submissions.find({'status': 'evaluated'}))
        
        if not submissions:
            return jsonify({
                'success': False,
                'error': 'No evaluated submissions found'
            }), 404
        
        # Generate spreadsheet
        spreadsheet_path = report_generator.generate_spreadsheet(submissions)
        
        return jsonify({
            'success': True,
            'message': 'Spreadsheet generated successfully',
            'download_url': f'/api/reports/download/{os.path.basename(spreadsheet_path)}'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/reports/download/<filename>', methods=['GET'])
def download_report(filename):
    """Download generated report"""
    try:
        file_path = os.path.join(Config.REPORTS_DIR, filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': 'Report not found'
            }), 404
        
        return send_file(file_path, as_attachment=True)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# STATISTICS ENDPOINTS
# ============================================================================

@app.route('/api/stats/overview', methods=['GET'])
def get_statistics_overview():
    """Get overall statistics"""
    try:
        total_submissions = db.submissions.count_documents({})
        evaluated = db.submissions.count_documents({'status': 'evaluated'})
        pending = db.submissions.count_documents({'status': 'pending'})
        
        # Calculate average score
        pipeline = [
            {'$match': {'status': 'evaluated'}},
            {'$group': {
                '_id': None,
                'avg_score': {'$avg': '$assessment.total_score'}
            }}
        ]
        avg_result = list(db.submissions.aggregate(pipeline))
        avg_score = round(avg_result[0]['avg_score'], 2) if avg_result else 0
        
        # Get pass/fail counts
        passed = db.submissions.count_documents({
            'status': 'evaluated',
            'assessment.total_score': {'$gte': Config.PASS_THRESHOLD}
        })
        
        failed = evaluated - passed
        
        return jsonify({
            'success': True,
            'statistics': {
                'total_submissions': total_submissions,
                'evaluated': evaluated,
                'pending': pending,
                'average_score': avg_score,
                'passed': passed,
                'failed': failed,
                'pass_rate': round((passed / evaluated * 100), 2) if evaluated > 0 else 0
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats/submissions', methods=['GET'])
def get_submission_trends():
    """Get submission trends over time"""
    try:
        pipeline = [
            {
                '$group': {
                    '_id': {
                        '$dateToString': {
                            'format': '%Y-%m-%d',
                            'date': '$submitted_at'
                        }
                    },
                    'count': {'$sum': 1}
                }
            },
            {'$sort': {'_id': 1}},
            {'$limit': 30}  # Last 30 days
        ]
        
        trends = list(db.submissions.aggregate(pipeline))
        
        return jsonify({
            'success': True,
            'trends': trends
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("AutoAssess - Autonomous Programming Assignment Evaluation")
    print("=" * 60)
    print(f"Server starting on http://{Config.HOST}:{Config.PORT}")
    print("=" * 60)
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
