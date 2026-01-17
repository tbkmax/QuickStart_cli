# QuickStart_cli Plan

## Goal
Create a CLI tool (`qs`) for Windows 11 to manage and launch "workspaces" (sets of applications/files) efficiently.

## Technical Stack
- **OS**: Windows 11
- **Language**: Python 3.10+
- **Database**: SQLite (built-in `sqlite3` module)
- **CLI Framework**: `typer` (for modern, easy-to-maintain CLI)
- **GUI Interactions**: `tkinter.filedialog` (for file selection windows)

## Features & Commands

### 1. `qs ls`
List all authenticated workspaces.
- **Output Columns**: Workspace Name, File Count, Created Date, Last Activated, Activate Count.
- **Format**: Table format (using `rich` or `tabulate` for readability).

### 2. `qs build`
Interactive process to create a new workspace.
1. Prompt for **Workspace Name** (must be unique, no spaces).
2. Loop:
   - Open a Windows file selection dialog (`tkinter`) to verify user intention.
   - User selects a file (executable, image, document, etc.).
   - Confirm if more files need to be added.
3. Save workspace to database.

### 3. `qs start <workspace_name>`
Launch a specific workspace.
- **Action**: Open all files/applications associated with the workspace using `os.startfile` or `subprocess.Popen`.
- **Logic**:
  - Update `last_activated_date`.
  - Increment `activate_count`.
- **Output**: Silent on success. Print error only if launch fails.

### 4. `qs delete <workspace_name>`
Remove a workspace from the database.
- **Confirmation**: Simple confirmation prompt (y/n) recommended.

## Database Schema
**Table: workspaces**
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `name`: TEXT UNIQUE NOT NULL
- `created_at`: DATETIME DEFAULT CURRENT_TIMESTAMP
- `last_activated_at`: DATETIME
- `activate_count`: INTEGER DEFAULT 0

**Table: workspace_files**
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `workspace_id`: INTEGER FOREIGN KEY (workspaces.id)
- `file_path`: TEXT NOT NULL (Must support UTF-8 for Chinese/Japanese characters)

## Constraints & Requirements
- **Localization**: Full support for Chinese/Japanese characters in file paths.
- **Silent Mode**: `qs start` should have no output unless an error occurs.
- **File Types**: Must handle `.exe`, `.clip` (CLIP Studio), `.ref` (PureRef), images (`.png`, `.jpg`), etc.