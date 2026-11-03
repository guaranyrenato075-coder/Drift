import urllib.request
import json

url = 'https://api.github.com/repos/guaranyrenato075-coder/Drift/actions/runs/41146829522/jobs'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        for j in data.get('jobs', []):
            print(f"Job: {j.get('name')} | Status: {j.get('status')} | Conclusion: {j.get('conclusion')}")
except Exception as e:
    print("Error:", e)

