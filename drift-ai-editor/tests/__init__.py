import sys
from pathlib import Path

# Ensure drift-ai-editor is on sys.path for all unit tests
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
