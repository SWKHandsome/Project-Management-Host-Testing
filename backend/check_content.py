from pymongo import MongoClient

client = MongoClient('mongodb+srv://autoassess_user:xx05310705@autoassess.cop7vie.mongodb.net/')
db = client['autoassess']

sub = db['submissions'].find_one({'file_name': '4444.pdf'})

if sub:
    content = sub['file_content']
    words = content.split()
    meaningful = [w for w in words if len(w) > 2 and not w.isdigit()]
    
    print(f'Content length: {len(content)} chars')
    print(f'Total words: {len(words)}')
    print(f'Meaningful words: {len(meaningful)}')
    print(f'\nFirst 500 chars of content:')
    print(repr(content[:500]))
    print(f'\nFirst 20 meaningful words:')
    print(meaningful[:20])
    print(f'\nScore: {sub["assessment"]["total_score"]}/100')
else:
    print('File not found')
