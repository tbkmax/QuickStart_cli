# Implementation Plan - Process Management & Stop Command

## Goal
Implement a mechanism to track and terminate running workspaces. This involves switching from `os.startfile` to `subprocess.Popen` to capture Process IDs (PIDs) and storing them in the database.

## User Review Required
> [!WARNING]
> Switching to `subprocess.Popen` from `os.startfile` on Windows may change how some applications launch.
> **Limitation**: Some applications (like Chrome or game launchers) start a background process and exit the launcher immediately. In these cases, the captured PID will be invalid (dead), and `qs stop` will not be able to close the actual application.

## Proposed Changes

### Database Schema
#### [MODIFY] `database_manager.py`
- Create a new table `active_processes` to track running applications.
```sql
CREATE TABLE active_processes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id INTEGER,
    pid INTEGER,
    file_path TEXT,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(workspace_id) REFERENCES workspaces(id)
);
```

### Logic Layer
#### [MODIFY] `workspace_manager.py`
- **Method `start_workspace`**:
    - Change implementation to use `subprocess.Popen` instead of `os.startfile`.
    - `Popen` should be non-blocking (fire and forget from CLI perspective, but capture PID).
    - Insert `(workspace_id, pid, file_path)` into `active_processes`.
- **New Method `stop_workspace(name)`**:
    - specific workspace name is optional? Or stop all? -> Stop specific workspace.
    - query `active_processes` for the given workspace.
    - Loop through PIDs:
        - Check if process exists (`psutil.pid_exists` or `os.kill(pid, 0)`).
        - Terminate process (`os.kill` or `psutil.Process.terminate`).
    - Clean up entries from `active_processes`.
- **New Method `get_active_workspaces()`**:
    - Return list of workspaces that have active entries in DB.

### CLI Layer
#### [MODIFY] `main.py`
- Add `stop` command: `qs stop <name>`
- Update `status` or `ls` command to show "Running" status next to workspaces.

## Verification Plan

### Automated Tests
- **Test Database**: Ensure `active_processes` table is created.
- **Test Manager**:
    - Mock `subprocess.Popen` to return a dummy PID.
    - Verify `start_workspace` inserts into DB.
    - Verify `stop_workspace` attempts to kill PID and removes from DB.

### Manual Verification
1.  **Start Workspace**: Run `qs start <name>`.
2.  **Verify DB**: Check if PIDs are stored in `active_processes`.
3.  **Check Process**: Verify the app is actually running.
4.  **Stop Workspace**: Run `qs stop <name>`.
5.  **Verify Termination**: Check if the app closes (for simple apps like Notepad/Calc).
6.  **Edge Cases**: Test with "launcher" type apps (e.g. Chrome) to confirm the "Limitation" behavior.

