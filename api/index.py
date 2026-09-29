import sys
import os
from pathlib import Path

# Add project root to sys.path so backend and other modules can be imported
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Set VERCEL environment indicator
os.environ["VERCEL"] = "1"

# Import FastAPI application
from backend.main import app
