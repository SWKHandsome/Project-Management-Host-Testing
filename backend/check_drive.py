"""Check files in Google Drive folder"""
from services.drive_monitor import DriveMonitor

dm = DriveMonitor()

if dm.service:
    folder_id = '1XAIeUTkE5rNb08zoYTK8rb-GULDK85ed'
    results = dm.service.files().list(
        q=f"'{folder_id}' in parents and trashed=false",
        fields='files(id, name, createdTime, mimeType)',
        orderBy='createdTime desc'
    ).execute()
    
    files = results.get('files', [])
    print(f"\n✓ Files found in Google Drive folder: {len(files)}\n")
    
    if files:
        for f in files:
            print(f"  📄 {f['name']}")
            print(f"     Created: {f.get('createdTime', 'Unknown')}")
            print(f"     Type: {f.get('mimeType', 'Unknown')}")
            print()
    else:
        print("  No files found in the folder yet.\n")
else:
    print("✗ Google Drive API not initialized")
