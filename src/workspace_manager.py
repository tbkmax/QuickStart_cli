import os
import subprocess
import psutil
import datetime
from typing import List, Optional
from .database_manager import DatabaseManager
from .utils import open_file_picker

class WorkspaceManager:
    def __init__(self):
        self.db = DatabaseManager()
        self.db.initialize_db()

    def create_workspace(self, name: str, file_paths: List[str]) -> bool:
        """Creates a new workspace with the given files."""
        if not file_paths:
            return False

        try:
            # Insert workspace
            workspace_id = self.db.execute_query(
                "INSERT INTO workspaces (name) VALUES (?)", (name,)
            )

            # Insert files
            for path in file_paths:
                self.db.execute_query(
                    "INSERT INTO workspace_files (workspace_id, file_path) VALUES (?, ?)",
                    (workspace_id, path)
                )
            return True
        except Exception as e:
            # If unique constraint failed (name exists) or other error
            print(f"Error creating workspace: {e}")
            return False

    def list_workspaces(self) -> List[dict]:
        """Returns a list of all workspaces with their details."""
        query = """
        SELECT w.name, w.created_at, w.last_activated_at, w.activate_count, count(wf.id) as file_count
        FROM workspaces w
        LEFT JOIN workspace_files wf ON w.id = wf.workspace_id
        GROUP BY w.id
        ORDER BY w.last_activated_at DESC
        """
        rows = self.db.fetch_all(query)
        result = []
        for row in rows:
            result.append({
                "name": row[0],
                "created_at": row[1],
                "last_activated_at": row[2],
                "activate_count": row[3],
                "file_count": row[4]
            })
        return result

    def start_workspace(self, name: str) -> bool:
        """Launches all files in the workspace and tracks processes."""
        workspace = self.db.fetch_one("SELECT id FROM workspaces WHERE name = ?", (name,))
        if not workspace:
            print(f"Workspace '{name}' not found.")
            return False
        
        workspace_id = workspace[0]
        
        files = self.db.fetch_all("SELECT file_path FROM workspace_files WHERE workspace_id = ?", (workspace_id,))
        if not files:
            print(f"No files found for workspace '{name}'.")
            return False

        success = True
        for (path,) in files:
            try:
                # Use subprocess.Popen to get PID
                # shell=True is often needed for opening files with default app on Windows via 'start' logic
                # But 'start' is a shell command. 
                # Better: usage of os.startfile is "fire and forget" and doesn't give PID easily.
                # using Popen with executable might be needed, or 'cmd /c start' which also makes PID tracking hard.
                # However, for executables, Popen works well. For documents, shell=True works but PID might be the shell.
                
                # Plan says: "Switching to subprocess.Popen ... Limitation: ... captured PID will be invalid (dead)"
                # We will try Popen directly. If it's a non-executable (like .txt), we need shell=True on Windows.
                
                # Use DETACHED_PROCESS (0x00000008) to prevent console attachment on Windows
                creation_flags = 0x00000008 if os.name == 'nt' else 0

                proc = subprocess.Popen(
                    [path], 
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    creationflags=creation_flags
                ) 
                
                # Store PID
                self.db.execute_query(
                    "INSERT INTO active_processes (workspace_id, pid, file_path) VALUES (?, ?, ?)",
                    (workspace_id, proc.pid, path)
                )
                
            except OSError as e:
                print(f"Failed to open '{path}': {e}")
                success = False
        
        # Update usage stats
        now = datetime.datetime.now()
        self.db.execute_query(
            "UPDATE workspaces SET last_activated_at = ?, activate_count = activate_count + 1 WHERE id = ?",
            (now, workspace_id)
        )
        return success

    def stop_workspace(self, name: str) -> bool:
        """Terminates all running processes for a workspace."""
        workspace = self.db.fetch_one("SELECT id FROM workspaces WHERE name = ?", (name,))
        if not workspace:
            print(f"Workspace '{name}' not found.")
            return False
            
        workspace_id = workspace[0]
        
        # Get active processes
        processes = self.db.fetch_all(
            "SELECT id, pid, file_path FROM active_processes WHERE workspace_id = ?", 
            (workspace_id,)
        )
        
        if not processes:
            print(f"No active processes found for workspace '{name}'.")
            return True # Not an error, just nothing to stop
            
        for proc_id, pid, path in processes:
            try:
                if psutil.pid_exists(pid):
                    parent = psutil.Process(pid)
                    # Kill children (if any)
                    for child in parent.children(recursive=True):
                        child.terminate()
                    parent.terminate()
                else:
                    pass
            except Exception as e:
                print(f"Error terminating process {pid}: {e}")
            
            # Remove from DB regardless of whether it was running (cleanup)
            self.db.execute_query("DELETE FROM active_processes WHERE id = ?", (proc_id,))
            
        return True

    def get_active_workspaces(self) -> List[dict]:
        """Returns a list of workspaces that have active processes."""
        # Simple distinct check
        query = """
        SELECT DISTINCT w.name 
        FROM active_processes ap
        JOIN workspaces w ON ap.workspace_id = w.id
        """
        rows = self.db.fetch_all(query)
        return [row[0] for row in rows]

    def delete_workspace(self, name: str) -> bool:
        """Deletes a workspace and its associated files."""
        workspace = self.db.fetch_one("SELECT id FROM workspaces WHERE name = ?", (name,))
        if not workspace:
             print(f"Workspace '{name}' not found.")
             return False
        
        # Cascading delete is set up in schema, but to be sure we can delete parent
        try:
            self.db.execute_query("DELETE FROM workspaces WHERE name = ?", (name,))
            return True
        except Exception as e:
            print(f"Error deleting workspace: {e}")
            return False
