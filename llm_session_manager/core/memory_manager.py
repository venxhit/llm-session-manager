"""Cross-session memory management using ChromaDB.

This module enables sessions to share knowledge via semantic search.
When you learn something in Session A, Session B can find and use that knowledge.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import structlog

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

from ..models import Session, Memory

logger = structlog.get_logger()


class MemoryManager:
    """Manages cross-session memory using ChromaDB for semantic search.

    Features:
    - Extract important knowledge from sessions
    - Store memories with embeddings
    - Semantic search across all sessions
    - Auto-inject relevant memories into new sessions

    Example:
        # In Session A, you learn how to implement auth
        memory_mgr.add_memory(
            session_id="session-a",
            content="Implemented JWT authentication using jose library...",
            tags=["auth", "jwt", "backend"]
        )

        # Later in Session B, searching for auth
        memories = memory_mgr.search_memories("how to do authentication", limit=3)
        # Returns relevant memories from Session A
    """

    def __init__(self, storage_path: str = "data/memories"):
        """Initialize memory manager with ChromaDB.

        Args:
            storage_path: Directory to store ChromaDB data.
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        if not CHROMADB_AVAILABLE:
            logger.warning("chromadb_not_available", fallback="memory_disabled")
            self.client = None
            self.collection = None
            return

        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=str(self.storage_path),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )

            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="session_memories",
                metadata={"description": "Cross-session memory storage"}
            )

            logger.info("memory_manager_initialized",
                       storage=str(self.storage_path),
                       memories=self.collection.count())

        except Exception as e:
            logger.error("chromadb_init_failed", error=str(e))
            self.client = None
            self.collection = None

    def is_available(self) -> bool:
        """Check if memory system is available.

        Returns:
            True if ChromaDB is initialized and working.
        """
        return self.collection is not None

    def add_memory(
        self,
        session_id: str,
        content: str,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Add a memory to the knowledge base.

        Args:
            session_id: Source session ID.
            content: Memory content (will be embedded for search).
            tags: Optional tags for categorization.
            metadata: Optional additional metadata.

        Returns:
            Memory ID.

        Raises:
            RuntimeError: If ChromaDB not available.
        """
        if not self.is_available():
            raise RuntimeError("Memory system not available - ChromaDB not initialized")

        memory_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        # Prepare metadata
        meta = {
            "session_id": session_id,
            "timestamp": timestamp,
            "tags": json.dumps(tags or []),
        }
        if metadata:
            meta.update(metadata)

        # Add to ChromaDB (embedding happens automatically)
        self.collection.add(
            ids=[memory_id],
            documents=[content],
            metadatas=[meta]
        )

        logger.info("memory_added",
                   memory_id=memory_id,
                   session_id=session_id,
                   content_length=len(content))

        return memory_id

    def search_memories(
        self,
        query: str,
        limit: int = 5,
        session_id: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Search memories using semantic similarity.

        Args:
            query: Natural language search query.
            limit: Maximum number of results.
            session_id: Optional filter by source session.
            tags: Optional filter by tags.

        Returns:
            List of matching memories with metadata and relevance scores.
        """
        if not self.is_available():
            logger.warning("memory_search_failed", reason="chromadb_not_available")
            return []

        try:
            # Build where filter
            where = None
            if session_id:
                where = {"session_id": session_id}

            # Query ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=limit,
                where=where
            )

            # Format results
            memories = []
            if results and results['ids'] and results['ids'][0]:
                for i, memory_id in enumerate(results['ids'][0]):
                    # ChromaDB uses L2 distance - lower is better
                    # Convert to relevance score (0-1, higher is better)
                    distance = results['distances'][0][i] if 'distances' in results else 0.0
                    # Normalize distance to 0-1 range (assuming max distance ~2)
                    relevance = max(0.0, 1.0 - (distance / 2.0))

                    memory = {
                        "id": memory_id,
                        "content": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": distance,
                        "relevance": relevance,
                        "tags": json.loads(results['metadatas'][0][i].get('tags', '[]'))
                    }

                    # Filter by tags if specified
                    if tags:
                        memory_tags = set(memory['tags'])
                        if not any(tag in memory_tags for tag in tags):
                            continue

                    memories.append(memory)

            logger.info("memory_search_completed",
                       query=query,
                       results=len(memories))

            return memories

        except Exception as e:
            logger.error("memory_search_failed", error=str(e))
            return []

    def get_memories_by_session(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all memories from a specific session.

        Args:
            session_id: Session ID to filter by.

        Returns:
            List of memories from the session.
        """
        if not self.is_available():
            return []

        try:
            results = self.collection.get(
                where={"session_id": session_id}
            )

            memories = []
            if results and results['ids']:
                for i, memory_id in enumerate(results['ids']):
                    memories.append({
                        "id": memory_id,
                        "content": results['documents'][i],
                        "metadata": results['metadatas'][i],
                        "tags": json.loads(results['metadatas'][i].get('tags', '[]'))
                    })

            return memories

        except Exception as e:
            logger.error("get_session_memories_failed", error=str(e))
            return []

    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory by ID.

        Args:
            memory_id: Memory ID to delete.

        Returns:
            True if deleted successfully.
        """
        if not self.is_available():
            return False

        try:
            self.collection.delete(ids=[memory_id])
            logger.info("memory_deleted", memory_id=memory_id)
            return True
        except Exception as e:
            logger.error("memory_delete_failed", error=str(e))
            return False

    def delete_session_memories(self, session_id: str) -> int:
        """Delete all memories from a session.

        Args:
            session_id: Session ID to delete memories for.

        Returns:
            Number of memories deleted.
        """
        if not self.is_available():
            return 0

        try:
            # Get all memories for session
            memories = self.get_memories_by_session(session_id)
            memory_ids = [m['id'] for m in memories]

            if memory_ids:
                self.collection.delete(ids=memory_ids)
                logger.info("session_memories_deleted",
                           session_id=session_id,
                           count=len(memory_ids))

            return len(memory_ids)

        except Exception as e:
            logger.error("delete_session_memories_failed", error=str(e))
            return 0

    def extract_session_knowledge(self, session: Session) -> List[str]:
        """Extract key knowledge points from a session.

        This is a simple heuristic-based extraction. In the future,
        this could use an LLM to intelligently extract learnings.

        Args:
            session: Session to extract knowledge from.

        Returns:
            List of knowledge snippets to save as memories.
        """
        knowledge_points = []

        # For now, extract based on session metadata
        if session.description:
            knowledge_points.append(session.description)

        # Could add more sophisticated extraction here:
        # - Parse commit messages
        # - Analyze file changes
        # - Extract code comments
        # - Use LLM to summarize session

        return knowledge_points

    def get_relevant_context(
        self,
        query: str,
        current_session_id: str,
        limit: int = 3
    ) -> str:
        """Get relevant context from other sessions for a query.

        Args:
            query: What you're working on or need help with.
            current_session_id: Current session ID (to exclude).
            limit: Max number of relevant memories.

        Returns:
            Formatted context string to inject into prompts.
        """
        # Search memories from other sessions
        all_memories = self.search_memories(query, limit=limit * 2)

        # Filter out current session
        other_memories = [
            m for m in all_memories
            if m['metadata'].get('session_id') != current_session_id
        ][:limit]

        if not other_memories:
            return ""

        # Format as context
        context_parts = [
            "=== RELEVANT KNOWLEDGE FROM PAST SESSIONS ===\n"
        ]

        for i, memory in enumerate(other_memories, 1):
            session_id = memory['metadata'].get('session_id', 'unknown')
            timestamp = memory['metadata'].get('timestamp', 'unknown')
            relevance = memory['relevance'] * 100

            context_parts.append(
                f"\n[Memory {i}] (Relevance: {relevance:.0f}%)\n"
                f"From: {session_id[:20]}...\n"
                f"When: {timestamp}\n"
                f"Content: {memory['content']}\n"
            )

        context_parts.append("\n=== END PAST KNOWLEDGE ===\n")

        return "".join(context_parts)

    def get_stats(self) -> Dict[str, Any]:
        """Get memory system statistics.

        Returns:
            Dictionary with stats.
        """
        if not self.is_available():
            return {
                "available": False,
                "total_memories": 0,
                "sessions_with_memories": 0
            }

        total = self.collection.count()

        # Get unique sessions (approximation)
        # In production, you'd maintain this separately
        sessions = set()
        try:
            results = self.collection.get()
            if results and results['metadatas']:
                sessions = {m.get('session_id') for m in results['metadatas']}
        except:
            pass

        return {
            "available": True,
            "total_memories": total,
            "sessions_with_memories": len(sessions),
            "storage_path": str(self.storage_path)
        }
