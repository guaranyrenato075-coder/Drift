import sys
import urllib.request

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else "8765"
    url = f"http://127.0.0.1:{port}/api/health"
    try:
        with urllib.request.urlopen(url, timeout=1.5) as r:
            sys.exit(0 if r.status == 200 else 1)
    except Exception:
        sys.exit(1)

if __name__ == "__main__":
    main()
