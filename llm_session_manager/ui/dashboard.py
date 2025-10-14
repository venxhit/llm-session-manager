"""Rich TUI dashboard for LLM session monitoring."""

import sys
import time
import threading
from datetime import datetime, timedelta
from typing import List, Optional, Callable
import structlog

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn
from rich.align import Align

from ..models import Session
from ..core.health_monitor import HealthMonitor
from ..core.session_discovery import SessionDiscovery
from ..utils.token_estimator import TokenEstimator

logger = structlog.get_logger()


def get_key_non_blocking():
    """Get a single key press in a non-blocking way.

    Returns:
        Key character or None if no key pressed.
    """
    try:
        import sys
        import select
        import tty
        import termios

        # Check if stdin is a terminal
        if not sys.stdin.isatty():
            return None

        # Save terminal settings
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setcbreak(sys.stdin.fileno())

            # Check if data is available (non-blocking)
            if select.select([sys.stdin], [], [], 0)[0]:
                key = sys.stdin.read(1)
                return key.lower()
            return None
        finally:
            # Restore terminal settings
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    except Exception:
        # Windows or other systems without termios
        return None


class Dashboard:
    """Rich TUI dashboard for monitoring LLM sessions.

    Provides a live-updating terminal interface showing session health,
    token usage, and activity metrics.
    """

    def __init__(
        self,
        discovery: SessionDiscovery,
        health_monitor: HealthMonitor,
        token_estimator: TokenEstimator,
        refresh_interval: int = 5
    ):
        """Initialize dashboard.

        Args:
            discovery: SessionDiscovery instance for finding sessions.
            health_monitor: HealthMonitor instance for health scoring.
            token_estimator: TokenEstimator instance for token counting.
            refresh_interval: Seconds between refreshes (default: 5).
        """
        self.discovery = discovery
        self.health_monitor = health_monitor
        self.token_estimator = token_estimator
        self.refresh_interval = refresh_interval
        self.console = Console()
        self.sessions: List[Session] = []
        self.last_refresh: datetime = datetime.now()
        self.running = False
        self._stop_event = threading.Event()

    def create_header(self) -> Panel:
        """Create header panel with title and metadata.

        Returns:
            Rich Panel with header information.
        """
        session_count = len(self.sessions)
        refresh_time = self.last_refresh.strftime("%Y-%m-%d %H:%M:%S")

        # Count sessions by status
        active_count = sum(1 for s in self.sessions if s.status.value == "active")
        idle_count = sum(1 for s in self.sessions if s.status.value == "idle")

        header_text = Text()
        header_text.append("🖥️  LLM Session Manager", style="bold cyan")
        header_text.append(" - Dashboard\n\n", style="bold white")
        header_text.append(f"Total Sessions: {session_count}", style="white")
        header_text.append(f"  •  Active: {active_count}", style="green")
        header_text.append(f"  •  Idle: {idle_count}", style="yellow")
        header_text.append(f"\nLast Refresh: {refresh_time}", style="dim white")

        return Panel(
            Align.center(header_text),
            border_style="cyan",
            padding=(1, 2)
        )

    def create_session_table(self, sessions: List[Session]) -> Table:
        """Create Rich table with session information.

        Args:
            sessions: List of Session objects to display.

        Returns:
            Rich Table with formatted session data.
        """
        table = Table(
            title="Active Sessions",
            title_style="bold magenta",
            show_header=True,
            header_style="bold cyan",
            border_style="blue",
            show_lines=True
        )

        # Define columns
        table.add_column("ID", style="dim", width=25)
        table.add_column("Type", justify="center", width=12)
        table.add_column("PID", justify="right", width=8)
        table.add_column("Status", justify="center", width=10)
        table.add_column("Duration", justify="right", width=12)
        table.add_column("Tokens", justify="right", width=30)
        table.add_column("Health", justify="center", width=20)

        # Sort sessions by health score (worst first)
        sorted_sessions = sorted(sessions, key=lambda s: s.health_score)

        for session in sorted_sessions:
            # Format duration as HH:MM:SS
            duration = datetime.now() - session.start_time
            duration_str = self._format_duration(duration)

            # Format token usage with progress bar
            token_percent = (session.token_count / session.token_limit * 100) if session.token_limit > 0 else 0
            token_text = self._create_token_bar(session.token_count, session.token_limit, token_percent)

            # Format health with color and emoji
            health_score = session.health_score / 100  # Convert back to 0-1 scale
            health_text = self._create_health_text(health_score)

            # Format type
            type_text = Text(session.type.value, style=self._get_type_style(session.type.value))

            # Format status
            status_text = Text(session.status.value, style=self._get_status_style(session.status.value))

            # Format ID (truncate if too long)
            session_id = session.id[:23] + ".." if len(session.id) > 25 else session.id

            # Add row
            table.add_row(
                session_id,
                type_text,
                str(session.pid),
                status_text,
                duration_str,
                token_text,
                health_text
            )

        if not sessions:
            # Show empty state
            table.add_row(
                Text("No active sessions found", style="dim italic"),
                "", "", "", "", "", ""
            )

        return table

    def create_footer(self) -> Panel:
        """Create footer panel with keyboard shortcuts.

        Returns:
            Rich Panel with footer information.
        """
        footer_text = Text()
        footer_text.append("Keyboard Shortcuts: ", style="bold white")
        footer_text.append("[Q]", style="bold red")
        footer_text.append("uit  ", style="white")
        footer_text.append("[R]", style="bold green")
        footer_text.append("efresh  ", style="white")
        footer_text.append("[D]", style="bold blue")
        footer_text.append("etails  ", style="white")
        footer_text.append("[H]", style="bold yellow")
        footer_text.append("elp", style="white")

        return Panel(
            Align.center(footer_text),
            border_style="dim white",
            padding=(0, 2)
        )

    def _format_duration(self, duration: timedelta) -> str:
        """Format timedelta as HH:MM:SS.

        Args:
            duration: Time duration.

        Returns:
            Formatted string.
        """
        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _create_token_bar(self, current: int, limit: int, percent: float) -> Text:
        """Create token usage bar with text.

        Args:
            current: Current token count.
            limit: Token limit.
            percent: Usage percentage.

        Returns:
            Rich Text with progress bar.
        """
        # Determine color based on percentage
        if percent < 70:
            color = "green"
        elif percent < 90:
            color = "yellow"
        else:
            color = "red"

        # Create visual bar
        bar_length = 15
        filled = int((percent / 100) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)

        text = Text()
        text.append(f"{current:,}", style=color)
        text.append(f"/{limit:,} ", style="dim white")
        text.append(f"[{bar}]", style=color)
        text.append(f" {percent:.0f}%", style=color)

        return text

    def _create_health_text(self, health_score: float) -> Text:
        """Create health display with emoji and color.

        Args:
            health_score: Score between 0.0 and 1.0.

        Returns:
            Rich Text with health indicator.
        """
        emoji = self.health_monitor.get_health_emoji(health_score)
        status = self.health_monitor.get_health_status(health_score)
        color = self.health_monitor.get_health_color(health_score)

        text = Text()
        text.append(f"{emoji} ", style=color)
        text.append(f"{health_score * 100:.0f}% ", style=f"bold {color}")
        text.append(f"({status})", style=color)

        return text

    def _get_type_style(self, session_type: str) -> str:
        """Get color style for session type.

        Args:
            session_type: Session type string.

        Returns:
            Style string.
        """
        styles = {
            "claude_code": "cyan",
            "cursor_cli": "magenta",
            "unknown": "dim white"
        }
        return styles.get(session_type, "white")

    def _get_status_style(self, status: str) -> str:
        """Get color style for session status.

        Args:
            status: Status string.

        Returns:
            Style string.
        """
        styles = {
            "active": "green",
            "idle": "yellow",
            "waiting": "blue",
            "error": "red"
        }
        return styles.get(status, "white")

    def refresh_data(self) -> None:
        """Refresh session data from discovery and update metrics."""
        logger.debug("refreshing_dashboard_data")

        # Discover active sessions
        self.sessions = self.discovery.discover_sessions()

        # Update token counts
        self.token_estimator.update_token_counts(self.sessions)

        # Update health scores
        self.health_monitor.update_health_scores(self.sessions)

        # Update refresh timestamp
        self.last_refresh = datetime.now()

        logger.info(
            "dashboard_data_refreshed",
            session_count=len(self.sessions)
        )

    def create_layout(self) -> Layout:
        """Create dashboard layout with header, table, and footer.

        Returns:
            Rich Layout with all components.
        """
        layout = Layout()

        # Split into header, body, footer
        layout.split_column(
            Layout(name="header", size=7),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )

        # Populate sections
        layout["header"].update(self.create_header())
        layout["body"].update(self.create_session_table(self.sessions))
        layout["footer"].update(self.create_footer())

        return layout

    def run_dashboard(self, callback: Optional[Callable] = None) -> None:
        """Run the dashboard with live updates and keyboard input.

        Keyboard shortcuts:
        - 'q' or Ctrl+C: Quit dashboard
        - 'r': Force refresh
        - 'h': Show help

        Args:
            callback: Optional callback function for handling user input.
        """
        self.running = True
        self._stop_event.clear()

        logger.info("starting_dashboard", refresh_interval=self.refresh_interval)

        # Show initial message
        self.console.print("\n[cyan]Starting LLM Session Manager Dashboard...[/cyan]")
        self.console.print("[dim]Press 'q' to quit, 'r' to refresh, 'h' for help[/dim]\n")
        time.sleep(1)

        try:
            # Initial data refresh
            self.refresh_data()

            with Live(
                self.create_layout(),
                console=self.console,
                refresh_per_second=2,
                screen=False
            ) as live:
                next_refresh = time.time() + self.refresh_interval

                while self.running and not self._stop_event.is_set():
                    # Check for keyboard input (non-blocking)
                    key = get_key_non_blocking()
                    if key:
                        logger.debug("key_pressed", key=key)

                        if key == 'q':
                            # Quit
                            logger.info("quit_requested")
                            self.console.print("\n[yellow]Exiting dashboard...[/yellow]\n")
                            break
                        elif key == 'r':
                            # Force refresh
                            logger.info("manual_refresh_requested")
                            self.console.print("\n[green]Refreshing data...[/green]")
                            self.refresh_data()
                            next_refresh = time.time() + self.refresh_interval
                            time.sleep(0.5)  # Brief pause to show message
                        elif key == 'h':
                            # Show help
                            logger.info("help_requested")
                            live.stop()
                            self.display_help()
                            self.console.print("\n[dim]Press Enter to continue...[/dim]")
                            input()
                            live.start()
                            live.update(self.create_layout())

                    # Update display
                    live.update(self.create_layout())

                    # Check if it's time for automatic refresh
                    current_time = time.time()
                    if current_time >= next_refresh:
                        self.refresh_data()
                        next_refresh = current_time + self.refresh_interval

                    # Small sleep to prevent CPU spinning
                    time.sleep(0.1)

        except KeyboardInterrupt:
            logger.info("dashboard_interrupted_by_user")
            self.console.print("\n[yellow]Dashboard interrupted by user[/yellow]\n")
        except Exception as e:
            logger.error("dashboard_error", error=str(e))
            self.console.print(f"\n[red]Error: {e}[/red]\n")
        finally:
            self.running = False
            logger.info("dashboard_stopped")
            self.console.print("[green]Dashboard stopped successfully[/green]\n")

    def stop_dashboard(self) -> None:
        """Stop the dashboard gracefully."""
        logger.info("stopping_dashboard")
        self.running = False
        self._stop_event.set()

    def run_once(self) -> None:
        """Run dashboard for a single refresh (useful for testing).

        Displays the dashboard once without live updates.
        """
        self.refresh_data()
        self.console.print(self.create_layout())

    def get_session_details(self, session_id: str) -> Optional[dict]:
        """Get detailed information for a specific session.

        Args:
            session_id: Session ID to query.

        Returns:
            Session details dictionary or None if not found.
        """
        for session in self.sessions:
            if session.id.startswith(session_id):
                health_score = session.health_score / 100
                summary = self.health_monitor.get_health_summary(session)
                return {
                    "session": session,
                    "health_summary": summary
                }
        return None

    def display_help(self) -> None:
        """Display help panel with usage instructions."""
        help_text = Text()
        help_text.append("LLM Session Manager - Help\n\n", style="bold cyan")
        help_text.append("Dashboard Commands:\n", style="bold white")
        help_text.append("  Q / Ctrl+C  - ", style="white")
        help_text.append("Quit dashboard\n", style="dim white")
        help_text.append("  R           - ", style="white")
        help_text.append("Force refresh\n", style="dim white")
        help_text.append("  D           - ", style="white")
        help_text.append("Show session details\n", style="dim white")
        help_text.append("  H           - ", style="white")
        help_text.append("Show this help\n\n", style="dim white")
        help_text.append("Health Indicators:\n", style="bold white")
        help_text.append("  ✅ Green   - ", style="green")
        help_text.append("Healthy (>= 70%)\n", style="dim white")
        help_text.append("  ⚠️  Yellow  - ", style="yellow")
        help_text.append("Warning (40-70%)\n", style="dim white")
        help_text.append("  🔴 Red     - ", style="red")
        help_text.append("Critical (< 40%)\n", style="dim white")

        self.console.print(Panel(help_text, border_style="cyan", padding=(1, 2)))
