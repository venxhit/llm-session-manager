"""WebSocket connection manager for real-time collaboration."""

from typing import Dict, Set, Optional, List
from fastapi import WebSocket
from datetime import datetime
import structlog
import json

logger = structlog.get_logger()


class ConnectionManager:
    """Manages WebSocket connections for collaborative sessions."""

    def __init__(self):
        # session_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}

        # session_id -> user_id -> connection info
        self.session_users: Dict[str, Dict[str, dict]] = {}

        # websocket -> (session_id, user_id)  # Reverse lookup
        self.websocket_to_session: Dict[WebSocket, tuple] = {}

        logger.info("connection_manager_initialized")

    async def connect(
        self,
        websocket: WebSocket,
        session_id: str,
        user_id: str,
        username: str,
        role: str
    ):
        """Connect user to collaborative session.

        Args:
            websocket: WebSocket connection
            session_id: Session ID to join
            user_id: User ID
            username: Username for display
            role: User role (host, editor, viewer)
        """
        await websocket.accept()

        # Add to connections set
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        self.active_connections[session_id].add(websocket)

        # Track user info
        if session_id not in self.session_users:
            self.session_users[session_id] = {}

        self.session_users[session_id][user_id] = {
            "websocket": websocket,
            "user_id": user_id,
            "username": username,
            "role": role,
            "joined_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat()
        }

        # Reverse lookup
        self.websocket_to_session[websocket] = (session_id, user_id)

        logger.info(
            "user_connected",
            session_id=session_id,
            user_id=user_id,
            username=username,
            role=role,
            connection_count=len(self.active_connections[session_id])
        )

        # Notify others
        await self.broadcast_to_session(
            session_id,
            {
                "type": "user_joined",
                "session_id": session_id,
                "user": {
                    "id": user_id,
                    "username": username,
                    "role": role
                },
                "timestamp": datetime.utcnow().isoformat()
            },
            exclude_user=user_id
        )

        # Send current participants list to new user
        participants = self.get_session_participants(session_id)
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id,
            "participants": participants,
            "your_role": role,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def disconnect(self, websocket: WebSocket):
        """Disconnect user from session.

        Args:
            websocket: WebSocket connection to disconnect
        """
        # Get session and user from reverse lookup
        if websocket not in self.websocket_to_session:
            return

        session_id, user_id = self.websocket_to_session[websocket]

        # Remove from connections
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)

            # Clean up empty sessions
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

        # Get user info before removing
        user_info = None
        if session_id in self.session_users:
            user_info = self.session_users[session_id].get(user_id)
            self.session_users[session_id].pop(user_id, None)

            # Clean up empty sessions
            if not self.session_users[session_id]:
                del self.session_users[session_id]

        # Remove reverse lookup
        del self.websocket_to_session[websocket]

        logger.info(
            "user_disconnected",
            session_id=session_id,
            user_id=user_id,
            remaining_users=len(self.session_users.get(session_id, {}))
        )

        # Notify others
        if user_info:
            await self.broadcast_to_session(
                session_id,
                {
                    "type": "user_left",
                    "session_id": session_id,
                    "user_id": user_id,
                    "username": user_info.get("username"),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

    async def broadcast_to_session(
        self,
        session_id: str,
        message: dict,
        exclude_user: Optional[str] = None
    ):
        """Broadcast message to all users in session.

        Args:
            session_id: Session ID
            message: Message dict to broadcast
            exclude_user: Optional user ID to exclude from broadcast
        """
        if session_id not in self.session_users:
            logger.warning(
                "broadcast_to_nonexistent_session",
                session_id=session_id
            )
            return

        disconnected = []

        for user_id, info in self.session_users[session_id].items():
            # Skip excluded user
            if exclude_user and user_id == exclude_user:
                continue

            websocket = info["websocket"]
            try:
                await websocket.send_json(message)
                logger.debug(
                    "message_sent",
                    session_id=session_id,
                    user_id=user_id,
                    message_type=message.get("type")
                )
            except Exception as e:
                logger.error(
                    "broadcast_failed",
                    session_id=session_id,
                    user_id=user_id,
                    error=str(e)
                )
                disconnected.append(websocket)

        # Clean up disconnected websockets
        for ws in disconnected:
            await self.disconnect(ws)

    async def send_to_user(
        self,
        session_id: str,
        user_id: str,
        message: dict
    ):
        """Send message to specific user.

        Args:
            session_id: Session ID
            user_id: User ID
            message: Message dict to send
        """
        if session_id not in self.session_users:
            logger.warning(
                "send_to_user_nonexistent_session",
                session_id=session_id,
                user_id=user_id
            )
            return

        if user_id not in self.session_users[session_id]:
            logger.warning(
                "send_to_nonexistent_user",
                session_id=session_id,
                user_id=user_id
            )
            return

        websocket = self.session_users[session_id][user_id]["websocket"]
        try:
            await websocket.send_json(message)
            logger.debug(
                "direct_message_sent",
                session_id=session_id,
                user_id=user_id,
                message_type=message.get("type")
            )
        except Exception as e:
            logger.error(
                "direct_message_failed",
                session_id=session_id,
                user_id=user_id,
                error=str(e)
            )
            await self.disconnect(websocket)

    def get_session_participants(self, session_id: str) -> List[dict]:
        """Get list of participants in session.

        Args:
            session_id: Session ID

        Returns:
            List of participant dicts
        """
        if session_id not in self.session_users:
            return []

        return [
            {
                "id": user_id,
                "username": info["username"],
                "role": info["role"],
                "joined_at": info["joined_at"]
            }
            for user_id, info in self.session_users[session_id].items()
        ]

    def get_user_count(self, session_id: str) -> int:
        """Get number of users in session.

        Args:
            session_id: Session ID

        Returns:
            User count
        """
        return len(self.session_users.get(session_id, {}))

    def is_user_in_session(self, session_id: str, user_id: str) -> bool:
        """Check if user is in session.

        Args:
            session_id: Session ID
            user_id: User ID

        Returns:
            True if user is in session
        """
        return (
            session_id in self.session_users and
            user_id in self.session_users[session_id]
        )

    def get_user_role(self, session_id: str, user_id: str) -> Optional[str]:
        """Get user's role in session.

        Args:
            session_id: Session ID
            user_id: User ID

        Returns:
            Role string or None
        """
        if session_id in self.session_users:
            if user_id in self.session_users[session_id]:
                return self.session_users[session_id][user_id]["role"]
        return None

    def get_all_sessions(self) -> List[str]:
        """Get list of all active session IDs.

        Returns:
            List of session IDs
        """
        return list(self.active_connections.keys())

    def get_stats(self) -> dict:
        """Get connection statistics.

        Returns:
            Statistics dict
        """
        total_connections = sum(
            len(conns) for conns in self.active_connections.values()
        )

        return {
            "active_sessions": len(self.active_connections),
            "total_connections": total_connections,
            "sessions": {
                session_id: {
                    "user_count": len(users),
                    "users": [
                        {"id": uid, "username": info["username"], "role": info["role"]}
                        for uid, info in users.items()
                    ]
                }
                for session_id, users in self.session_users.items()
            }
        }
