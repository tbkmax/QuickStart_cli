# QuickStart CLI

A simple Windows CLI tool to manage and launch sets of files and applications (workspaces) efficiently.

For detailed architecture and design decisions, please refer to [design.md](design.md).

## Installation

1.  **Prerequisites**: Python 3.10+
2.  **Setup**:
    ```powershell
    python -m venv .venv
    .\.venv\Scripts\activate
    pip install -r requirements.txt
    pip install -e .
    ```

    > **Note**: `pip install -e .` registers the `qs` command.

## Usage

You can run the tool via Python or using the built executable.

### Commands

*   **List Workspaces**: Show all saved workspaces and their status.
    ```powershell
    qs ls
    ```

*   **Create Workspace**: Interactive prompt to create a new workspace.
    ```powershell
    qs build
    ```

*   **Start Workspace**: Launch all files in a workspace.
    ```powershell
    qs start <name>
    ```

*   **Stop Workspace**: Terminate all running processes for a workspace.
    ```powershell
    qs stop <name>
    ```

*   **Delete Workspace**: Remove a workspace configuration.
    ```powershell
    qs delete <name>
    ```

> **Note**: Commands are "Silent on Success". If a command works, it produces no output (except `ls`).

## Build (Exe)

To create a standalone `qs.exe` for Windows:

```powershell
.\.venv\Scripts\pyinstaller --onefile --name qs cli.py
```

The executable will be generated in the `dist/` folder.
