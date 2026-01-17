# Implementation Plan - Usage Analytics

## Goal
Implement a usage tracking system to monitor how long workspaces are active. This involves recording session durations when a workspace is stopped and aggregating this data to show total usage time.

## User Review Required
> [!NOTE]
> Usage time is calculated based on the "Active Process" duration. If a workspace is started but the process dies silently (outside of `qs stop`), that session might not be recorded accurately until the zombie entry is cleaned up or treated as "crashed". For this iteration, we assume usage is recorded only on explicit `qs stop`.

## Proposed Changes

### Database Schema
#### [MODIFY] `database_manager.py`
- Create a new table `workspace_usage` to store historical session data.
- Add `total_usage_seconds` column to `workspaces` table for quick aggregation.

```sql
CREATE TABLE workspace_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id INTEGER,
    started_at DATETIME,
    ended_at DATETIME,
    duration_seconds INTEGER,
    FOREIGN KEY(workspace_id) REFERENCES workspaces(id)
);

-- Migration for existing active_processes table if needed, or just new logic
ALTER TABLE workspaces ADD COLUMN total_usage_seconds INTEGER DEFAULT 0;
```

### Logic Layer
#### [MODIFY] `workspace_manager.py`
- **Method `stop_workspace(name)`**:
    - When iterating through active processes to stop them:
        - Calculate `session_duration = current_time - process_started_at`.
        - Insert record into `workspace_usage (workspace_id, started_at, ended_at, duration_seconds)`.
        - Update `workspaces` table: `total_usage_seconds = total_usage_seconds + session_duration`.
- **Method `get_workspace_stats(name)`** (Optional/Internal):
    - Helper to retrieve usage stats if needed.

### CLI Layer
#### [MODIFY] `main.py`
- **Command `ls`**:
    - Update the table view to include a "Total Usage" column.
    - Format seconds into human-readable string (e.g., "2h 15m").

### Timezone Display
#### [MODIFY] `utils.py`
- Add `utc_to_local_str(utc_str)` function:
  - Parse DB string as UTC.
  - Convert to local system timezone.
  - Return formatted string (YYYY-MM-DD HH:MM:SS).

#### [MODIFY] `main.py`
- Use `utc_to_local_str` for "Created" and "Last Activated" columns in `ls` command.

## Verification Plan

### Automated Tests
- **Test DB**: Verify `workspace_usage` table creation and `workspaces` column addition.
- **Test Usage Recording**:
    - Start a mock workspace.
    - Wait nominal time.
    - Stop workspace.
    - Verify `workspace_usage` has a new row with correct duration.
    - Verify `workspaces.total_usage_seconds` is updated.
- **Test Timezone**:
    - Verify `ls` outputs current system time for a newly started workspace.

### Manual Verification
1.  **Start**: `qs start <name>`.
2.  **Wait**: Let it run for ~1 minute.
3.  **Stop**: `qs stop <name>`.
4.  **Verify**: Run `qs ls` and check if "Total Usage" shows "1m".
5.  **Accumulate**: Start/Stop again and verify the time adds up.
