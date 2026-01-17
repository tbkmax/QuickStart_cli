# QuickStart_cli

A CLI tool for Windows 11 to manage and launch workspaces (sets of applications/files) efficiently.

## Installation

1. Install Python 3.10+.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### List Workspaces
```bash
python src/main.py ls
```

### Create a Workspace
```bash
python src/main.py build
```
Follow the interactive prompts to add files to your new workspace.

### Start a Workspace
```bash
python src/main.py start <workspace_name>
```

### Delete a Workspace
```bash
python src/main.py delete <workspace_name>
```
