from utils.db_connection import db

# Find the submission
sub = db.submissions.find_one({'student_id': 'B250103A'})

if sub:
    print("="*70)
    print(f"File: {sub.get('file_name')}")
    print(f"Student ID: {sub.get('student_id')}")
    print(f"Student Name: {sub.get('student_name')}")
    print(f"Status: {sub.get('status')}")
    print(f"Total Score: {sub.get('assessment', {}).get('total_score')}")
    print("="*70)
    
    # Check file content length
    file_content = sub.get('file_content', '')
    print(f"\nExtracted Content Length: {len(file_content)} characters")
    print("\nFirst 1000 characters of extracted content:")
    print("-"*70)
    print(file_content[:1000])
    print("-"*70)
    
    # Check assessment breakdown
    print("\n\nAssessment Breakdown:")
    print("="*70)
    breakdown = sub.get('assessment', {}).get('breakdown', {})
    for category, details in breakdown.items():
        print(f"\n{category.upper()}:")
        print(f"  Score: {details.get('score')}/{details.get('max_score')}")
        print(f"  Feedback: {details.get('feedback')}")
    
else:
    print("Submission not found")
