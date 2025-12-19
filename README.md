# AutoAssess: Autonomous Programming Assignment Evaluation System

## 🎯 Project Overview
AutoAssess is an autonomous system that assists lecturers in assessing programming logic design assignments submitted by Foundation students. The system automatically monitors Google Drive for new submissions, extracts student details, evaluates assignments based on rubrics, and generates comprehensive assessment reports.

## 🏗️ Architecture
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python (Flask)
- **Database**: MongoDB
- **Cloud Platform**: Google Cloud Platform (GCP)
- **File Storage**: Google Drive

## 📁 Project Structure
```
AutoAssess/
├── backend/
│   ├── app.py                  # Main Flask application
│   ├── config.py               # Configuration settings
│   ├── requirements.txt        # Python dependencies
│   ├── models/
│   │   ├── submission.py       # Submission database model
│   │   └── assessment.py       # Assessment database model
│   ├── services/
│   │   ├── drive_monitor.py    # Google Drive file monitoring
│   │   ├── extraction.py       # Student data extraction
│   │   ├── evaluator.py        # Rubric-based evaluation engine
│   │   └── report_generator.py # Report generation
│   └── utils/
│       ├── db_connection.py    # MongoDB connection
│       └── helpers.py          # Utility functions
├── frontend/
│   ├── index.html              # Main dashboard
│   ├── css/
│   │   └── styles.css          # Styling
│   └── js/
│       └── dashboard.js        # Dashboard functionality
├── config/
│   ├── rubric.json             # Assessment rubric
│   └── credentials.json.example # GCP credentials template
└── README.md
```

## 🚀 Setup Instructions

### Prerequisites
- Python 3.9+
- MongoDB (local or MongoDB Atlas)
- Google Cloud Platform account
- Modern web browser

### 1. Clone and Setup Environment
```bash
cd AutoAssess
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r backend/requirements.txt
```

### 2. Configure Google Drive API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Drive API
4. Create service account credentials
5. Download credentials JSON and save as `config/credentials.json`
6. Share your Google Drive folder with the service account email

### 3. Configure MongoDB
Create `.env` file in backend directory:
```
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=autoassess
GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
```

### 4. Run the Application
```bash
# Start backend server
cd backend
python app.py

# Open frontend in browser
# Navigate to frontend/index.html or use live server
```

## 📋 Features

### 1. File Monitoring
- Automatically detects new submissions in Google Drive
- Supports PDF, DOCX, TXT formats
- Real-time monitoring with configurable intervals

### 2. Data Extraction
- Extracts student name and ID from filename
- Falls back to document content parsing
- Pattern matching for various naming conventions

### 3. Rubric-Based Evaluation
Evaluates assignments based on:
- **Logic Design** (30%): Correctness and efficiency
- **Flowchart** (25%): Clarity, symbols, flow
- **Pseudocode** (25%): Syntax, structure, clarity
- **Formatting** (10%): Organization and presentation
- **Documentation** (10%): Comments and explanations

### 4. Report Generation
- Individual PDF reports per student
- Excel spreadsheet with all scores
- Detailed feedback and recommendations

### 5. Lecturer Dashboard
- View all submissions
- Filter and search functionality
- Download individual or batch reports
- Real-time assessment status

## 🔧 API Endpoints

- `GET /api/submissions` - Get all submissions
- `GET /api/submissions/<id>` - Get specific submission
- `POST /api/submissions/<id>/evaluate` - Trigger evaluation
- `POST /api/monitor/start` - Start Drive monitoring
- `POST /api/monitor/stop` - Stop Drive monitoring
- `GET /api/reports/individual/<id>` - Generate individual report
- `GET /api/reports/spreadsheet` - Generate Excel spreadsheet
- `GET /api/stats/overview` - Get statistics

## 📧 Support
For technical issues, refer to the project documentation.
