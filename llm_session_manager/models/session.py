"""Session data model and related enums."""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from uuid import uuid4


class SessionType(str, Enum):
    """Type of LLM coding session."""
    CLAUDE_CODE = "claude_code"
    CURSOR_CLI = "cursor_cli"
    GITHUB_COPILOT = "github_copilot"
    UNKNOWN = "unknown"


class SessionStatus(str, Enum):
    """Current status of a session."""
    ACTIVE = "active"
    IDLE = "idle"
    WAITING = "waiting"
    ERROR = "error"


@dataclass
class Session:
    """Represents an LLM coding session.

    Tracks metadata, health metrics, and token usage for a single
    LLM coding assistant session (Claude Code, Cursor CLI, etc.).
    """

    # Identity
    id: str = field(default_factory=lambda: str(uuid4()))
    pid: int = 0
    type: SessionType = SessionType.UNKNOWN
    status: SessionStatus = SessionStatus.ACTIVE

    # Timestamps
    start_time: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)

    # Context
    working_directory: str = ""

    # Token tracking
    token_count: int = 0
    token_limit: int = 200000

    # Health metrics
    health_score: float = 100.0
    message_count: int = 0
    file_count: int = 0
    error_count: int = 0

    # Organization
    tags: List[str] = field(default_factory=list)
    project_name: Optional[str] = None
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to JSON-serializable dictionary.

        Returns:
            Dictionary representation with datetime objects converted to ISO format strings.
        """
        data = asdict(self)
        # Convert datetime objects to ISO format strings
        data["start_time"] = self.start_time.isoformat()
        data["last_activity"] = self.last_activity.isoformat()
        # Convert enums to their values
        data["type"] = self.type.value
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """Create session from dictionary.

        Args:
            data: Dictionary containing session data.

        Returns:
            Session instance.
        """
        # Create a copy to avoid modifying the original
        data = data.copy()

        # Convert ISO format strings back to datetime objects
        if isinstance(data.get("start_time"), str):
            data["start_time"] = datetime.fromisoformat(data["start_time"])
        if isinstance(data.get("last_activity"), str):
            data["last_activity"] = datetime.fromisoformat(data["last_activity"])

        # Convert string values back to enums
        if isinstance(data.get("type"), str):
            data["type"] = SessionType(data["type"])
        if isinstance(data.get("status"), str):
            data["status"] = SessionStatus(data["status"])

        return cls(**data)

    def update_activity(self) -> None:
        """Update the last activity timestamp to now."""
        self.last_activity = datetime.now()

    def calculate_token_usage_percent(self) -> float:
        """Calculate token usage as a percentage of the limit.

        Returns:
            Token usage percentage (0-100).
        """
        if self.token_limit == 0:
            return 0.0
        return (self.token_count / self.token_limit) * 100

    def is_healthy(self, threshold: float = 70.0) -> bool:
        """Check if session health is above threshold.

        Args:
            threshold: Minimum health score to consider healthy (default: 70.0).

        Returns:
            True if health score is above threshold.
        """
        return self.health_score >= threshold

    def add_tag(self, tag: str) -> None:
        """Add a tag to the session.

        Args:
            tag: Tag to add (will be lowercased and stripped).
        """
        tag = tag.lower().strip()
        if tag and tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the session.

        Args:
            tag: Tag to remove.
        """
        tag = tag.lower().strip()
        if tag in self.tags:
            self.tags.remove(tag)

    def has_tag(self, tag: str) -> bool:
        """Check if session has a specific tag.

        Args:
            tag: Tag to check for.

        Returns:
            True if session has the tag.
        """
        return tag.lower().strip() in self.tags

    def set_project(self, project_name: str) -> None:
        """Set the project name for this session.

        Args:
            project_name: Name of the project.
        """
        self.project_name = project_name.strip() if project_name else None
