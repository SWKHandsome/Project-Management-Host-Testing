"""
Configuration settings for AutoAssess system
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # MongoDB Configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'autoassess')
    
    # Google Drive Configuration
    GOOGLE_DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID', '')
    GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', '../config/credentials.json')
    
    # File Monitoring Configuration
    MONITORING_INTERVAL = int(os.getenv('MONITORING_INTERVAL', 30))  # seconds
    SUPPORTED_FILE_TYPES = ['.pdf', '.docx', '.txt', '.doc']
    
    # Evaluation Configuration
    MAX_SCORE = 100
    PASS_THRESHOLD = 50
    
    # Report Configuration
    REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'reports')
    TEMP_DIR = os.path.join(os.path.dirname(__file__), 'temp')
    
    # Ensure directories exist
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    # Rubric Configuration (weights in percentage)
    RUBRIC = {
        'logic_design': {
            'weight': 30,
            'criteria': [
                'Problem understanding',
                'Solution correctness',
                'Algorithm efficiency',
                'Edge case handling'
            ]
        },
        'flowchart': {
            'weight': 25,
            'criteria': [
                'Proper symbol usage',
                'Clear flow direction',
                'Completeness',
                'Readability'
            ]
        },
        'pseudocode': {
            'weight': 25,
            'criteria': [
                'Syntax accuracy',
                'Logical structure',
                'Variable naming',
                'Clarity'
            ]
        },
        'formatting': {
            'weight': 10,
            'criteria': [
                'Organization',
                'Neatness',
                'Consistency',
                'Professional appearance'
            ]
        },
        'documentation': {
            'weight': 10,
            'criteria': [
                'Comments quality',
                'Explanations',
                'Clarity',
                'Completeness'
            ]
        }
    }
    
    # Student ID patterns (regex patterns)
    STUDENT_ID_PATTERNS = [
        r'[A-Z]\d{6}[A-Z]',  # Example: B240253C (1 letter + 6 digits + 1 letter)
        r'[A-Z]{2}\d{6}',    # Example: AB123456 (2 letters + 6 digits)
        r'\d{8,10}',         # Example: 12345678 (8-10 digits)
        r'[A-Z]\d{7}',       # Example: A1234567 (1 letter + 7 digits)
    ]
    
    # Name extraction patterns
    NAME_PATTERNS = [
        r'Name:\s*([A-Za-z\s]+)',
        r'Student:\s*([A-Za-z\s]+)',
        r'Prepared by:\s*([A-Za-z\s]+)',
    ]
    
    @staticmethod
    def validate():
        """Validate required configuration"""
        if not Config.GOOGLE_DRIVE_FOLDER_ID:
            print("WARNING: GOOGLE_DRIVE_FOLDER_ID not set. Please configure in .env file.")
        
        if not os.path.exists(Config.GOOGLE_CREDENTIALS_PATH):
            print(f"WARNING: Google credentials not found at {Config.GOOGLE_CREDENTIALS_PATH}")
            print("Please set up Google Drive API credentials.")
        
        return True
