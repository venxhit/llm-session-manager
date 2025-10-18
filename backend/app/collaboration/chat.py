"""Chat and messaging for collaborative sessions."""

from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from datetime import datetime
import structlog
import re

logger = structlog.get_logger()


class ChatManager:
    """Manages chat messages and comments in collaborative sessions."""

    def __init__(self, db: Session):
        """Initialize chat manager.

        Args:
            db: Database session
        """
        self.db = db
        logger.info("chat_manager_initialized")

    def send_message(
        self,
        session_id: str,
        user_id: str,
        username: str,
        content: str,
        message_type: str = "chat",
        metadata: Optional[dict] = None,
        parent_id: Optional[str] = None
    ) -> dict:
        """Create and save chat message.

        Args:
            session_id: Session ID
            user_id: User ID
            username: Username for display
            content: Message content
            message_type: Type (chat, comment, system)
            metadata: Additional metadata
            parent_id: Parent message ID for threading

        Returns:
            Message dict
        """
        from ..models import SessionMessage

        # Extract mentions
        mentions = self._extract_mentions(content)

        # Create message
        message = SessionMessage(
            session_id=session_id,
            user_id=user_id,
            message_type=message_type,
            content=content,
            metadata={
                **(metadata or {}),
                "mentions": mentions,
                "reactions": {}
            },
            parent_id=parent_id,
            created_at=datetime.utcnow()
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        logger.info("message_sent",
                   session_id=session_id,
                   user_id=user_id,
                   message_id=message.id,
                   message_type=message_type)

        return self._message_to_dict(message, username)

    def get_messages(
        self,
        session_id: str,
        limit: int = 50,
        before: Optional[datetime] = None,
        message_type: Optional[str] = None
    ) -> List[dict]:
        """Get chat messages for session.

        Args:
            session_id: Session ID
            limit: Max messages to return
            before: Get messages before this timestamp
            message_type: Filter by message type

        Returns:
            List of message dicts
        """
        from ..models import SessionMessage, User

        query = self.db.query(SessionMessage, User).join(
            User, SessionMessage.user_id == User.id
        ).filter(
            SessionMessage.session_id == session_id,
            SessionMessage.deleted_at.is_(None)
        )

        if before:
            query = query.filter(SessionMessage.created_at < before)

        if message_type:
            query = query.filter(SessionMessage.message_type == message_type)

        results = query.order_by(
            SessionMessage.created_at.desc()
        ).limit(limit).all()

        messages = []
        for message, user in results:
            messages.append(self._message_to_dict(message, user.username))

        # Reverse to get chronological order
        return list(reversed(messages))

    def get_message(self, message_id: str) -> Optional[dict]:
        """Get specific message by ID.

        Args:
            message_id: Message ID

        Returns:
            Message dict or None
        """
        from ..models import SessionMessage, User

        result = self.db.query(SessionMessage, User).join(
            User, SessionMessage.user_id == User.id
        ).filter(
            SessionMessage.id == message_id,
            SessionMessage.deleted_at.is_(None)
        ).first()

        if result:
            message, user = result
            return self._message_to_dict(message, user.username)

        return None

    def delete_message(self, message_id: str, user_id: str) -> bool:
        """Soft delete message (only by author).

        Args:
            message_id: Message ID
            user_id: User ID (must be author)

        Returns:
            True if deleted successfully
        """
        from ..models import SessionMessage

        message = self.db.query(SessionMessage).filter(
            SessionMessage.id == message_id,
            SessionMessage.user_id == user_id,
            SessionMessage.deleted_at.is_(None)
        ).first()

        if message:
            message.deleted_at = datetime.utcnow()
            self.db.commit()

            logger.info("message_deleted",
                       message_id=message_id,
                       user_id=user_id)
            return True

        return False

    def edit_message(self, message_id: str, user_id: str, new_content: str) -> Optional[dict]:
        """Edit message content (only by author).

        Args:
            message_id: Message ID
            user_id: User ID (must be author)
            new_content: New message content

        Returns:
            Updated message dict or None
        """
        from ..models import SessionMessage, User

        result = self.db.query(SessionMessage, User).join(
            User, SessionMessage.user_id == User.id
        ).filter(
            SessionMessage.id == message_id,
            SessionMessage.user_id == user_id,
            SessionMessage.deleted_at.is_(None)
        ).first()

        if result:
            message, user = result
            message.content = new_content
            message.updated_at = datetime.utcnow()

            # Update mentions
            mentions = self._extract_mentions(new_content)
            metadata = message.metadata or {}
            metadata["mentions"] = mentions
            message.metadata = metadata

            self.db.commit()
            self.db.refresh(message)

            logger.info("message_edited",
                       message_id=message_id,
                       user_id=user_id)

            return self._message_to_dict(message, user.username)

        return None

    def add_reaction(self, message_id: str, user_id: str, emoji: str) -> bool:
        """Add emoji reaction to message.

        Args:
            message_id: Message ID
            user_id: User ID
            emoji: Emoji string

        Returns:
            True if added successfully
        """
        from ..models import SessionMessage

        message = self.db.query(SessionMessage).filter(
            SessionMessage.id == message_id,
            SessionMessage.deleted_at.is_(None)
        ).first()

        if message:
            metadata = message.metadata or {}
            reactions = metadata.get("reactions", {})

            # Add user to emoji reactions
            if emoji not in reactions:
                reactions[emoji] = []

            if user_id not in reactions[emoji]:
                reactions[emoji].append(user_id)

            metadata["reactions"] = reactions
            message.metadata = metadata
            self.db.commit()

            logger.info("reaction_added",
                       message_id=message_id,
                       user_id=user_id,
                       emoji=emoji)
            return True

        return False

    def remove_reaction(self, message_id: str, user_id: str, emoji: str) -> bool:
        """Remove emoji reaction from message.

        Args:
            message_id: Message ID
            user_id: User ID
            emoji: Emoji string

        Returns:
            True if removed successfully
        """
        from ..models import SessionMessage

        message = self.db.query(SessionMessage).filter(
            SessionMessage.id == message_id,
            SessionMessage.deleted_at.is_(None)
        ).first()

        if message:
            metadata = message.metadata or {}
            reactions = metadata.get("reactions", {})

            if emoji in reactions and user_id in reactions[emoji]:
                reactions[emoji].remove(user_id)

                # Clean up empty emoji lists
                if not reactions[emoji]:
                    del reactions[emoji]

                metadata["reactions"] = reactions
                message.metadata = metadata
                self.db.commit()

                logger.info("reaction_removed",
                           message_id=message_id,
                           user_id=user_id,
                           emoji=emoji)
                return True

        return False

    def add_code_comment(
        self,
        session_id: str,
        user_id: str,
        username: str,
        file: str,
        line: int,
        content: str,
        code_snippet: Optional[str] = None
    ) -> dict:
        """Add a code comment at specific file location.

        Args:
            session_id: Session ID
            user_id: User ID
            username: Username
            file: File path
            line: Line number
            content: Comment content
            code_snippet: Optional code snippet

        Returns:
            Comment dict
        """
        metadata = {
            "file": file,
            "line": line,
            "code_snippet": code_snippet
        }

        return self.send_message(
            session_id=session_id,
            user_id=user_id,
            username=username,
            content=content,
            message_type="comment",
            metadata=metadata
        )

    def get_code_comments(
        self,
        session_id: str,
        file: Optional[str] = None,
        line: Optional[int] = None
    ) -> List[dict]:
        """Get code comments for session, optionally filtered by file/line.

        Args:
            session_id: Session ID
            file: Optional file path filter
            line: Optional line number filter

        Returns:
            List of comment dicts
        """
        from ..models import SessionMessage, User

        query = self.db.query(SessionMessage, User).join(
            User, SessionMessage.user_id == User.id
        ).filter(
            SessionMessage.session_id == session_id,
            SessionMessage.message_type == "comment",
            SessionMessage.deleted_at.is_(None)
        )

        results = query.order_by(SessionMessage.created_at.desc()).all()

        comments = []
        for message, user in results:
            comment_dict = self._message_to_dict(message, user.username)

            # Filter by file/line if specified
            if file and comment_dict.get("metadata", {}).get("file") != file:
                continue
            if line is not None and comment_dict.get("metadata", {}).get("line") != line:
                continue

            comments.append(comment_dict)

        return comments

    def get_thread(self, parent_id: str) -> List[dict]:
        """Get threaded replies to a message.

        Args:
            parent_id: Parent message ID

        Returns:
            List of reply message dicts
        """
        from ..models import SessionMessage, User

        results = self.db.query(SessionMessage, User).join(
            User, SessionMessage.user_id == User.id
        ).filter(
            SessionMessage.parent_id == parent_id,
            SessionMessage.deleted_at.is_(None)
        ).order_by(SessionMessage.created_at.asc()).all()

        return [
            self._message_to_dict(message, user.username)
            for message, user in results
        ]

    def _extract_mentions(self, content: str) -> List[str]:
        """Extract @mentions from message content.

        Args:
            content: Message content

        Returns:
            List of mentioned usernames
        """
        # Match @username pattern
        mentions = re.findall(r'@(\w+)', content)
        return list(set(mentions))  # Remove duplicates

    def _message_to_dict(self, message, username: str) -> dict:
        """Convert message model to dict.

        Args:
            message: SessionMessage model
            username: Username string

        Returns:
            Message dict
        """
        return {
            "id": message.id,
            "session_id": message.session_id,
            "user_id": message.user_id,
            "username": username,
            "message_type": message.message_type,
            "content": message.content,
            "metadata": message.metadata or {},
            "parent_id": message.parent_id,
            "created_at": message.created_at.isoformat(),
            "updated_at": message.updated_at.isoformat() if message.updated_at else None,
            "deleted_at": message.deleted_at.isoformat() if message.deleted_at else None
        }

    def get_stats(self, session_id: str) -> dict:
        """Get chat statistics for session.

        Args:
            session_id: Session ID

        Returns:
            Statistics dict
        """
        from ..models import SessionMessage

        total_messages = self.db.query(SessionMessage).filter(
            SessionMessage.session_id == session_id,
            SessionMessage.deleted_at.is_(None)
        ).count()

        chat_messages = self.db.query(SessionMessage).filter(
            SessionMessage.session_id == session_id,
            SessionMessage.message_type == "chat",
            SessionMessage.deleted_at.is_(None)
        ).count()

        comments = self.db.query(SessionMessage).filter(
            SessionMessage.session_id == session_id,
            SessionMessage.message_type == "comment",
            SessionMessage.deleted_at.is_(None)
        ).count()

        return {
            "total_messages": total_messages,
            "chat_messages": chat_messages,
            "comments": comments,
            "system_messages": total_messages - chat_messages - comments
        }
