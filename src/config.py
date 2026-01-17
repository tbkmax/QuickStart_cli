import os
from pathlib import Path

import sys

APP_NAME = "QuickStart_cli"

# Determine project root
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app 
    # path into variable _MEIPASS.
    # However, we want the data to be persistent, so we shouldn't store it in _MEIPASS (temp)
    # unless it's read-only data.
    # For a persistent DB next to the executable:
    PROJECT_ROOT = Path(sys.executable).parent
else:
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
