import sys

sys.path.insert(0, r'c:\Users\ssuch\OneDrive\Documents\sem 7\ai\project\AI_PROJECT-tools-recommended--main\backend')

from app import app

client = app.test_client()
path = r'c:\Users\ssuch\OneDrive\Documents\sem 7\ai\project\AI_PROJECT-tools-recommended--main\backend\uploads\datapilot_test_dataset.csv'

with open(path, 'rb') as f:
    upload = client.post(
        '/api/dataset/upload',
        data={'file': (f, 'datapilot_test_dataset.csv')},
        content_type='multipart/form-data'
    )
    print('UPLOAD', upload.status_code, upload.get_json())

resp = client.post(
    '/api/analyze',
    json={'question': 'Analyze the correlation between salary, years of experience, performance score, and monthly hours.'}
)
print('ANALYZE_STATUS', resp.status_code)
print('ANALYZE_JSON', resp.get_json())
