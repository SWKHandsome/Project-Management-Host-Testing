from utils.db_connection import db
import json

sub = db.submissions.find_one({})
if not sub:
    print("No submission found")
else:
    print("="*60)
    print(f"Student ID: {sub.get('student_id')}")
    print(f"File Name: {sub.get('file_name')}")
    print(f"Status: {sub.get('status')}")
    print("="*60)
    
    assessment = sub.get('assessment', {})
    print(f"\nTotal Score: {assessment.get('total_score')}/100")
    print(f"Grade: {assessment.get('grade')}")
    print("\nScore Breakdown:")
    print("-"*60)
    
    breakdown = assessment.get('breakdown', {})
    for category, details in breakdown.items():
        score = details.get('score', 0)
        max_score = details.get('max_score', 0)
        percentage = details.get('percentage', 0)
        print(f"\n{category.replace('_', ' ').title()}:")
        print(f"  Score: {score}/{max_score} ({percentage}%)")
        feedback = details.get('feedback', [])
        if feedback:
            print(f"  Feedback: {', '.join(feedback)}")
    
    print("\n" + "="*60)
    print("Overall Feedback:")
    print("-"*60)
    feedback_obj = assessment.get('feedback', {})
    
    if 'summary' in feedback_obj:
        print(f"\nSummary: {feedback_obj['summary']}")
    
    strengths = assessment.get('strengths', [])
    if strengths:
        print(f"\nStrengths:")
        for s in strengths:
            print(f"  ✓ {s}")
    
    improvements = assessment.get('improvements', [])
    if improvements:
        print(f"\nAreas for Improvement:")
        for i in improvements:
            print(f"  ✗ {i}")
