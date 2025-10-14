"""Token estimation and tracking for LLM sessions."""

import os
from pathlib import Path
from typing import Dict, List, Set, Optional
import structlog

from ..models import Session

logger = structlog.get_logger()


class TokenEstimator:
    """Estimates and tracks token usage for LLM sessions.

    Uses heuristics to estimate token counts based on messages and files
    in the session's working directory.
    """

    # Token estimation constants
    BASE_TOKENS = 1000  # Base context tokens
    TOKENS_PER_MESSAGE = 200  # Average tokens per message
    CHARS_PER_TOKEN = 4  # Rough estimate: 1 token ≈ 4 characters

    # Token limits by plan type (in thousands of tokens)
    TOKEN_LIMITS = {
        "claude_pro": 7000,
        "claude_max5": 35000,
        "claude_max20": 140000,
        "cursor_default": 10000,
    }

    # File extensions to process
    TEXT_FILE_EXTENSIONS = {
        # Code files
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
        '.hpp', '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt',
        # Web files
        '.html', '.css', '.scss', '.sass', '.less', '.vue',
        # Documentation
        '.md', '.txt', '.rst', '.adoc',
        # Config files
        '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
        # Shell scripts
        '.sh', '.bash', '.zsh', '.fish',
    }

    # File extensions to ignore
    BINARY_FILE_EXTENSIONS = {
        '.pyc', '.pyo', '.so', '.dylib', '.dll', '.exe', '.bin',
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg',
        '.mp3', '.mp4', '.avi', '.mov', '.wav',
        '.zip', '.tar', '.gz', '.bz2', '.7z', '.rar',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx',
        '.db', '.sqlite', '.sqlite3',
    }

    # Directories to skip
    SKIP_DIRECTORIES = {
        '__pycache__', 'node_modules', '.git', '.svn', '.hg',
        'venv', 'env', '.venv', '.env',
        'build', 'dist', 'target', 'out',
        '.pytest_cache', '.mypy_cache', '.ruff_cache',
    }

    def __init__(self):
        """Initialize token estimator with empty cache."""
        self._file_token_cache: Dict[str, int] = {}
        self._file_mtime_cache: Dict[str, float] = {}

    def estimate_session_tokens(self, session: Session) -> int:
        """Estimate total token count for a session.

        Uses the formula:
        total_tokens = BASE_TOKENS +
                       (message_count * TOKENS_PER_MESSAGE) +
                       sum(file_tokens)

        Args:
            session: Session object to estimate tokens for.

        Returns:
            Estimated total token count.
        """
        # Base context tokens
        total_tokens = self.BASE_TOKENS

        # Message tokens
        message_tokens = session.message_count * self.TOKENS_PER_MESSAGE
        total_tokens += message_tokens

        # File tokens from working directory
        if session.working_directory and os.path.isdir(session.working_directory):
            file_tokens = self._estimate_directory_tokens(session.working_directory)
            total_tokens += file_tokens
            logger.debug(
                "session_token_estimate",
                session_id=session.id,
                base=self.BASE_TOKENS,
                messages=message_tokens,
                files=file_tokens,
                total=total_tokens
            )
        else:
            logger.debug(
                "session_token_estimate_no_directory",
                session_id=session.id,
                working_directory=session.working_directory
            )

        return total_tokens

    def estimate_file_tokens(self, file_path: str) -> int:
        """Estimate token count for a single file.

        Args:
            file_path: Path to file to analyze.

        Returns:
            Estimated token count (0 if file cannot be read or is binary).
        """
        try:
            path = Path(file_path)

            # Check if file exists
            if not path.exists() or not path.is_file():
                return 0

            # Check file extension
            if path.suffix.lower() in self.BINARY_FILE_EXTENSIONS:
                return 0

            if path.suffix.lower() not in self.TEXT_FILE_EXTENSIONS:
                # Unknown extension, skip
                return 0

            # Check cache
            file_mtime = path.stat().st_mtime
            if file_path in self._file_token_cache:
                cached_mtime = self._file_mtime_cache.get(file_path, 0)
                if cached_mtime == file_mtime:
                    # File hasn't changed, return cached value
                    return self._file_token_cache[file_path]

            # Read file and estimate tokens
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    token_count = len(content) // self.CHARS_PER_TOKEN

                    # Update cache
                    self._file_token_cache[file_path] = token_count
                    self._file_mtime_cache[file_path] = file_mtime

                    return token_count

            except UnicodeDecodeError:
                # File is binary or uses unsupported encoding
                logger.debug("binary_file_skipped", file=file_path)
                return 0

        except (OSError, IOError) as e:
            logger.debug("file_read_error", file=file_path, error=str(e))
            return 0

        except Exception as e:
            logger.warning("unexpected_file_error", file=file_path, error=str(e))
            return 0

    def _estimate_directory_tokens(self, directory: str, max_depth: int = 3) -> int:
        """Estimate total tokens for all text files in a directory.

        Args:
            directory: Directory path to scan.
            max_depth: Maximum recursion depth.

        Returns:
            Total estimated tokens for all files in directory.
        """
        total_tokens = 0
        file_count = 0

        try:
            for root, dirs, files in os.walk(directory):
                # Calculate current depth
                depth = root[len(directory):].count(os.sep)
                if depth >= max_depth:
                    dirs.clear()  # Don't recurse deeper
                    continue

                # Skip certain directories
                dirs[:] = [d for d in dirs if d not in self.SKIP_DIRECTORIES]

                # Process files
                for filename in files:
                    file_path = os.path.join(root, filename)
                    tokens = self.estimate_file_tokens(file_path)
                    if tokens > 0:
                        total_tokens += tokens
                        file_count += 1

        except Exception as e:
            logger.warning("directory_scan_error", directory=directory, error=str(e))

        logger.debug(
            "directory_tokens_estimated",
            directory=directory,
            files_processed=file_count,
            total_tokens=total_tokens
        )

        return total_tokens

    def update_token_counts(self, sessions: List[Session]) -> None:
        """Update token counts for all sessions.

        Args:
            sessions: List of Session objects to update.
        """
        logger.info("updating_token_counts", session_count=len(sessions))

        for session in sessions:
            old_count = session.token_count
            new_count = self.estimate_session_tokens(session)

            session.token_count = new_count

            if new_count != old_count:
                logger.info(
                    "token_count_updated",
                    session_id=session.id,
                    old_count=old_count,
                    new_count=new_count,
                    change=new_count - old_count
                )

    def get_token_limit(self, plan_type: str) -> int:
        """Get token limit for a specific plan type.

        Args:
            plan_type: Plan type identifier (e.g., "claude_pro", "cursor_default").

        Returns:
            Token limit, or default 200000 if plan not found.
        """
        return self.TOKEN_LIMITS.get(plan_type, 200000)

    def calculate_token_percentage(self, session: Session) -> float:
        """Calculate token usage as percentage of limit.

        Args:
            session: Session to calculate percentage for.

        Returns:
            Percentage of token limit used (0-100).
        """
        if session.token_limit == 0:
            return 0.0
        return (session.token_count / session.token_limit) * 100

    def is_token_limit_critical(self, session: Session, threshold: float = 90.0) -> bool:
        """Check if session is approaching token limit.

        Args:
            session: Session to check.
            threshold: Percentage threshold for critical warning (default: 90%).

        Returns:
            True if token usage exceeds threshold.
        """
        return self.calculate_token_percentage(session) >= threshold

    def get_remaining_tokens(self, session: Session) -> int:
        """Calculate remaining tokens before hitting limit.

        Args:
            session: Session to calculate for.

        Returns:
            Number of tokens remaining.
        """
        return max(0, session.token_limit - session.token_count)

    def clear_cache(self) -> None:
        """Clear the file token cache.

        Useful for forcing re-estimation of all files.
        """
        self._file_token_cache.clear()
        self._file_mtime_cache.clear()
        logger.info("token_cache_cleared")

    def get_cache_stats(self) -> Dict[str, int]:
        """Get statistics about the token cache.

        Returns:
            Dictionary with cache statistics.
        """
        return {
            "cached_files": len(self._file_token_cache),
            "total_cached_tokens": sum(self._file_token_cache.values()),
        }
