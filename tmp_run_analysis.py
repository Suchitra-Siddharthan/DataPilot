import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from agent.agent import datapilot_agent
from data.dataset_manager import dataset_manager
import pandas as pd

# Prepare sample dataset similar to tests
sample_data = pd.DataFrame({
    'Name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie', 'Dana', 'Eve', 'Frank', 'Grace', 'Hank'],
    'Age': [30, 28, 35, 32, 45, 22, 29, 41, 36, 50],
    'Salary': [65000, 52000, 58000, 70000, 55000, 180000, 60000, 59000, 61000, 62000],
    'Experience': [5, 3, 7, 6, 15, 1, 4, 10, 8, 20],
    'Department': ['IT', 'HR', 'Sales', 'IT', 'HR', 'Executive', 'IT', 'Sales', 'HR', 'IT']
})

# Load into dataset_manager
dataset_manager.current_dataset = sample_data
dataset_manager.dataset_metadata = {
    'rows': len(sample_data),
    'columns': len(sample_data.columns),
    'numeric_columns': ['Age', 'Salary', 'Experience'],
    'categorical_columns': ['Name', 'Department'],
    'column_names': list(sample_data.columns)
}

questions = [
    'Give me the summary statistics of this dataset.',
    'Predict whether an employee will leave the company using the available features.',
    'Find unusual values in the salary column',
]

for q in questions:
    print('QUESTION:', q)
    res = datapilot_agent.analyze(q)
    print('SUCCESS:', res.get('success'))
    print('INTENT:', res.get('intent'))
    print('CONFIDENCE:', res.get('confidence'))
    print('SELECTED_TOOL:', res.get('selected_tool'))
    print('EXPLANATION:', res.get('explanation'))
    print('RESULT_KEYS:', list(res.get('result', {}).keys()) if res.get('result') else res.get('result'))
    print('-----')

print('DONE')
