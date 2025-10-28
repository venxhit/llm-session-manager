"""SQLite database layer for session and memory persistence."""

import sqlite3
import json
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import structlog

from ..models import Session, SessionType, SessionStatus, Memory

logger = structlog.get_logger()


class Database:
    """SQLite database manager for LLM session tracking.

    Handles persistence of sessions, session history, and shared memories.
    Uses context managers for proper connection handling.
    """

    def __init__(self, db_path: str = "data/sessions.db"):
        """Initialize database connection.

        Args:
            db_path: Path to SQLite database file.
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info("database_initialized", path=str(self.db_path))

    @contextmanager
    def get_connection(self):
        """Context manager for database connections.

        Yields:
            sqlite3.Connection: Database connection with row factory set.

        Example:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(...)
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error("database_error", error=str(e))
            raise
        finally:
            conn.close()

    def init_db(self) -> None:
        """Initialize database schema.

        Creates tables for sessions, session_history, and memories if they don't exist.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    pid INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    last_activity TEXT NOT NULL,
                    working_directory TEXT NOT NULL,
                    token_count INTEGER DEFAULT 0,
                    token_limit INTEGER DEFAULT 200000,
                    health_score REAL DEFAULT 100.0,
                    message_count INTEGER DEFAULT 0,
                    file_count INTEGER DEFAULT 0,
                    error_count INTEGER DEFAULT 0,
                    tags TEXT DEFAULT '[]',
                    project_name TEXT,
                    description TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Session history table for tracking changes over time
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    token_count INTEGER NOT NULL,
                    health_score REAL NOT NULL,
                    status TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
                )
            """)

            # Memories table for cross-session context sharing
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    embedding TEXT,
                    source_session TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    tags TEXT NOT NULL,
                    relevance_score REAL DEFAULT 0.0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_session) REFERENCES sessions (id) ON DELETE CASCADE
                )
            """)

            # Tag feedback table for learning from user choices
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tag_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    suggested_tag TEXT NOT NULL,
                    accepted BOOLEAN NOT NULL,
                    source TEXT DEFAULT 'heuristic',
                    context_tags TEXT,
                    file_extensions TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
                )
            """)

            # Create indexes for common queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_status
                ON sessions(status)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_type
                ON sessions(type)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_history_session
                ON session_history(session_id, timestamp)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_memories_session
                ON memories(source_session)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tag_feedback
                ON tag_feedback(suggested_tag, accepted)
            """)

            logger.info("database_schema_initialized")

    def add_session(self, session: Session) -> None:
        """Insert a new session into the database.

        Args:
            session: Session object to insert.

        Raises:
            sqlite3.IntegrityError: If session ID already exists.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sessions (
                    id, pid, type, status, start_time, last_activity,
                    working_directory, token_count, token_limit, health_score,
                    message_count, file_count, error_count, tags, project_name, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session.id,
                session.pid,
                session.type.value,
                session.status.value,
                session.start_time.isoformat(),
                session.last_activity.isoformat(),
                session.working_directory,
                session.token_count,
                session.token_limit,
                session.health_score,
                session.message_count,
                session.file_count,
                session.error_count,
                json.dumps(session.tags),
                session.project_name,
                session.description,
            ))
            logger.info("session_added", session_id=session.id, pid=session.pid)

    def update_session(self, session: Session) -> None:
        """Update an existing session in the database.

        Args:
            session: Session object with updated values.

        Raises:
            sqlite3.Error: If update fails.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE sessions SET
                    pid = ?,
                    type = ?,
                    status = ?,
                    start_time = ?,
                    last_activity = ?,
                    working_directory = ?,
                    token_count = ?,
                    token_limit = ?,
                    health_score = ?,
                    message_count = ?,
                    file_count = ?,
                    error_count = ?,
                    tags = ?,
                    project_name = ?,
                    description = ?
                WHERE id = ?
            """, (
                session.pid,
                session.type.value,
                session.status.value,
                session.start_time.isoformat(),
                session.last_activity.isoformat(),
                session.working_directory,
                session.token_count,
                session.token_limit,
                session.health_score,
                session.message_count,
                session.file_count,
                session.error_count,
                json.dumps(session.tags),
                session.project_name,
                session.description,
                session.id,
            ))
            logger.info("session_updated", session_id=session.id)

    def get_session(self, session_id: str) -> Optional[Session]:
        """Retrieve a session by ID.

        Args:
            session_id: Unique session identifier.

        Returns:
            Session object if found, None otherwise.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()

            if row:
                return self._row_to_session(row)
            return None

    def get_all_sessions(self) -> List[Session]:
        """Retrieve all sessions from the database.

        Returns:
            List of all Session objects, ordered by last activity (most recent first).
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM sessions
                ORDER BY last_activity DESC
            """)
            rows = cursor.fetchall()
            return [self._row_to_session(row) for row in rows]

    def get_active_sessions(self) -> List[Session]:
        """Retrieve only active sessions.

        Returns:
            List of Session objects with ACTIVE status.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM sessions
                WHERE status = ?
                ORDER BY last_activity DESC
            """, (SessionStatus.ACTIVE.value,))
            rows = cursor.fetchall()
            return [self._row_to_session(row) for row in rows]

    def delete_session(self, session_id: str) -> None:
        """Remove a session from the database.

        Args:
            session_id: Unique session identifier.

        Note:
            This will also cascade delete related history entries and memories.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            logger.info("session_deleted", session_id=session_id)

    def add_history_entry(
        self,
        session_id: str,
        token_count: int,
        health_score: float,
        status: str
    ) -> None:
        """Add a history snapshot for a session.

        Args:
            session_id: Session to track.
            token_count: Current token count.
            health_score: Current health score.
            status: Current session status.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO session_history (
                    session_id, token_count, health_score, status, timestamp
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                session_id,
                token_count,
                health_score,
                status,
                datetime.now().isoformat(),
            ))
            logger.debug("history_entry_added", session_id=session_id)

    def get_session_history(
        self,
        session_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve history entries for a session.

        Args:
            session_id: Session to query.
            limit: Maximum number of entries to return.

        Returns:
            List of history entry dictionaries, ordered by timestamp (newest first).
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM session_history
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (session_id, limit))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def add_memory(self, memory: Memory) -> None:
        """Store a memory for cross-session sharing.

        Args:
            memory: Memory object to store.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO memories (
                    id, content, embedding, source_session, timestamp, tags, relevance_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                memory.id,
                memory.content,
                json.dumps(memory.embedding) if memory.embedding else None,
                memory.source_session,
                memory.timestamp.isoformat(),
                json.dumps(memory.tags),
                memory.relevance_score,
            ))
            logger.info("memory_added", memory_id=memory.id)

    def get_memories_by_session(self, session_id: str) -> List[Memory]:
        """Retrieve all memories from a specific session.

        Args:
            session_id: Source session ID.

        Returns:
            List of Memory objects.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM memories
                WHERE source_session = ?
                ORDER BY timestamp DESC
            """, (session_id,))
            rows = cursor.fetchall()
            return [self._row_to_memory(row) for row in rows]

    def get_all_memories(self, limit: int = 1000) -> List[Memory]:
        """Retrieve all memories.

        Args:
            limit: Maximum number of memories to return.

        Returns:
            List of Memory objects, ordered by timestamp (newest first).
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM memories
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [self._row_to_memory(row) for row in rows]

    def _row_to_session(self, row: sqlite3.Row) -> Session:
        """Convert database row to Session object.

        Args:
            row: SQLite row from sessions table.

        Returns:
            Session object.
        """
        # Deserialize tags from JSON
        tags = json.loads(row["tags"]) if row["tags"] else []

        return Session(
            id=row["id"],
            pid=row["pid"],
            type=SessionType(row["type"]),
            status=SessionStatus(row["status"]),
            start_time=datetime.fromisoformat(row["start_time"]),
            last_activity=datetime.fromisoformat(row["last_activity"]),
            working_directory=row["working_directory"],
            token_count=row["token_count"],
            token_limit=row["token_limit"],
            health_score=row["health_score"],
            message_count=row["message_count"],
            file_count=row["file_count"],
            error_count=row["error_count"],
            tags=tags,
            project_name=row["project_name"] if "project_name" in row.keys() else None,
            description=row["description"] if "description" in row.keys() else None,
        )

    def _row_to_memory(self, row: sqlite3.Row) -> Memory:
        """Convert database row to Memory object.

        Args:
            row: SQLite row from memories table.

        Returns:
            Memory object.
        """
        embedding = json.loads(row["embedding"]) if row["embedding"] else None
        tags = json.loads(row["tags"])

        return Memory(
            id=row["id"],
            content=row["content"],
            embedding=embedding,
            source_session=row["source_session"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            tags=tags,
            relevance_score=row["relevance_score"],
        )

    def add_tag_feedback(
        self,
        session_id: str,
        suggested_tag: str,
        accepted: bool,
        source: str = "heuristic",
        context_tags: Optional[List[str]] = None,
        file_extensions: Optional[List[str]] = None
    ) -> None:
        """Record user feedback on tag suggestions for learning.

        Args:
            session_id: Session the tag was suggested for.
            suggested_tag: The tag that was suggested.
            accepted: Whether user accepted the tag.
            source: Source of suggestion (heuristic, ai, hybrid).
            context_tags: Other tags present at time of suggestion.
            file_extensions: File extensions found in session.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tag_feedback (
                    session_id, suggested_tag, accepted, source, context_tags, file_extensions
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                suggested_tag,
                accepted,
                source,
                json.dumps(context_tags) if context_tags else None,
                json.dumps(file_extensions) if file_extensions else None,
            ))
            logger.debug("tag_feedback_recorded",
                        tag=suggested_tag,
                        accepted=accepted)

    def get_tag_acceptance_rate(self, tag: str) -> float:
        """Get historical acceptance rate for a tag.

        Args:
            tag: Tag to query.

        Returns:
            Acceptance rate (0.0 to 1.0), or 0.5 if no data.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    SUM(CASE WHEN accepted THEN 1 ELSE 0 END) as accepted_count,
                    COUNT(*) as total_count
                FROM tag_feedback
                WHERE suggested_tag = ?
            """, (tag,))
            row = cursor.fetchone()

            if row and row["total_count"] > 0:
                return row["accepted_count"] / row["total_count"]
            return 0.5  # Neutral default

    def get_tag_suggestions_insights(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get insights about tag suggestions for improving algorithm.

        Args:
            limit: Number of top tags to return.

        Returns:
            List of dicts with tag statistics.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    suggested_tag,
                    SUM(CASE WHEN accepted THEN 1 ELSE 0 END) as accepted,
                    SUM(CASE WHEN NOT accepted THEN 1 ELSE 0 END) as rejected,
                    COUNT(*) as total,
                    CAST(SUM(CASE WHEN accepted THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) as acceptance_rate,
                    source
                FROM tag_feedback
                GROUP BY suggested_tag, source
                ORDER BY total DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def search_sessions_by_description(self, query: str) -> List[Session]:
        """Search sessions by description text.

        Args:
            query: Search query string.

        Returns:
            List of matching Session objects.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Use LIKE for simple text search
            search_pattern = f"%{query}%"
            cursor.execute("""
                SELECT * FROM sessions
                WHERE description LIKE ?
                ORDER BY last_activity DESC
            """, (search_pattern,))
            rows = cursor.fetchall()
            return [self._row_to_session(row) for row in rows]
