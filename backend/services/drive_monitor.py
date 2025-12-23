"""
Google Drive monitoring service
Monitors a specific folder for new submissions
"""
import time
import os
from collections import deque
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import io

from config import Config
from utils.db_connection import db
from utils.helpers import parse_student_info_from_filename, create_submission_record
from services.extraction import DataExtractor
from services.evaluator import AssignmentEvaluator

class DriveMonitor:
    """Google Drive file monitoring service"""
    
    def __init__(self):
        self.service = None
        self.is_running = False
        self.last_check_time = None
        self.files_processed = 0
        self.extractor = DataExtractor()
        self.evaluator = AssignmentEvaluator()
        self.processed_file_ids = set()
        self.request_timestamps = deque()
        self.max_requests_per_minute = 50
        self.throttle_window = 60
        
        # Initialize Google Drive API
        self.initialize_drive_api()

    def _throttle_requests(self):
        """Simple leaky-bucket limiter to keep requests under quota"""
        now = time.time()
        while self.request_timestamps and now - self.request_timestamps[0] > self.throttle_window:
            self.request_timestamps.popleft()
        if len(self.request_timestamps) >= self.max_requests_per_minute:
            wait_for = self.throttle_window - (now - self.request_timestamps[0]) + 1
            wait_for = max(1, int(wait_for))
            print(f"  ⚠ Drive quota reached, pausing {wait_for}s")
            time.sleep(wait_for)
            self._throttle_requests()
        else:
            self.request_timestamps.append(now)

    def _handle_rate_error(self, error, context):
        if isinstance(error, HttpError) and error.resp.status in (403, 429):
            print(f"  ⚠ Drive API {error.resp.status} during {context}, backing off 60s")
            time.sleep(60)
            return True
        return False
    
    def initialize_drive_api(self):
        """Initialize Google Drive API service"""
        try:
            creds_path = os.path.abspath(Config.GOOGLE_CREDENTIALS_PATH)
            if not os.path.exists(creds_path):
                print(f"✗ Google Drive credentials not found at: {creds_path}")
                return
            
            credentials = service_account.Credentials.from_service_account_file(
                creds_path,
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            
            self.service = build('drive', 'v3', credentials=credentials)
            print("✓ Google Drive API initialized")
            
        except Exception as e:
            print(f"✗ Failed to initialize Google Drive API: {e}")
    
    def start_monitoring(self):
        """Start monitoring Google Drive folder"""
        if not self.service:
            print("✗ Cannot start monitoring: Google Drive API not initialized")
            return
        
        if not Config.GOOGLE_DRIVE_FOLDER_ID:
            print("✗ Cannot start monitoring: GOOGLE_DRIVE_FOLDER_ID not configured")
            return
        
        self.is_running = True
        print(f"✓ Started monitoring Google Drive folder")
        print(f"  Checking every {Config.MONITORING_INTERVAL} seconds...")
        
        # Load previously processed files
        self.load_processed_files()
        
        while self.is_running:
            try:
                self.check_for_new_files()
                self.last_check_time = datetime.utcnow().isoformat()
                time.sleep(Config.MONITORING_INTERVAL)
            except Exception as e:
                print(f"✗ Error during monitoring: {e}")
                time.sleep(Config.MONITORING_INTERVAL)
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_running = False
        print("✓ Monitoring stopped")
    
    def load_processed_files(self):
        """Load previously processed file IDs from database"""
        try:
            submissions = db.submissions.find({}, {'file_id': 1})
            self.processed_file_ids = {sub['file_id'] for sub in submissions}
            print(f"  Loaded {len(self.processed_file_ids)} previously processed files")
        except Exception as e:
            print(f"✗ Error loading processed files: {e}")
    
    def check_for_new_files(self):
        """Check for new files in Google Drive folder"""
        try:
            # Query for files in the specified folder
            query = f"'{Config.GOOGLE_DRIVE_FOLDER_ID}' in parents and trashed=false"
            
            self._throttle_requests()
            results = self.service.files().list(
                q=query,
                fields="files(id, name, mimeType, size, createdTime, modifiedTime)",
                orderBy="createdTime desc"
            ).execute()
            
            files = results.get('files', [])
            
            # Process new files
            new_files_count = 0
            for file in files:
                if file['id'] not in self.processed_file_ids:
                    # Check if file type is supported
                    file_ext = os.path.splitext(file['name'])[1].lower()
                    if file_ext in Config.SUPPORTED_FILE_TYPES:
                        self.process_new_file(file)
                        self.processed_file_ids.add(file['id'])
                        new_files_count += 1
            
            if new_files_count > 0:
                print(f"✓ Processed {new_files_count} new file(s)")
            
        except HttpError as http_error:
            if not self._handle_rate_error(http_error, 'listing files'):
                print(f"✗ Drive API error while listing files: {http_error}")
        except Exception as e:
            print(f"✗ Error checking for new files: {e}")
    
    def process_new_file(self, file_info):
        """Process a newly detected file"""
        try:
            print(f"\n📄 Processing: {file_info['name']}")
            
            # Extract student info from filename
            student_info = parse_student_info_from_filename(file_info['name'])
            
            # Download file content for analysis
            file_content = self.download_file_content(file_info['id'])
            
            # Extract additional info from content if needed
            if not student_info['student_id'] or not student_info['student_name']:
                extracted_info = self.extractor.extract_from_content(
                    file_content, 
                    file_info['name']
                )
                
                # Merge extracted info
                if not student_info['student_id']:
                    student_info['student_id'] = extracted_info.get('student_id')
                if not student_info['student_name']:
                    student_info['student_name'] = extracted_info.get('student_name')
            
            # Extract full text content from file for evaluation
            extracted_text = self.extractor.extract_assignment_content(
                file_content,
                file_info['name']
            )
            
            # Create submission record
            submission_data = create_submission_record(file_info, student_info)
            # Store extracted text (limit to 5000 chars for database)
            submission_data['file_content'] = extracted_text[:5000] if extracted_text else ""
            
            # Insert into database
            result = db.submissions.insert_one(submission_data)
            submission_data['_id'] = result.inserted_id
            
            print(f"  ✓ Student ID: {student_info['student_id']}")
            print(f"  ✓ Student Name: {student_info['student_name']}")
            print(f"  ✓ Saved to database")
            
            # Automatically evaluate the submission
            print(f"  ⚙ Evaluating submission...")
            assessment = self.evaluator.evaluate(submission_data)
            
            # Update submission with assessment
            db.submissions.update_one(
                {'_id': result.inserted_id},
                {
                    '$set': {
                        'assessment': assessment,
                        'status': 'evaluated',
                        'evaluated_at': datetime.utcnow()
                    }
                }
            )
            
            print(f"  ✓ Evaluation complete - Score: {assessment['total_score']}/100")
            
            self.files_processed += 1
            
        except Exception as e:
            print(f"  ✗ Error processing file: {e}")
            
            # Save as error submission
            try:
                error_submission = create_submission_record(file_info, {'student_id': 'UNKNOWN', 'student_name': 'UNKNOWN'})
                error_submission['status'] = 'error'
                error_submission['error_message'] = str(e)
                db.submissions.insert_one(error_submission)
            except:
                pass
    
    def download_file_content(self, file_id):
        """Download file content from Google Drive"""
        try:
            # Re-initialize credentials if needed
            if not self.service:
                print("  ⚠ Drive service not initialized, attempting to reinitialize...")
                self.initialize_drive_api()
                if not self.service:
                    print("  ✗ Failed to reinitialize Drive service")
                    return b""
            
            self._throttle_requests()
            request = self.service.files().get_media(fileId=file_id)
            file_handle = io.BytesIO()
            downloader = MediaIoBaseDownload(file_handle, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            file_handle.seek(0)
            content = file_handle.read()
            print(f"  ✓ Downloaded {len(content)} bytes from Google Drive")
            return content
            
        except HttpError as http_error:
            if self._handle_rate_error(http_error, f'downloading file {file_id}'):
                return self.download_file_content(file_id)
            print(f"  ✗ Drive API error downloading file: {http_error}")
            return b""
        except Exception as e:
            print(f"  ✗ Error downloading file from Google Drive: {e}")
            # Try reinitializing and retry once
            try:
                print("  → Attempting to reinitialize Google Drive API...")
                self.initialize_drive_api()
                if self.service:
                    self._throttle_requests()
                    request = self.service.files().get_media(fileId=file_id)
                    file_handle = io.BytesIO()
                    downloader = MediaIoBaseDownload(file_handle, request)
                    done = False
                    while not done:
                        status, done = downloader.next_chunk()
                    file_handle.seek(0)
                    content = file_handle.read()
                    print(f"  ✓ Downloaded {len(content)} bytes after retry")
                    return content
            except Exception as retry_error:
                print(f"  ✗ Retry failed: {retry_error}")
            return b""
