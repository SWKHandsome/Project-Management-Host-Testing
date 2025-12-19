"""
MongoDB database connection module
"""
from pymongo import MongoClient
from config import Config

class Database:
    """MongoDB database connection wrapper"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(Config.MONGODB_URI)
            self.db = self.client[Config.MONGODB_DB_NAME]
            
            # Test connection
            self.client.server_info()
            print(f"✓ Connected to MongoDB: {Config.MONGODB_DB_NAME}")
            
            # Create indexes
            self.create_indexes()
            
        except Exception as e:
            print(f"✗ MongoDB connection failed: {e}")
            print("  Make sure MongoDB is running and connection string is correct")
    
    def create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Submissions collection indexes
            self.db.submissions.create_index('student_id')
            self.db.submissions.create_index('status')
            self.db.submissions.create_index('submitted_at')
            self.db.submissions.create_index('file_id')
            
            print("✓ Database indexes created")
        except Exception as e:
            print(f"✗ Error creating indexes: {e}")
    
    @property
    def submissions(self):
        """Get submissions collection"""
        return self.db.submissions
    
    @property
    def assessments(self):
        """Get assessments collection"""
        return self.db.assessments
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            print("✓ MongoDB connection closed")

# Create global database instance
db = Database()
