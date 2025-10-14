"""CLI interface for LLM Session Manager using Typer."""

import json
import sys
from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import structlog

from .core.session_discovery import SessionDiscovery
from .core.health_monitor import HealthMonitor
from .core.memory_manager import MemoryManager
from .utils.token_estimator import TokenEstimator
from .utils.recommendations import RecommendationEngine
from .utils.auto_tagger import AutoTagger
from .storage.database import Database
from .ui.dashboard import Dashboard
from .models import Session
from .config import Config

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
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status: active, idle, etc."),
    tag: Optional[str] = typer.Option(None, "--tag", "-t", help="Filter by tag"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Filter by project name")
):
    """List all active LLM coding sessions.

    Displays session information including:
    - Session ID and type
    - Process ID
    - Status and duration
    - Token usage
    - Health score
    - Tags and project
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

        # Filter by tag if specified
        if tag:
            sessions = [s for s in sessions if s.has_tag(tag)]
            if not sessions:
                console.print(f"[yellow]No sessions with tag '{tag}' found.[/yellow]")
                return

        # Filter by project if specified
        if project:
            sessions = [s for s in sessions if s.project_name and project.lower() in s.project_name.lower()]
            if not sessions:
                console.print(f"[yellow]No sessions for project '{project}' found.[/yellow]")
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

            table.add_column("ID", style="dim", width=20)
            table.add_column("Type", style="cyan")
            table.add_column("PID", justify="right")
            table.add_column("Status", justify="center")
            table.add_column("Duration")
            table.add_column("Tokens", justify="right")
            table.add_column("Health", justify="center")
            table.add_column("Tags/Project", style="magenta")

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

                # Tags/Project display
                tags_display = []
                if session.project_name:
                    tags_display.append(f"📁 {session.project_name}")
                if session.tags:
                    tags_display.append(", ".join(f"#{t}" for t in session.tags[:2]))
                tags_str = " ".join(tags_display) if tags_display else "-"

                table.add_row(
                    session.id[:18] + "..." if len(session.id) > 20 else session.id,
                    session.type.value,
                    str(session.pid),
                    f"[{status_color}]{session.status.value}[/{status_color}]",
                    duration_str,
                    f"{session.token_count:,} ({token_pct:.0f}%)",
                    f"{emoji} {session.health_score:.0f}%",
                    tags_str
                )

            console.print(table)

    except Exception as e:
        console.print(f"[red]Error listing sessions: {e}[/red]")
        logger.error("list_sessions_failed", error=str(e))
        raise typer.Exit(code=1)


@app.command()
def export(
    session_id: str = typer.Argument(..., help="Session ID to export"),
    output: str = typer.Option("context.json", "--output", "-o", help="Output file path"),
    format: str = typer.Option("json", "--format", "-f", help="Export format: json, yaml, or markdown")
):
    """Export session context to a file.

    Creates a file containing:
    - Session metadata
    - Token usage
    - Health metrics
    - Tags and project info
    - Working directory files

    Formats:
    - json: Structured JSON data
    - yaml: YAML format
    - markdown: Human-readable report
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
            "project_name": session.project_name,
            "description": session.description,
            "tags": session.tags,
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
                    "export_version": "0.2.0"
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

        # Write to file based on format
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == "yaml":
            import yaml
            with open(output_path, 'w') as f:
                yaml.dump(export_data, f, default_flow_style=False, sort_keys=False)
        elif format == "markdown":
            # Generate Markdown report
            duration = datetime.now() - session.start_time
            hours = int(duration.total_seconds() // 3600)
            minutes = int((duration.total_seconds() % 3600) // 60)

            md_content = f"""# Session Report: {session.id}

## Overview
- **Type**: {session.type.value}
- **Status**: {session.status.value}
- **Project**: {session.project_name or 'N/A'}
- **Tags**: {', '.join(f'`{t}`' for t in session.tags) if session.tags else 'None'}
- **PID**: {session.pid}
- **Working Directory**: `{session.working_directory}`

## Timing
- **Started**: {session.start_time.strftime('%Y-%m-%d %H:%M:%S')}
- **Last Activity**: {session.last_activity.strftime('%Y-%m-%d %H:%M:%S')}
- **Duration**: {hours}h {minutes}m

## Metrics
- **Token Usage**: {session.token_count:,} / {session.token_limit:,} ({session.token_count/session.token_limit*100:.1f}%)
- **Health Score**: {session.health_score:.1f}%
- **Messages**: {session.message_count}
- **Files Tracked**: {session.file_count}
- **Errors**: {session.error_count}

## Files in Working Directory
{chr(10).join(f'- `{f}`' for f in export_data["context"]["files"][:20]) if export_data["context"]["files"] else 'No files listed'}

## Description
{session.description or 'No description provided.'}

---
*Exported by LLM Session Manager v0.2.0 on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            with open(output_path, 'w') as f:
                f.write(md_content)
        else:  # json
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)

        console.print(f"[green]✓[/green] Session exported to: [cyan]{output_path}[/cyan]")
        console.print(f"  Format: {format}")
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
def tag(
    session_id: str = typer.Argument(..., help="Session ID to tag"),
    tags: List[str] = typer.Argument(..., help="Tags to add (space-separated)")
):
    """Add tags to a session.

    Tags help organize and filter sessions. You can add multiple tags at once.

    Example:
        llm-session tag abc123 backend api feature-xyz
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

        # Add tags
        for t in tags:
            session.add_tag(t)

        # Save to database
        db.update_session(session)

        console.print(f"[green]✓[/green] Added {len(tags)} tag(s) to session {session.id[:20]}...")
        console.print(f"  Tags: {', '.join(f'#{t}' for t in session.tags)}")

    except Exception as e:
        console.print(f"[red]Error adding tags: {e}[/red]")
        logger.error("tag_failed", error=str(e))
        raise typer.Exit(code=1)


@app.command()
def untag(
    session_id: str = typer.Argument(..., help="Session ID to untag"),
    tags: List[str] = typer.Argument(..., help="Tags to remove (space-separated)")
):
    """Remove tags from a session.

    Example:
        llm-session untag abc123 old-tag deprecated
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

        # Remove tags
        for t in tags:
            session.remove_tag(t)

        # Save to database
        db.update_session(session)

        console.print(f"[green]✓[/green] Removed {len(tags)} tag(s) from session {session.id[:20]}...")
        console.print(f"  Remaining tags: {', '.join(f'#{t}' for t in session.tags) if session.tags else 'none'}")

    except Exception as e:
        console.print(f"[red]Error removing tags: {e}[/red]")
        logger.error("untag_failed", error=str(e))
        raise typer.Exit(code=1)


@app.command()
def set_project(
    session_id: str = typer.Argument(..., help="Session ID to update"),
    project_name: str = typer.Argument(..., help="Project name")
):
    """Set the project name for a session.

    Example:
        llm-session set-project abc123 "My Web App"
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

        # Set project
        session.set_project(project_name)

        # Save to database
        db.update_session(session)

        console.print(f"[green]✓[/green] Set project for session {session.id[:20]}...")
        console.print(f"  Project: 📁 {session.project_name}")

    except Exception as e:
        console.print(f"[red]Error setting project: {e}[/red]")
        logger.error("set_project_failed", error=str(e))
        raise typer.Exit(code=1)


@app.command()
def auto_tag(
    session_id: str = typer.Argument(..., help="Session ID to auto-tag"),
    apply: bool = typer.Option(False, "--apply", "-a", help="Apply tags automatically without confirmation")
):
    """Suggest tags for a session based on file content analysis.

    Analyzes file extensions, imports, keywords, and directory structure
    to suggest relevant tags.

    Example:
        llm-session auto-tag abc123          # Show suggestions
        llm-session auto-tag abc123 --apply  # Auto-apply tags
    """
    try:
        # Initialize components
        db, discovery, health_monitor, token_estimator = get_components()
        auto_tagger = AutoTagger()

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

        # Analyze and suggest tags
        console.print(f"[dim]Analyzing session content...[/dim]\n")
        suggested_tags = auto_tagger.suggest_tags(session, max_tags=10)

        if not suggested_tags:
            console.print("[yellow]No tags suggested. Session may not have a working directory or analyzable files.[/yellow]")
            return

        # Show suggestions
        console.print(f"[bold cyan]Suggested tags for session {session.id[:20]}...[/bold cyan]\n")

        # Separate existing vs new tags
        existing_tags = set(session.tags)
        new_tags = [t for t in suggested_tags if t not in existing_tags]
        already_tagged = [t for t in suggested_tags if t in existing_tags]

        if new_tags:
            console.print("[bold]New tag suggestions:[/bold]")
            for i, tag in enumerate(new_tags, 1):
                console.print(f"  {i}. [magenta]#{tag}[/magenta]")
        else:
            console.print("[green]Session already has all suggested tags![/green]")

        if already_tagged:
            console.print(f"\n[dim]Already tagged: {', '.join(f'#{t}' for t in already_tagged)}[/dim]")

        if not new_tags:
            return

        # Apply tags if requested or confirmed
        if apply:
            should_apply = True
        else:
            console.print()
            should_apply = typer.confirm("Apply these tags?", default=True)

        if should_apply:
            for tag in new_tags:
                session.add_tag(tag)
            db.update_session(session)

            console.print(f"\n[green]✓[/green] Applied {len(new_tags)} tags to session")
            console.print(f"  All tags: {', '.join(f'#{t}' for t in session.tags)}")
        else:
            console.print("[dim]Tags not applied.[/dim]")

    except Exception as e:
        console.print(f"[red]Error auto-tagging: {e}[/red]")
        logger.error("auto_tag_failed", error=str(e))
        raise typer.Exit(code=1)


@app.command()
def describe(
    session_id: str = typer.Argument(..., help="Session ID to describe"),
    description: str = typer.Argument(..., help="Session description")
):
    """Add or update a session description.

    Example:
        llm-session describe abc123 "Working on authentication feature for the API"
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

        # Set description
        session.description = description

        # Save to database
        db.update_session(session)

        console.print(f"[green]✓[/green] Description updated for session {session.id[:20]}...")
        console.print(f"  Description: {description}")

    except Exception as e:
        console.print(f"[red]Error setting description: {e}[/red]")
        logger.error("describe_failed", error=str(e))
        raise typer.Exit(code=1)


@app.command()
def init_config():
    """Initialize configuration file with defaults.

    Creates a default config.yaml file at:
    ~/.config/llm-session-manager/config.yaml

    This file can be edited to customize:
    - Token limits
    - Health score weights
    - Dashboard settings
    - Warning thresholds
    """
    try:
        config = Config()

        if config.config_path.exists():
            overwrite = typer.confirm(
                f"Config file already exists at {config.config_path}. Overwrite?",
                default=False
            )
            if not overwrite:
                console.print("[yellow]Configuration creation cancelled.[/yellow]")
                return

        config.create_default_config()

        console.print(f"[green]✓[/green] Configuration file created: [cyan]{config.config_path}[/cyan]")
        console.print()
        console.print("[bold]Default configuration includes:[/bold]")
        console.print("  • Token limits for Claude, Cursor, GitHub Copilot")
        console.print("  • Health scoring weights")
        console.print("  • Warning and critical thresholds")
        console.print("  • Dashboard preferences")
        console.print()
        console.print(f"Edit the file to customize your settings:")
        console.print(f"  [dim]{config.config_path}[/dim]")

    except Exception as e:
        console.print(f"[red]Error creating config: {e}[/red]")
        logger.error("config_creation_failed", error=str(e))
        raise typer.Exit(code=1)


@app.command()
def show_config():
    """Show current configuration values."""
    try:
        config = Config()

        console.print()
        console.print(f"[bold cyan]Configuration[/bold cyan] ([dim]{config.config_path}[/dim])")
        console.print()

        # Token Limits
        console.print("[bold]Token Limits:[/bold]")
        for plan, limit in config.get("token_limits", {}).items():
            console.print(f"  {plan:20s}: {limit:,} tokens")
        console.print()

        # Health Weights
        console.print("[bold]Health Weights:[/bold]")
        for component, weight in config.get("health_weights", {}).items():
            console.print(f"  {component:20s}: {weight:.2f}")
        console.print()

        # Thresholds
        console.print("[bold]Thresholds:[/bold]")
        for threshold, value in config.get("thresholds", {}).items():
            if "minutes" in threshold:
                console.print(f"  {threshold:25s}: {value:.0f} minutes")
            else:
                console.print(f"  {threshold:25s}: {value:.1%}")
        console.print()

        # Dashboard
        console.print("[bold]Dashboard:[/bold]")
        for setting, value in config.get("dashboard", {}).items():
            console.print(f"  {setting:20s}: {value}")
        console.print()

    except Exception as e:
        console.print(f"[red]Error reading config: {e}[/red]")
        logger.error("config_read_failed", error=str(e))
        raise typer.Exit(code=1)


@app.command()
def batch_tag(
    session_pattern: str = typer.Argument(..., help="Pattern to match sessions (e.g., 'abc*' or 'all')"),
    tags: List[str] = typer.Argument(..., help="Tags to add to all matching sessions")
):
    """Add tags to multiple sessions at once.

    Use 'all' to tag all sessions, or a pattern like 'abc*' to match specific ones.

    Example:
        llm-session batch-tag all backend api
        llm-session batch-tag "test-*" testing experimental
    """
    try:
        # Initialize components
        db, discovery, health_monitor, token_estimator = get_components()

        # Discover sessions
        console.print("[dim]Discovering sessions...[/dim]")
        all_sessions = discovery.discover_sessions()

        # Filter sessions by pattern
        if session_pattern == "all":
            sessions = all_sessions
        else:
            # Simple pattern matching (prefix match)
            pattern = session_pattern.replace("*", "")
            sessions = [s for s in all_sessions if s.id.startswith(pattern)]

        if not sessions:
            console.print(f"[yellow]No sessions match pattern '{session_pattern}'[/yellow]")
            return

        # Confirm operation
        console.print(f"\n[yellow]About to tag {len(sessions)} sessions with: {', '.join(f'#{t}' for t in tags)}[/yellow]")
        confirm = typer.confirm("Continue?", default=True)
        if not confirm:
            console.print("[dim]Cancelled.[/dim]")
            return

        # Tag all sessions
        for session in sessions:
            for tag in tags:
                session.add_tag(tag)
            db.update_session(session)

        console.print(f"\n[green]✓[/green] Tagged {len(sessions)} sessions")
        for session in sessions[:5]:  # Show first 5
            console.print(f"  • {session.id[:30]}... → {', '.join(f'#{t}' for t in session.tags)}")
        if len(sessions) > 5:
            console.print(f"  ... and {len(sessions) - 5} more")

    except Exception as e:
        console.print(f"[red]Error batch tagging: {e}[/red]")
        logger.error("batch_tag_failed", error=str(e))
        raise typer.Exit(code=1)


@app.command()
def batch_export(
    session_pattern: str = typer.Argument(..., help="Pattern to match sessions"),
    output_dir: str = typer.Option("exports", "--output-dir", "-o", help="Output directory"),
    format: str = typer.Option("json", "--format", "-f", help="Export format: json, yaml, or markdown")
):
    """Export multiple sessions at once.

    Example:
        llm-session batch-export all --output-dir ./exports --format json
        llm-session batch-export "project-*" --format markdown
    """
    try:
        from pathlib import Path

        # Initialize components
        db, discovery, health_monitor, token_estimator = get_components()

        # Discover sessions
        console.print("[dim]Discovering sessions...[/dim]")
        all_sessions = discovery.discover_sessions()

        # Filter sessions
        if session_pattern == "all":
            sessions = all_sessions
        else:
            pattern = session_pattern.replace("*", "")
            sessions = [s for s in all_sessions if s.id.startswith(pattern)]

        if not sessions:
            console.print(f"[yellow]No sessions match pattern '{session_pattern}'[/yellow]")
            return

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Confirm
        console.print(f"\n[yellow]About to export {len(sessions)} sessions to {output_path}[/yellow]")
        confirm = typer.confirm("Continue?", default=True)
        if not confirm:
            console.print("[dim]Cancelled.[/dim]")
            return

        # Update metrics
        token_estimator.update_token_counts(sessions)
        health_monitor.update_health_scores(sessions)

        # Export each session
        for session in sessions:
            # Determine filename
            filename = f"{session.id[:20]}.{format}"
            file_path = output_path / filename

            # Create export data
            from datetime import datetime as dt
            export_data = {
                "session_id": session.id,
                "timestamp": dt.now().isoformat(),
                "type": session.type.value,
                "project_name": session.project_name,
                "description": session.description,
                "tags": session.tags,
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
                }
            }

            # Write based on format
            if format == "yaml":
                import yaml
                with open(file_path, 'w') as f:
                    yaml.dump(export_data, f, default_flow_style=False)
            elif format == "markdown":
                duration = dt.now() - session.start_time
                hours = int(duration.total_seconds() // 3600)
                minutes = int((duration.total_seconds() % 3600) // 60)

                md_content = f"""# Session Report: {session.id}

## Overview
- **Type**: {session.type.value}
- **Status**: {session.status.value}
- **Project**: {session.project_name or 'N/A'}
- **Tags**: {', '.join(f'`{t}`' for t in session.tags) if session.tags else 'None'}

## Metrics
- **Token Usage**: {session.token_count:,} / {session.token_limit:,} ({session.token_count/session.token_limit*100:.1f}%)
- **Health Score**: {session.health_score:.1f}%
- **Duration**: {hours}h {minutes}m

## Description
{session.description or 'No description'}
"""
                with open(file_path, 'w') as f:
                    f.write(md_content)
            else:  # json
                with open(file_path, 'w') as f:
                    json.dump(export_data, f, indent=2)

        console.print(f"\n[green]✓[/green] Exported {len(sessions)} sessions to {output_path}/")

    except Exception as e:
        console.print(f"[red]Error batch exporting: {e}[/red]")
        logger.error("batch_export_failed", error=str(e))
        raise typer.Exit(code=1)


@app.command()
def memory_add(
    session_id: str = typer.Argument(..., help="Session ID to save memory from"),
    content: str = typer.Argument(..., help="Memory content to save"),
    tags: Optional[List[str]] = typer.Option(None, "--tag", "-t", help="Tags for categorization")
):
    """Save important knowledge from a session to cross-session memory.

    This allows other sessions to find and use this knowledge later.

    Example:
        llm-session memory-add abc123 "Implemented JWT auth using jose library" --tag auth --tag backend
    """
    try:
        memory_mgr = MemoryManager()

        if not memory_mgr.is_available():
            console.print("[red]Memory system not available. ChromaDB may not be installed.[/red]")
            console.print("[yellow]Install with: poetry add chromadb[/yellow]")
            raise typer.Exit(code=1)

        memory_id = memory_mgr.add_memory(
            session_id=session_id,
            content=content,
            tags=tags or []
        )

        console.print(f"[green]✓[/green] Memory saved!")
        console.print(f"  Memory ID: {memory_id}")
        console.print(f"  Session: {session_id[:30]}...")
        console.print(f"  Content: {content[:100]}{'...' if len(content) > 100 else ''}")
        if tags:
            console.print(f"  Tags: {', '.join(f'#{t}' for t in tags)}")

    except Exception as e:
        console.print(f"[red]Error saving memory: {e}[/red]")
        logger.error("memory_add_failed", error=str(e))
        raise typer.Exit(code=1)


@app.command()
def memory_search(
    query: str = typer.Argument(..., help="What to search for"),
    limit: int = typer.Option(5, "--limit", "-n", help="Number of results"),
    session: Optional[str] = typer.Option(None, "--session", "-s", help="Filter by session ID")
):
    """Search across all session memories using semantic search.

    Finds relevant knowledge from past sessions based on meaning, not just keywords.

    Example:
        llm-session memory-search "how to implement authentication"
        llm-session memory-search "database setup" --limit 3
    """
    try:
        memory_mgr = MemoryManager()

        if not memory_mgr.is_available():
            console.print("[red]Memory system not available. ChromaDB may not be installed.[/red]")
            raise typer.Exit(code=1)

        console.print(f"[dim]Searching for: {query}...[/dim]\n")

        memories = memory_mgr.search_memories(
            query=query,
            limit=limit,
            session_id=session
        )

        if not memories:
            console.print("[yellow]No memories found.[/yellow]")
            return

        console.print(f"[bold cyan]Found {len(memories)} relevant memories:[/bold cyan]\n")

        for i, memory in enumerate(memories, 1):
            relevance = memory['relevance'] * 100
            session_id = memory['metadata'].get('session_id', 'unknown')
            timestamp = memory['metadata'].get('timestamp', 'unknown')

            # Determine relevance color
            if relevance >= 80:
                rel_color = "green"
            elif relevance >= 60:
                rel_color = "yellow"
            else:
                rel_color = "red"

            panel_text = Text()
            panel_text.append(f"{memory['content']}\n\n", style="white")
            panel_text.append("From: ", style="bold dim")
            panel_text.append(f"{session_id[:30]}...\n", style="dim")
            panel_text.append("When: ", style="bold dim")
            panel_text.append(f"{timestamp}\n", style="dim")
            if memory['tags']:
                panel_text.append("Tags: ", style="bold dim")
                panel_text.append(f"{', '.join(f'#{t}' for t in memory['tags'])}", style="magenta")

            console.print(Panel(
                panel_text,
                title=f"Memory {i} (Relevance: [{rel_color}]{relevance:.0f}%[/{rel_color}])",
                border_style=rel_color
            ))
            console.print()

    except Exception as e:
        console.print(f"[red]Error searching memories: {e}[/red]")
        logger.error("memory_search_failed", error=str(e))
        raise typer.Exit(code=1)


@app.command()
def memory_list(
    session_id: Optional[str] = typer.Option(None, "--session", "-s", help="Filter by session ID")
):
    """List all saved memories.

    Example:
        llm-session memory-list
        llm-session memory-list --session abc123
    """
    try:
        memory_mgr = MemoryManager()

        if not memory_mgr.is_available():
            console.print("[red]Memory system not available.[/red]")
            raise typer.Exit(code=1)

        if session_id:
            memories = memory_mgr.get_memories_by_session(session_id)
            title = f"Memories from session {session_id[:20]}..."
        else:
            # Get all memories (limited implementation)
            stats = memory_mgr.get_stats()
            console.print(f"[cyan]Total memories: {stats['total_memories']}[/cyan]")
            console.print(f"[cyan]Sessions with memories: {stats['sessions_with_memories']}[/cyan]\n")

            console.print("[dim]Tip: Use --session to filter by specific session[/dim]")
            console.print("[dim]Tip: Use 'memory-search' to find relevant memories[/dim]")
            return

        if not memories:
            console.print("[yellow]No memories found.[/yellow]")
            return

        console.print(f"\n[bold]{title}[/bold]")
        console.print(f"[dim]Found {len(memories)} memories[/dim]\n")

        for i, memory in enumerate(memories, 1):
            timestamp = memory['metadata'].get('timestamp', 'unknown')
            tags = memory['tags']

            console.print(f"{i}. [bold]{memory['content'][:80]}...[/bold]")
            console.print(f"   [dim]ID: {memory['id']}[/dim]")
            console.print(f"   [dim]When: {timestamp}[/dim]")
            if tags:
                console.print(f"   [magenta]Tags: {', '.join(f'#{t}' for t in tags)}[/magenta]")
            console.print()

    except Exception as e:
        console.print(f"[red]Error listing memories: {e}[/red]")
        logger.error("memory_list_failed", error=str(e))
        raise typer.Exit(code=1)


@app.command()
def memory_stats():
    """Show memory system statistics.

    Example:
        llm-session memory-stats
    """
    try:
        memory_mgr = MemoryManager()

        if not memory_mgr.is_available():
            console.print("[red]Memory system not available. ChromaDB may not be installed.[/red]")
            raise typer.Exit(code=1)

        stats = memory_mgr.get_stats()

        console.print("\n[bold cyan]Memory System Statistics[/bold cyan]\n")
        console.print(f"  Total Memories:        {stats['total_memories']:,}")
        console.print(f"  Sessions with Memories: {stats['sessions_with_memories']}")
        console.print(f"  Storage Location:       {stats['storage_path']}")
        console.print(f"  Status:                 [green]Active[/green]")
        console.print()

    except Exception as e:
        console.print(f"[red]Error getting stats: {e}[/red]")
        logger.error("memory_stats_failed", error=str(e))
        raise typer.Exit(code=1)


@app.command()
def recommend():
    """Get smart recommendations for session management.

    Analyzes all active sessions and provides recommendations for:
    - Restarting unhealthy sessions
    - Closing idle sessions
    - Merging similar sessions
    - Token usage warnings
    """
    try:
        # Initialize components
        db, discovery, health_monitor, token_estimator = get_components()
        recommendation_engine = RecommendationEngine()

        # Discover and analyze sessions
        console.print("[dim]Analyzing sessions...[/dim]")
        sessions = discovery.discover_sessions()

        if not sessions:
            console.print("[yellow]No active sessions found.[/yellow]")
            return

        # Update metrics
        token_estimator.update_token_counts(sessions)
        health_monitor.update_health_scores(sessions)

        # Generate recommendations
        recommendations = recommendation_engine.analyze_sessions(sessions)

        # Display recommendations
        console.print()
        if not recommendations:
            console.print("[green]✅ No recommendations - all sessions healthy![/green]\n")
            return

        console.print(f"[bold cyan]Smart Recommendations ({len(recommendations)})[/bold cyan]\n")

        priority_emojis = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        priority_colors = {"high": "red", "medium": "yellow", "low": "green"}

        for i, rec in enumerate(recommendations, 1):
            emoji = priority_emojis.get(rec["priority"], "ℹ️")
            color = priority_colors.get(rec["priority"], "white")

            panel_text = Text()
            panel_text.append(f"{rec['message']}\n\n", style=f"bold {color}")
            panel_text.append("Reason: ", style="bold")
            panel_text.append(f"{rec['reason']}\n", style="dim")
            panel_text.append("Action: ", style="bold")
            panel_text.append(f"{rec['action']}\n", style="cyan")

            if len(rec['session_ids']) == 1:
                panel_text.append("\nSession: ", style="bold dim")
                panel_text.append(f"{rec['session_ids'][0][:30]}...", style="dim")
            else:
                panel_text.append(f"\nAffects {len(rec['session_ids'])} sessions", style="dim")

            console.print(Panel(
                panel_text,
                title=f"{emoji} {rec['type'].upper()} (Priority: {rec['priority']})",
                border_style=color
            ))
            console.print()

    except Exception as e:
        console.print(f"[red]Error generating recommendations: {e}[/red]")
        logger.error("recommendations_failed", error=str(e))
        raise typer.Exit(code=1)


@app.command()
def info():
    """Show information about the tool."""
    console.print("\n[bold cyan]LLM Session Manager[/bold cyan]")
    console.print("Version: 0.2.0")
    console.print()
    console.print("A CLI tool for tracking and managing multiple AI coding assistant sessions.")
    console.print()
    console.print("[bold]Features:[/bold]")
    console.print("  • Real-time session monitoring")
    console.print("  • Token usage tracking (with tiktoken)")
    console.print("  • Health scoring")
    console.print("  • Context export/import (JSON, YAML, Markdown)")
    console.print("  • Session tagging and organization")
    console.print("  • Cross-session memory (semantic search with ChromaDB)")
    console.print("  • Configurable via YAML")
    console.print("  • GitHub Copilot support")
    console.print()
    console.print("[bold]Commands:[/bold]")
    console.print("  monitor       - Start the real-time dashboard")
    console.print("  list          - List all active sessions")
    console.print("  tag / untag   - Add/remove tags from a session")
    console.print("  auto-tag      - AI-powered automatic tagging")
    console.print("  describe      - Add description to a session")
    console.print("  set-project   - Set project name for a session")
    console.print("  batch-tag     - Tag multiple sessions at once")
    console.print("  batch-export  - Export multiple sessions at once")
    console.print("  export        - Export session context (JSON/YAML/Markdown)")
    console.print("  import-context- Import session context")
    console.print("  health        - Show health details")
    console.print("  recommend     - Get smart recommendations")
    console.print("  memory-add    - Save knowledge to cross-session memory")
    console.print("  memory-search - Search memories semantically")
    console.print("  memory-list   - List all memories")
    console.print("  memory-stats  - Show memory system stats")
    console.print("  init-config   - Create default configuration file")
    console.print("  show-config   - Show current configuration")
    console.print()
    console.print("Run [cyan]llm-session --help[/cyan] for more information.\n")


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
