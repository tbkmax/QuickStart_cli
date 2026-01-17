import sqlite3
import contextlib
from .config import DB_PATH

class DatabaseManager:
    def __init__(self):
        self.db_path = DB_PATH

    def initialize_db(self):
        """Create tables if they don't exist."""
        create_workspaces_table = """
        CREATE TABLE IF NOT EXISTS workspaces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_activated_at DATETIME,
            activate_count INTEGER DEFAULT 0
        );
        """
        create_files_table = """
        CREATE TABLE IF NOT EXISTS workspace_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workspace_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            FOREIGN KEY (workspace_id) REFERENCES workspaces (id) ON DELETE CASCADE
        );
        """
        create_processes_table = """
        CREATE TABLE IF NOT EXISTS active_processes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workspace_id INTEGER,
            pid INTEGER,
            file_path TEXT,
            started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(workspace_id) REFERENCES workspaces(id)
        );
        """
        with self.get_connection() as conn:
            conn.execute(create_workspaces_table)
            conn.execute(create_files_table)
            conn.execute(create_processes_table)

    @contextlib.contextmanager
    def get_connection(self):
        """Yields a database connection."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def execute_query(self, query: str, params: tuple = ()):
        """Executes a write query."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.lastrowid

    def fetch_all(self, query: str, params: tuple = ()):
        """Executes a read query and returns all results."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def fetch_one(self, query: str, params: tuple = ()):
        """Executes a read query and returns one result."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
