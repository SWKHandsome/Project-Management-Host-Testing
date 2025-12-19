"""
Utility helper functions
"""
import re
import os
from datetime import datetime

def extract_file_extension(filename):
    """Extract file extension from filename"""
    return os.path.splitext(filename)[1].lower()

def is_supported_file(filename):
    """Check if file type is supported"""
    from config import Config
    ext = extract_file_extension(filename)
    return ext in Config.SUPPORTED_FILE_TYPES

def sanitize_filename(filename):
    """Sanitize filename for safe storage"""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    return filename

def format_date(date_obj):
    """Format datetime object to string"""
    if isinstance(date_obj, datetime):
        return date_obj.strftime('%Y-%m-%d %H:%M:%S')
    return str(date_obj)

def calculate_percentage(score, max_score):
    """Calculate percentage score"""
    if max_score == 0:
        return 0
    return round((score / max_score) * 100, 2)

def get_grade(score):
    """Convert score to letter grade"""
    if score >= 90:
        return 'A+'
    elif score >= 85:
        return 'A'
    elif score >= 80:
        return 'A-'
    elif score >= 75:
        return 'B+'
    elif score >= 70:
        return 'B'
    elif score >= 65:
        return 'B-'
    elif score >= 60:
        return 'C+'
    elif score >= 55:
        return 'C'
    elif score >= 50:
        return 'C-'
    elif score >= 45:
        return 'D'
    else:
        return 'F'

def parse_student_info_from_filename(filename):
    """
    Extract student ID and name from filename
    Expected formats:
    - StudentName_StudentID_Assignment.pdf
    - ID_Name_Assignment.docx
    - StudentID-StudentName.pdf
    """
    from config import Config
    
    # Remove extension
    name_part = os.path.splitext(filename)[0]
    
    student_id = None
    student_name = None
    
    # Try to find student ID using patterns
    for pattern in Config.STUDENT_ID_PATTERNS:
        match = re.search(pattern, name_part)
        if match:
            student_id = match.group(0)
            break
    
    # Extract name (text before or after ID)
    if student_id:
        # Split by common delimiters
        parts = re.split(r'[_\-\s]+', name_part)
        for part in parts:
            # Look for part that's not the ID and contains letters
            if part != student_id and re.search(r'[A-Za-z]{2,}', part):
                if not student_name:
                    student_name = part
                else:
                    student_name += ' ' + part
    
    return {
        'student_id': student_id,
        'student_name': student_name.title() if student_name else None
    }

def validate_submission_data(data):
    """Validate submission data"""
    required_fields = ['file_name', 'file_id']
    
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}"
    
    return True, "Valid"

def create_submission_record(file_info, student_info):
    """Create submission record for database"""
    from dateutil import parser
    
    # Use the file's creation time from Google Drive if available
    submitted_at = datetime.utcnow()
    if 'createdTime' in file_info and file_info['createdTime']:
        try:
            submitted_at = parser.parse(file_info['createdTime'])
        except:
            pass
    
    return {
        'file_id': file_info.get('id'),
        'file_name': file_info.get('name'),
        'file_size': file_info.get('size', 0),
        'mime_type': file_info.get('mimeType'),
        'student_id': student_info.get('student_id'),
        'student_name': student_info.get('student_name'),
        'submitted_at': submitted_at,
        'status': 'pending',
        'assessment': None,
        'evaluated_at': None
    }
