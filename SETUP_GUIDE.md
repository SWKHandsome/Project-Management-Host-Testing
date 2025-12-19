# AutoAssess Setup Guide

## Quick Start Guide

### Step 1: Install Python Dependencies
```bash
cd C:\AutoAssess\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Setup MongoDB
1. **Option A: Local MongoDB**
   - Download and install MongoDB Community Server
   - Start MongoDB service
   - Default connection: `mongodb://localhost:27017/`

2. **Option B: MongoDB Atlas (Cloud)**
   - Create free account at https://www.mongodb.com/cloud/atlas
   - Create a cluster
   - Get connection string
   - Update `.env` file with connection string

### Step 3: Setup Google Drive API
1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Create a new project
3. Enable Google Drive API
4. Create Service Account:
   - Go to IAM & Admin → Service Accounts
   - Click "Create Service Account"
   - Download JSON credentials
5. Save credentials as `C:\AutoAssess\config\credentials.json`
6. Create a Google Drive folder for submissions
7. Share folder with service account email (found in credentials.json)
8. Copy folder ID from URL

### Step 4: Configure Environment
Create `.env` file in `C:\AutoAssess\backend\`:
```
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=autoassess
GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
GOOGLE_CREDENTIALS_PATH=../config/credentials.json
MONITORING_INTERVAL=30
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### Step 5: Run the Application
```bash
# Terminal 1: Start Backend
cd C:\AutoAssess\backend
python app.py

# Terminal 2: Open Frontend
# Simply open C:\AutoAssess\frontend\index.html in your browser
# Or use VS Code Live Server extension
```

### Step 6: Test the System
1. Open browser to `C:\AutoAssess\frontend\index.html`
2. Click "Start Monitoring"
3. Upload a test file to Google Drive folder
4. Watch it appear in the dashboard and get auto-evaluated

## Troubleshooting

### Backend won't start
- Check MongoDB is running
- Verify Python dependencies are installed
- Check `.env` configuration

### Google Drive not working
- Verify credentials.json exists
- Check folder is shared with service account
- Verify folder ID is correct

### Frontend not connecting
- Check backend is running on port 5000
- Update API_BASE_URL in dashboard.js if needed
- Check browser console for errors

## File Structure Reference
```
C:\AutoAssess\
├── backend\
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   ├── .env
│   ├── models\
│   ├── services\
│   └── utils\
├── frontend\
│   ├── index.html
│   ├── css\styles.css
│   └── js\dashboard.js
└── config\
    ├── rubric.json
    └── credentials.json
```

## Support
For issues, check:
1. Backend terminal for error messages
2. Browser console for frontend errors
3. MongoDB connection
4. Google Drive API credentials
