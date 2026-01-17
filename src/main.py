import typer
from rich.console import Console
from rich.table import Table
from typing import Optional
from .workspace_manager import WorkspaceManager
from .utils import open_file_picker

app = typer.Typer(help="QuickStart CLI - Manage and launch your workspaces.")
console = Console()
manager = WorkspaceManager()

@app.command()
def ls():
    """List all workspaces."""
    workspaces = manager.list_workspaces()
    if not workspaces:
        console.print("[yellow]No workspaces found.[/yellow]")
        return

    table = Table(title="Workspaces")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Status", style="yellow")
    table.add_column("Files", justify="right", style="magenta")
    table.add_column("Created", style="green")
    table.add_column("Last Activated", style="blue")
    table.add_column("Count", justify="right")

    active_workspaces = manager.get_active_workspaces()
    for wk in workspaces:
        status = "[green]Running[/green]" if wk['name'] in active_workspaces else "Stopped"
        last_active = str(wk['last_activated_at']) if wk['last_activated_at'] else "-"
        table.add_row(
            wk['name'],
            status,
            str(wk['file_count']),
            str(wk['created_at']),
            last_active,
            str(wk['activate_count'])
        )

    console.print(table)

@app.command()
def build():
    """Create a new workspace interactively."""
    name = typer.prompt("Enter workspace name (unique, no spaces)")
    if " " in name:
        console.print("[red]Error: Workspace name cannot contain spaces.[/red]")
        return

    # Check if exists (simplified check via listing or just try to insert later)
    # We rely on manager to catch duplicate error, or check here if we want better UX
    
    files = []
    while True:
        if not files:
            console.print("Please select the first file for this workspace.")
        else:
            confirm = typer.confirm("Do you want to add another file?")
            if not confirm:
                break
        
        path = open_file_picker()
        if path:
            console.print(f"[green]Added:[/green] {path}")
            files.append(path)
        else:
            console.print("[yellow]No file selected.[/yellow]")
            if not files:
                abort = typer.confirm("No files selected. Abort creation?")
                if abort:
                    return

    if files:
        if manager.create_workspace(name, files):
            console.print(f"[bold green]Workspace '{name}' created successfully![/bold green]")
        else:
            console.print("[bold red]Failed to create workspace. Name might be taken.[/bold red]")

@app.command()
def start(name: str):
    """Start a workspace."""
    # Silent success implies no output unless error
    # The manager handles printing errors
    manager.start_workspace(name)

@app.command()
def stop(name: str):
    """Stop a workspace (terminate running processes)."""
    if not manager.stop_workspace(name):
        console.print("[red]Failed to stop workspace (or it was not running).[/red]")

@app.command()
def delete(name: str):
    """Delete a workspace."""
    if typer.confirm(f"Are you sure you want to delete workspace '{name}'?"):
        if manager.delete_workspace(name):
            console.print(f"[green]Workspace '{name}' deleted.[/green]")
        else:
            console.print("[red]Failed to delete workspace.[/red]")

if __name__ == "__main__":
    app()
