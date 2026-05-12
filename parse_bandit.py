import json
import sys

try:
    with open('bandit_results.json', 'r') as f:
        data = json.load(f)
    
    results = data.get('results', [])
    for r in results:
        # Format: filename, line, test_id, severity, issue
        print(f"{r['filename']}:{r['line_number']}:{r['test_id']}:{r['issue_severity']}:{r['issue_text'][:60]}")
except Exception as e:
    print(f"Error parsing bandit results: {e}")
