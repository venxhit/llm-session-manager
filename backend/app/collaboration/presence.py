"""Presence management for tracking user activity and location in sessions."""

from typing import Dict, Optional, List
from datetime import datetime, timedelta
import asyncio
import structlog

logger = structlog.get_logger()


class PresenceManager:
    """Manages user presence in collaborative sessions.

    Tracks:
    - Online/offline status
    - Active/idle/away state
    - Cursor position (file, line, column)
    - Viewport (what user is viewing)
    - Last activity timestamp
    """

    def __init__(self, stale_threshold_minutes: int = 5):
        """Initialize presence manager.

        Args:
            stale_threshold_minutes: Minutes of inactivity before marking as stale
        """
        # session_id -> user_id -> presence data
        self.presence: Dict[str, Dict[str, dict]] = {}

        self.stale_threshold = timedelta(minutes=stale_threshold_minutes)

        # Start background cleanup task
        self._cleanup_task = None

        logger.info("presence_manager_initialized",
                   stale_threshold_minutes=stale_threshold_minutes)

    async def start_cleanup_task(self):
        """Start background task to clean up stale presence."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_stale_presence())
            logger.info("presence_cleanup_task_started")

    async def stop_cleanup_task(self):
        """Stop background cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            logger.info("presence_cleanup_task_stopped")

    def update_presence(
        self,
        session_id: str,
        user_id: str,
        username: str,
        status: Optional[str] = None,
        cursor: Optional[dict] = None,
        viewport: Optional[dict] = None
    ) -> dict:
        """Update user presence in session.

        Args:
            session_id: Session ID
            user_id: User ID
            username: Username for display
            status: User status (active, idle, away)
            cursor: Cursor position {file, line, column}
            viewport: Viewport {file, start_line, end_line}

        Returns:
            Updated presence data
        """
        if session_id not in self.presence:
            self.presence[session_id] = {}

        now = datetime.utcnow()

        # Get existing presence or create new
        if user_id in self.presence[session_id]:
            presence_data = self.presence[session_id][user_id]
        else:
            presence_data = {
                "user_id": user_id,
                "username": username,
                "status": "active",
                "cursor": None,
                "viewport": None,
                "joined_at": now.isoformat(),
                "last_update": now.isoformat()
            }

        # Update fields
        if status:
            presence_data["status"] = status
        if cursor:
            presence_data["cursor"] = cursor
        if viewport:
            presence_data["viewport"] = viewport

        presence_data["last_update"] = now.isoformat()

        self.presence[session_id][user_id] = presence_data

        logger.debug("presence_updated",
                    session_id=session_id,
                    user_id=user_id,
                    status=presence_data["status"])

        return presence_data

    def get_presence(self, session_id: str, user_id: Optional[str] = None) -> dict:
        """Get presence data for session or specific user.

        Args:
            session_id: Session ID
            user_id: Optional user ID (if None, returns all)

        Returns:
            Presence data dict
        """
        if session_id not in self.presence:
            return {} if user_id is None else None

        if user_id:
            return self.presence[session_id].get(user_id)

        return self.presence[session_id]

    def get_all_presence(self, session_id: str) -> List[dict]:
        """Get list of all presence data for session.

        Args:
            session_id: Session ID

        Returns:
            List of presence dicts
        """
        if session_id not in self.presence:
            return []

        return list(self.presence[session_id].values())

    def get_active_users(self, session_id: str) -> List[dict]:
        """Get list of active users in session.

        Args:
            session_id: Session ID

        Returns:
            List of active user presence dicts
        """
        all_presence = self.get_all_presence(session_id)
        return [p for p in all_presence if p.get("status") == "active"]

    def remove_user(self, session_id: str, user_id: str):
        """Remove user from presence tracking.

        Args:
            session_id: Session ID
            user_id: User ID
        """
        if session_id in self.presence:
            removed = self.presence[session_id].pop(user_id, None)

            # Clean up empty sessions
            if not self.presence[session_id]:
                del self.presence[session_id]

            if removed:
                logger.info("presence_removed",
                          session_id=session_id,
                          user_id=user_id)

    def set_user_status(self, session_id: str, user_id: str, status: str):
        """Set user status (active, idle, away).

        Args:
            session_id: Session ID
            user_id: User ID
            status: New status
        """
        if session_id in self.presence and user_id in self.presence[session_id]:
            self.presence[session_id][user_id]["status"] = status
            self.presence[session_id][user_id]["last_update"] = datetime.utcnow().isoformat()

            logger.debug("user_status_updated",
                        session_id=session_id,
                        user_id=user_id,
                        status=status)

    def update_cursor(
        self,
        session_id: str,
        user_id: str,
        file: str,
        line: int,
        column: int
    ):
        """Update user cursor position.

        Args:
            session_id: Session ID
            user_id: User ID
            file: File path
            line: Line number
            column: Column number
        """
        cursor = {
            "file": file,
            "line": line,
            "column": column
        }

        if session_id in self.presence and user_id in self.presence[session_id]:
            self.presence[session_id][user_id]["cursor"] = cursor
            self.presence[session_id][user_id]["last_update"] = datetime.utcnow().isoformat()

    def update_viewport(
        self,
        session_id: str,
        user_id: str,
        file: str,
        start_line: int,
        end_line: int
    ):
        """Update user viewport (what they're viewing).

        Args:
            session_id: Session ID
            user_id: User ID
            file: File path
            start_line: Start line
            end_line: End line
        """
        viewport = {
            "file": file,
            "start_line": start_line,
            "end_line": end_line
        }

        if session_id in self.presence and user_id in self.presence[session_id]:
            self.presence[session_id][user_id]["viewport"] = viewport
            self.presence[session_id][user_id]["last_update"] = datetime.utcnow().isoformat()

    def get_users_viewing_file(self, session_id: str, file: str) -> List[dict]:
        """Get users currently viewing a specific file.

        Args:
            session_id: Session ID
            file: File path

        Returns:
            List of user presence dicts viewing the file
        """
        all_presence = self.get_all_presence(session_id)
        return [
            p for p in all_presence
            if p.get("viewport", {}).get("file") == file or
               p.get("cursor", {}).get("file") == file
        ]

    def is_user_active(self, session_id: str, user_id: str) -> bool:
        """Check if user is active in session.

        Args:
            session_id: Session ID
            user_id: User ID

        Returns:
            True if user is active
        """
        presence = self.get_presence(session_id, user_id)
        if not presence:
            return False

        # Check if last update is recent
        last_update = datetime.fromisoformat(presence["last_update"])
        is_recent = (datetime.utcnow() - last_update) < self.stale_threshold

        return is_recent and presence.get("status") == "active"

    async def _cleanup_stale_presence(self):
        """Background task to remove stale presence data."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute

                now = datetime.utcnow()
                removed_count = 0

                # Check all sessions
                for session_id in list(self.presence.keys()):
                    for user_id in list(self.presence[session_id].keys()):
                        presence = self.presence[session_id][user_id]
                        last_update = datetime.fromisoformat(presence["last_update"])

                        # Remove if stale
                        if (now - last_update) > self.stale_threshold:
                            self.remove_user(session_id, user_id)
                            removed_count += 1
                            logger.info("stale_presence_removed",
                                      session_id=session_id,
                                      user_id=user_id,
                                      last_update=presence["last_update"])

                if removed_count > 0:
                    logger.info("presence_cleanup_completed",
                              removed_count=removed_count)

            except asyncio.CancelledError:
                logger.info("presence_cleanup_cancelled")
                break
            except Exception as e:
                logger.error("presence_cleanup_error", error=str(e))

    def get_stats(self) -> dict:
        """Get presence statistics.

        Returns:
            Statistics dict
        """
        total_users = sum(len(users) for users in self.presence.values())
        active_users = sum(
            len([u for u in users.values() if u.get("status") == "active"])
            for users in self.presence.values()
        )

        return {
            "total_sessions": len(self.presence),
            "total_users": total_users,
            "active_users": active_users,
            "sessions": {
                session_id: {
                    "user_count": len(users),
                    "active_count": len([u for u in users.values() if u.get("status") == "active"]),
                    "users": list(users.keys())
                }
                for session_id, users in self.presence.items()
            }
        }
