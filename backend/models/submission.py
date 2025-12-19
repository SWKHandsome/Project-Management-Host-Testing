"""
Submission database model
"""
from datetime import datetime

class Submission:
    """Submission model representing a student's assignment submission"""
    
    @staticmethod
    def create(data):
        """Create new submission document"""
        return {
            'file_id': data.get('file_id'),
            'file_name': data.get('file_name'),
            'file_size': data.get('file_size', 0),
            'mime_type': data.get('mime_type'),
            'student_id': data.get('student_id'),
            'student_name': data.get('student_name'),
            'submitted_at': datetime.utcnow(),
            'status': 'pending',  # pending, evaluated, error
            'assessment': None,
            'evaluated_at': None,
            'error_message': None,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
    
    @staticmethod
    def update_status(submission_id, status, assessment=None):
        """Update submission status and assessment"""
        update_data = {
            'status': status,
            'updated_at': datetime.utcnow()
        }
        
        if assessment:
            update_data['assessment'] = assessment
            update_data['evaluated_at'] = datetime.utcnow()
        
        return update_data
    
    @staticmethod
    def validate(data):
        """Validate submission data"""
        required_fields = ['file_id', 'file_name']
        
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"Missing required field: {field}"
        
        return True, "Valid"
