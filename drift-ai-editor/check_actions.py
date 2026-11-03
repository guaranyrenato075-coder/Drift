import urllib.request
import json

url = 'https://api.github.com/repos/guaranyrenato075-coder/Drift/actions/runs'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        runs = data.get('workflow_runs', [])
        print(f"Total runs: {len(runs)}")
        for r in runs[:10]:
            print(f"ID: {r.get('id')} | Name: {r.get('name')} | Status: {r.get('status')} | Conclusion: {r.get('conclusion')} | URL: {r.get('html_url')}")
except Exception as e:
    print("Error:", e)

