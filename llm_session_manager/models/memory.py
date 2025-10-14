"""Memory data model for cross-session context sharing."""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4


@dataclass
class Memory:
    """Represents a piece of shared context/knowledge between sessions.

    Stores conversation snippets, code examples, or other contextual information
    that can be retrieved and shared across different LLM sessions.
    """

    # Identity
    id: str = field(default_factory=lambda: str(uuid4()))

    # Content
    content: str = ""
    embedding: Optional[List[float]] = None

    # Metadata
    source_session: str = ""  # Session ID where this memory originated
    timestamp: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)

    # Relevance
    relevance_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert memory to JSON-serializable dictionary.

        Returns:
            Dictionary representation with datetime objects converted to ISO format strings.
        """
        data = asdict(self)
        # Convert datetime to ISO format string
        data["timestamp"] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Memory":
        """Create memory from dictionary.

        Args:
            data: Dictionary containing memory data.

        Returns:
            Memory instance.
        """
        # Create a copy to avoid modifying the original
        data = data.copy()

        # Convert ISO format string back to datetime object
        if isinstance(data.get("timestamp"), str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])

        return cls(**data)

    def add_tag(self, tag: str) -> None:
        """Add a tag to the memory if not already present.

        Args:
            tag: Tag string to add.
        """
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the memory if present.

        Args:
            tag: Tag string to remove.
        """
        if tag in self.tags:
            self.tags.remove(tag)

    def has_embedding(self) -> bool:
        """Check if memory has an embedding vector.

        Returns:
            True if embedding exists and is non-empty.
        """
        return self.embedding is not None and len(self.embedding) > 0

    def update_relevance(self, score: float) -> None:
        """Update the relevance score.

        Args:
            score: New relevance score (typically 0-1 range).
        """
        self.relevance_score = max(0.0, min(1.0, score))  # Clamp to 0-1 range
