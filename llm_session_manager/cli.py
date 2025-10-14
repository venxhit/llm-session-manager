"""CLI interface for LLM Session Manager using Typer."""

import json
import sys
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import structlog

from .core.session_discovery import SessionDiscovery
from .core.health_monitor import HealthMonitor
from .utils.token_estimator import TokenEstimator
from .storage.database import Database
from .ui.dashboard import Dashboard
from .models import Session

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ]
)

logger = structlog.get_logger()
console = Console()

# Create Typer app
app = typer.Typer(
    name="llm-session",
    help="LLM Session Manager - Track and manage AI coding assistant sessions",
    add_completion=False
)


def get_components():
    """Initialize and return all core components.

    Returns:
        Tuple of (Database, SessionDiscovery, HealthMonitor, TokenEstimator)
    """
    db = Database()
    db.init_db()

    discovery = SessionDiscovery()
    health_monitor = HealthMonitor()
    token_estimator = TokenEstimator()

    return db, discovery, health_monitor, token_estimator


@app.command()
def monitor(
    refresh_interval: int = typer.Option(5, "--interval", "-i", help="Refresh interval in seconds")
):
    """Start the real-time dashboard for monitoring sessions.

    The dashboard auto-refreshes and displays:
    - Active sessions
    - Token usage
    - Health scores
    - Duration

    Keyboard shortcuts:
    - q: Quit
    - r: Force refresh
    - h: Show help
    """
    console.print("\n[cyan]Initializing LLM Session Manager...[/cyan]\n")

    try:
        # Initialize components
        db, discovery, health_monitor, token_estimator = get_components()

        # Create dashboard
        dashboard = Dashboard(
            discovery=discovery,
            health_monitor=health_monitor,
            token_estimator=token_estimator,
            refresh_interval=refresh_interval
        )

        # Run dashboard
        dashboard.run_dashboard()

    except Exception as e:
        console.print(f"[red]Error starting dashboard: {e}[/red]")
        logger.error("dashboard_start_failed", error=str(e))
        raise typer.Exit(code=1)


@app.command()
def list(
    format: str = typer.Option("table", "--format", "-f", help="Output format: table or json"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status: active, idle, etc.")
):
    """List all active LLM coding sessions.

    Displays session information including:
    - Session ID and type
    - Process ID
    - Status and duration
    - Token usage
    - Health score
    """
    try:
        # Initialize components
        db, discovery, health_monitor, token_estimator = get_components()

        # Discover sessions
        console.print("[dim]Discovering sessions...[/dim]")
        sessions = discovery.discover_sessions()

        if not sessions:
            console.print("[yellow]No active sessions found.[/yellow]")
            return

        # Update metrics
        token_estimator.update_token_counts(sessions)
        health_monitor.update_health_scores(sessions)

        # Filter by status if specified
        if status:
            sessions = [s for s in sessions if s.status.value == status.lower()]
            if not sessions:
                console.print(f"[yellow]No sessions with status '{status}' found.[/yellow]")
                return

        # Display based on format
        if format == "json":
            # JSON output
            sessions_data = [s.to_dict() for s in sessions]
            console.print_json(data=sessions_data)
        else:
            # Table output
            table = Table(
                title=f"Active Sessions ({len(sessions)})",
                show_header=True,
                header_style="bold cyan"
            )

            table.add_column("ID", style="dim", width=30)
            table.add_column("Type", style="cyan")
            table.add_column("PID", justify="right")
            table.add_column("Status", justify="center")
            table.add_column("Duration")
            table.add_column("Tokens", justify="right")
            table.add_column("Health", justify="center")

            for session in sorted(sessions, key=lambda s: s.health_score):
                # Calculate duration
                from datetime import datetime
                duration = datetime.now() - session.start_time
                hours = int(duration.total_seconds() // 3600)
                minutes = int((duration.total_seconds() % 3600) // 60)
                duration_str = f"{hours}h {minutes}m"

                # Token percentage
                token_pct = (session.token_count / session.token_limit * 100) if session.token_limit > 0 else 0

                # Health emoji
                health_score = session.health_score / 100
                emoji = "✅" if health_score >= 0.7 else "⚠️" if health_score >= 0.4 else "🔴"

                # Status color
                status_colors = {"active": "green", "idle": "yellow", "waiting": "blue", "error": "red"}
                status_color = status_colors.get(session.status.value, "white")

                table.add_row(
                    session.id[:28] + "..." if len(session.id) > 30 else session.id,
                    session.type.value,
                    str(session.pid),
                    f"[{status_color}]{session.status.value}[/{status_color}]",
                    duration_str,
                    f"{session.token_count:,} ({token_pct:.0f}%)",
                    f"{emoji} {session.health_score:.0f}%"
                )

            console.print(table)

    except Exception as e:
        console.print(f"[red]Error listing sessions: {e}[/red]")
        logger.error("list_sessions_failed", error=str(e))
        raise typer.Exit(code=1)


@app.command()
def export(
    session_id: str = typer.Argument(..., help="Session ID to export"),
    output: str = typer.Option("context.json", "--output", "-o", help="Output file path")
):
    """Export session context to a JSON file.

    Creates a JSON file containing:
    - Session metadata
    - Token usage
    - Health metrics
    - Working directory files
    """
    try:
        # Initialize components
        db, discovery, health_monitor, token_estimator = get_components()

        # Discover sessions
        console.print(f"[dim]Searching for session: {session_id}...[/dim]")
        sessions = discovery.discover_sessions()

        # Find matching session
        session = None
        for s in sessions:
            if s.id == session_id or s.id.startswith(session_id):
                session = s
                break

        if not session:
            console.print(f"[red]Session '{session_id}' not found.[/red]")
            raise typer.Exit(code=1)

        # Update metrics
        token_estimator.update_token_counts([session])
        health_monitor.update_health_scores([session])

        # Create export data
        from datetime import datetime
        export_data = {
            "session_id": session.id,
            "timestamp": datetime.now().isoformat(),
            "type": session.type.value,
            "context": {
                "pid": session.pid,
                "status": session.status.value,
                "start_time": session.start_time.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "working_directory": session.working_directory,
                "token_count": session.token_count,
                "token_limit": session.token_limit,
                "health_score": session.health_score,
                "message_count": session.message_count,
                "file_count": session.file_count,
                "error_count": session.error_count,
                "messages": [
                    f"Placeholder message from session {session.id}"
                ],
                "files": [],
                "metadata": {
                    "export_tool": "llm-session-manager",
                    "export_version": "0.1.0"
                }
            }
        }

        # List files in working directory if available
        if session.working_directory and Path(session.working_directory).exists():
            try:
                files = []
                for f in Path(session.working_directory).rglob("*.py"):
                    if not any(p in f.parts for p in ["__pycache__", ".git", "venv", "node_modules"]):
                        files.append(str(f.relative_to(session.working_directory)))
                export_data["context"]["files"] = files[:50]  # Limit to 50 files
            except Exception as e:
                logger.warning("failed_to_list_files", error=str(e))

        # Write to file
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)

        console.print(f"[green]✓[/green] Session exported to: [cyan]{output_path}[/cyan]")
        console.print(f"  Session ID: {session.id}")
        console.print(f"  Type: {session.type.value}")
        console.print(f"  Tokens: {session.token_count:,}")
        console.print(f"  Health: {session.health_score:.0f}%")

    except Exception as e:
        console.print(f"[red]Error exporting session: {e}[/red]")
        logger.error("export_session_failed", error=str(e))
        raise typer.Exit(code=1)


@app.command()
def import_context(
    input: str = typer.Argument(..., help="Input JSON file path"),
    session_id: Optional[str] = typer.Option(None, "--session-id", "-s", help="Override session ID")
):
    """Import session context from a JSON file.

    Reads a previously exported session file and displays the context.
    """
    try:
        # Read JSON file
        input_path = Path(input)
        if not input_path.exists():
            console.print(f"[red]File not found: {input}[/red]")
            raise typer.Exit(code=1)

        console.print(f"[dim]Reading from: {input_path}...[/dim]")

        with open(input_path, 'r') as f:
            data = json.load(f)

        # Validate format
        required_fields = ["session_id", "timestamp", "type", "context"]
        missing = [f for f in required_fields if f not in data]
        if missing:
            console.print(f"[red]Invalid format. Missing fields: {', '.join(missing)}[/red]")
            raise typer.Exit(code=1)

        # Override session ID if provided
        if session_id:
            data["session_id"] = session_id

        # Display imported data
        console.print("\n[green]✓[/green] Context imported successfully!\n")

        panel_text = Text()
        panel_text.append("Session ID: ", style="bold")
        panel_text.append(f"{data['session_id']}\n", style="cyan")
        panel_text.append("Type: ", style="bold")
        panel_text.append(f"{data['type']}\n", style="cyan")
        panel_text.append("Timestamp: ", style="bold")
        panel_text.append(f"{data['timestamp']}\n", style="dim")

        context = data["context"]
        panel_text.append("\nWorking Dir: ", style="bold")
        panel_text.append(f"{context.get('working_directory', 'N/A')}\n", style="dim")
        panel_text.append("Tokens: ", style="bold")
        panel_text.append(f"{context.get('token_count', 0):,}\n", style="yellow")
        panel_text.append("Health: ", style="bold")
        panel_text.append(f"{context.get('health_score', 0):.0f}%\n", style="green")
        panel_text.append("Files: ", style="bold")
        panel_text.append(f"{len(context.get('files', []))} files\n", style="cyan")

        console.print(Panel(panel_text, title="Imported Session Context", border_style="green"))

    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON format: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Error importing context: {e}[/red]")
        logger.error("import_context_failed", error=str(e))
        raise typer.Exit(code=1)


@app.command()
def health(
    session_id: str = typer.Argument(..., help="Session ID to analyze")
):
    """Show detailed health breakdown for a session.

    Displays:
    - Overall health score
    - Component scores (tokens, duration, activity, errors)
    - Metrics and recommendations
    """
    try:
        # Initialize components
        db, discovery, health_monitor, token_estimator = get_components()

        # Discover sessions
        console.print(f"[dim]Searching for session: {session_id}...[/dim]")
        sessions = discovery.discover_sessions()

        # Find matching session
        session = None
        for s in sessions:
            if s.id == session_id or s.id.startswith(session_id):
                session = s
                break

        if not session:
            console.print(f"[red]Session '{session_id}' not found.[/red]")
            raise typer.Exit(code=1)

        # Update metrics
        token_estimator.update_token_counts([session])
        health_monitor.update_health_scores([session])

        # Get health summary
        health_score = session.health_score / 100
        summary = health_monitor.get_health_summary(session)

        # Display header
        console.print()
        console.print(f"[bold cyan]Health Report: {session.id[:40]}...[/bold cyan]")
        console.print()

        # Overall health
        overall = Panel(
            f"{summary['emoji']} [bold]{summary['overall_percentage']:.1f}%[/bold] - {summary['status'].upper()}",
            title="Overall Health",
            border_style=summary['color']
        )
        console.print(overall)
        console.print()

        # Component scores
        console.print("[bold]Component Scores:[/bold]")
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Component", style="cyan")
        table.add_column("Bar")
        table.add_column("Score", justify="right")

        for component, score in summary['component_scores'].items():
            bar_length = 20
            filled = int(score * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)

            color = "green" if score >= 0.7 else "yellow" if score >= 0.4 else "red"

            table.add_row(
                component.capitalize(),
                f"[{color}]{bar}[/{color}]",
                f"[{color}]{score * 100:.0f}%[/{color}]"
            )

        console.print(table)
        console.print()

        # Metrics
        console.print("[bold]Metrics:[/bold]")
        metrics = summary['metrics']
        console.print(f"  Duration:        {metrics['duration_hours']:.1f} hours")
        console.print(f"  Idle Time:       {metrics['idle_minutes']:.1f} minutes")
        console.print(f"  Token Usage:     {metrics['token_usage_percent']:.1f}%")
        console.print(f"  Error Count:     {metrics['error_count']}")
        console.print()

        # Recommendations
        if summary['recommendations']:
            console.print("[bold yellow]⚠️  Recommendations:[/bold yellow]")
            for rec in summary['recommendations']:
                console.print(f"  • {rec}")
            console.print()
        else:
            console.print("[green]✅ No recommendations - session is healthy![/green]")
            console.print()

        # Restart recommendation
        should_restart, reason = health_monitor.should_restart_session(session)
        if should_restart:
            console.print(f"[bold red]🔄 RESTART RECOMMENDED: {reason}[/bold red]\n")

    except Exception as e:
        console.print(f"[red]Error analyzing health: {e}[/red]")
        logger.error("health_check_failed", error=str(e))
        raise typer.Exit(code=1)


@app.command()
def info():
    """Show information about the tool."""
    console.print("\n[bold cyan]LLM Session Manager[/bold cyan]")
    console.print("Version: 0.1.0")
    console.print()
    console.print("A CLI tool for tracking and managing multiple AI coding assistant sessions.")
    console.print()
    console.print("[bold]Features:[/bold]")
    console.print("  • Real-time session monitoring")
    console.print("  • Token usage tracking")
    console.print("  • Health scoring")
    console.print("  • Context export/import")
    console.print()
    console.print("[bold]Commands:[/bold]")
    console.print("  monitor       - Start the real-time dashboard")
    console.print("  list          - List all active sessions")
    console.print("  export        - Export session context")
    console.print("  import-context- Import session context")
    console.print("  health        - Show health details")
    console.print()
    console.print("Run [cyan]llm-session --help[/cyan] for more information.\n")


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
