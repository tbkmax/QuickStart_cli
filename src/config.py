import os
from pathlib import Path

APP_NAME = "QuickStart_cli"

# Determine project root relative to this config file (src/config.py)
# src/config.py -> src/ -> project_root/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_DIR = PROJECT_ROOT / "data"
DB_PATH = DB_DIR / "quickstart.db"

# Ensure the directory exists
try:
    DB_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    # If we can't write to project dir (e.g. installed in read-only location), 
    # fallback to home dir or raise error. 
    # For now, we assume user has write access to their own code.
    print(f"Warning: Could not create data directory at {DB_DIR}. Using current directory.")
    DB_PATH = Path("quickstart.db")
