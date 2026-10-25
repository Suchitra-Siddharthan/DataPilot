import requests
import io
import csv

questions = [
    'What is the average salary?',
    'Find the correlation between salary and experience',
    'Show the distribution of salary',
    'Find unusual values in the salary column',
    'Handle missing values in the dataset',
    'Create a new age group column',
    'Predict customer churn'
]

print("END-TO-END DATAPILOT TEST RESULTS")
print("=" * 60)

# First upload a small CSV so the backend has a dataset loaded (API requires it)
csv_rows = [
    ['Name', 'Age', 'Salary', 'Experience', 'Department'],
    ['John', '30', '65000', '5', 'IT'],
    ['Jane', '28', '52000', '3', 'HR'],
    ['Bob', '35', '58000', '7', 'Sales'],
    ['Alice', '32', '70000', '6', 'IT'],
    ['Charlie', '45', '55000', '15', 'HR'],
    ['Dana', '22', '180000', '1', 'Executive'],
    ['Eve', '29', '60000', '4', 'IT'],
    ['Frank', '41', '59000', '10', 'Sales'],
    ['Grace', '36', '61000', '8', 'HR'],
    ['Hank', '50', '62000', '20', 'IT'],
    ['Ivy', '27', '58000', '3', 'Sales'],
    ['Jack', '31', '64000', '6', 'IT']
]

csv_buffer = io.StringIO()
writer = csv.writer(csv_buffer)
writer.writerows(csv_rows)
csv_buffer.seek(0)

files = {'file': ('test_dataset.csv', csv_buffer.read(), 'text/csv')}
upload_resp = requests.post('http://127.0.0.1:5000/api/dataset/upload', files=files)

if upload_resp.status_code != 200:
    print('Dataset upload failed:', upload_resp.status_code, upload_resp.text)
    raise SystemExit(1)

print('Dataset uploaded successfully')

for question in questions:
    response = requests.post('http://127.0.0.1:5000/api/analyze', json={'question': question})
    try:
        result = response.json()
    except Exception:
        result = {'error': 'no json', 'text': response.text}

    print(f'Question: {question}')
    print(f'Status: {response.status_code}')
    print(f'Intent: {result.get("intent", "N/A")}')
    print(f'Tool: {result.get("tool", "N/A")}')
    print(f'API Status: {result.get("status", "N/A")}')
    print(f'Validation Success: {result.get("validation", {}).get("success", False)}')

    if result.get('result') and isinstance(result['result'], dict):
        if 'error' in result['result']:
            print(f'Error: {result["result"]["error"]}')
        else:
            print(f'Result: Success')

    print('---')

print("=" * 60)
print("TEST COMPLETE")