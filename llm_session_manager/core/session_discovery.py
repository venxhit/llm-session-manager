"""Session discovery for finding running LLM coding assistant processes."""

import psutil
from datetime import datetime
from typing import List, Optional
import structlog

from ..models import Session, SessionType, SessionStatus
from .detectors import HybridDetector

logger = structlog.get_logger()


class SessionDiscovery:
    """Discovers and tracks running LLM coding assistant processes.

    Uses hybrid detection system combining registry, heuristics, and optional LLM.
    Scans the system for Claude Code, Cursor CLI, and other AI assistant
    processes, creating Session objects for each discovered process.
    """

    def __init__(self, enable_llm: bool = False):
        """Initialize session discovery.

        Args:
            enable_llm: Whether to enable LLM-based detection fallback (opt-in).
        """
        self.detector = HybridDetector(enable_llm=enable_llm)

    def discover_sessions(self) -> List[Session]:
        """Scan for running LLM assistant processes.

        Returns:
            List of Session objects for discovered processes.
        """
        discovered_sessions = []
        logger.info("starting_process_discovery")

        try:
            # Iterate through all running processes
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time', 'cwd']):
                try:
                    # Use hybrid detector to identify session type
                    session_type = self.detector.identify_session_type(proc)

                    if session_type is not None and session_type != SessionType.UNKNOWN:
                        session = self._create_session_from_process(proc, session_type)
                        discovered_sessions.append(session)
                        logger.info(
                            "session_discovered",
                            session_type=session_type.value,
                            pid=proc.info['pid'],
                            name=proc.info['name']
                        )

                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                    # Process disappeared or we don't have permission
                    logger.debug(
                        "process_access_error",
                        error=type(e).__name__,
                        pid=getattr(proc, 'pid', 'unknown')
                    )
                    continue
                except Exception as e:
                    # Unexpected error, log but continue scanning
                    logger.warning(
                        "unexpected_error_during_scan",
                        error=str(e),
                        pid=getattr(proc, 'pid', 'unknown')
                    )
                    continue

        except Exception as e:
            logger.error("process_discovery_failed", error=str(e))
            return []

        logger.info(
            "process_discovery_complete",
            sessions_found=len(discovered_sessions)
        )
        return discovered_sessions

    def get_working_directory(self, process: psutil.Process) -> str:
        """Extract working directory from process.

        Args:
            process: psutil.Process object.

        Returns:
            Working directory path, or empty string if unavailable.
        """
        try:
            # Try to get current working directory
            cwd = process.info.get('cwd')
            if cwd:
                return cwd

            # Fallback: try to get it directly (may require permissions)
            try:
                return process.cwd()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass

            # Last resort: try to extract from command line args
            cmdline = process.info.get('cmdline', [])
            for i, arg in enumerate(cmdline):
                if arg in ['--cwd', '-C', '--working-directory'] and i + 1 < len(cmdline):
                    return cmdline[i + 1]

            return ""

        except Exception as e:
            logger.debug("failed_to_get_working_directory", error=str(e))
            return ""

    def _create_session_from_process(
        self,
        process: psutil.Process,
        session_type: SessionType
    ) -> Session:
        """Create a Session object from process information.

        Args:
            process: psutil.Process object.
            session_type: Identified session type.

        Returns:
            Session object populated with process data.
        """
        proc_info = process.info
        pid = proc_info['pid']

        # Generate session ID using pid and timestamp
        session_id = f"{session_type.value}_{pid}_{int(datetime.now().timestamp())}"

        # Get process creation time
        try:
            create_time = datetime.fromtimestamp(proc_info.get('create_time', 0))
        except (OSError, ValueError):
            create_time = datetime.now()

        # Get working directory
        working_dir = self.get_working_directory(process)

        # Create session object
        session = Session(
            id=session_id,
            pid=pid,
            type=session_type,
            status=SessionStatus.ACTIVE,
            start_time=create_time,
            last_activity=datetime.now(),
            working_directory=working_dir,
            token_count=0,  # Will be updated by monitoring
            token_limit=200000,  # Default limit
            health_score=100.0,  # Start with perfect health
            message_count=0,
            file_count=0,
            error_count=0,
        )

        return session

    def is_process_running(self, pid: int) -> bool:
        """Check if a process with given PID is still running.

        Args:
            pid: Process ID to check.

        Returns:
            True if process exists and is running.
        """
        try:
            process = psutil.Process(pid)
            return process.is_running()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

    def get_process_info(self, pid: int) -> Optional[dict]:
        """Get detailed information about a specific process.

        Args:
            pid: Process ID to query.

        Returns:
            Dictionary with process info, or None if process not found.
        """
        try:
            process = psutil.Process(pid)
            return {
                'pid': pid,
                'name': process.name(),
                'status': process.status(),
                'cpu_percent': process.cpu_percent(interval=0.1),
                'memory_mb': process.memory_info().rss / (1024 * 1024),
                'create_time': datetime.fromtimestamp(process.create_time()),
                'num_threads': process.num_threads(),
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.debug("failed_to_get_process_info", pid=pid, error=str(e))
            return None
