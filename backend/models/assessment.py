"""
Assessment database model
"""
from datetime import datetime

class Assessment:
    """Assessment model representing evaluation results"""
    
    @staticmethod
    def create(submission_id, scores, feedback):
        """Create new assessment document"""
        return {
            'submission_id': submission_id,
            'scores': scores,
            'total_score': scores.get('total_score', 0),
            'grade': scores.get('grade'),
            'feedback': feedback,
            'rubric_breakdown': scores.get('breakdown', {}),
            'strengths': feedback.get('strengths', []),
            'improvements': feedback.get('improvements', []),
            'recommendations': feedback.get('recommendations', []),
            'assessed_at': datetime.utcnow(),
            'created_at': datetime.utcnow()
        }
    
    @staticmethod
    def calculate_total_score(breakdown):
        """Calculate total score from rubric breakdown"""
        total = 0
        for category, data in breakdown.items():
            total += data.get('score', 0)
        return round(total, 2)
    
    @staticmethod
    def get_grade(total_score):
        """Convert score to letter grade"""
        if total_score >= 90:
            return 'A+'
        elif total_score >= 85:
            return 'A'
        elif total_score >= 80:
            return 'A-'
        elif total_score >= 75:
            return 'B+'
        elif total_score >= 70:
            return 'B'
        elif total_score >= 65:
            return 'B-'
        elif total_score >= 60:
            return 'C+'
        elif total_score >= 55:
            return 'C'
        elif total_score >= 50:
            return 'C-'
        elif total_score >= 45:
            return 'D'
        else:
            return 'F'
