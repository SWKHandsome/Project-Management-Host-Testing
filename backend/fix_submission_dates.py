"""
Script to fix submission dates by fetching actual upload times from Google Drive
"""
from utils.db_connection import db
from config import Config
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dateutil import parser
import os

def fix_submission_dates():
    """Update all submission dates with actual Google Drive upload times"""
    try:
        # Initialize Google Drive API
        if not os.path.exists(Config.GOOGLE_CREDENTIALS_PATH):
            print("✗ Google Drive credentials not found")
            return
        
        credentials = service_account.Credentials.from_service_account_file(
            Config.GOOGLE_CREDENTIALS_PATH,
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        
        service = build('drive', 'v3', credentials=credentials)
        print("✓ Google Drive API initialized")
        
        # Get all submissions
        submissions = list(db.submissions.find({}))
        print(f"\n📊 Found {len(submissions)} submissions to update")
        
        updated_count = 0
        for submission in submissions:
            file_id = submission.get('file_id')
            if not file_id:
                continue
            
            try:
                # Get file metadata from Google Drive
                file_info = service.files().get(
                    fileId=file_id,
                    fields='id, name, createdTime'
                ).execute()
                
                # Parse the creation time
                created_time = parser.parse(file_info['createdTime'])
                
                # Update in database
                db.submissions.update_one(
                    {'_id': submission['_id']},
                    {'$set': {'submitted_at': created_time}}
                )
                
                print(f"✓ Updated: {submission.get('file_name')} -> {created_time}")
                updated_count += 1
                
            except Exception as e:
                print(f"✗ Error updating {submission.get('file_name')}: {e}")
        
        print(f"\n✅ Successfully updated {updated_count} submission dates")
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == '__main__':
    print("=" * 60)
    print("Fixing Submission Dates from Google Drive")
    print("=" * 60)
    fix_submission_dates()
