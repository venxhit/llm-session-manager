"""WebSocket endpoint for real-time collaboration."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import structlog
import json

from .database import get_db
from .auth import get_current_user_ws
from .models import SessionModel, SessionParticipant, SessionEvent, User
from .collaboration import ConnectionManager, PresenceManager, ChatManager
from datetime import datetime

logger = structlog.get_logger()

# Create router
router = APIRouter()

# Global managers (singleton instances)
connection_manager = ConnectionManager()
presence_manager = PresenceManager(stale_threshold_minutes=5)


@router.on_event("startup")
async def startup():
    """Start presence cleanup task."""
    await presence_manager.start_cleanup_task()


@router.on_event("shutdown")
async def shutdown():
    """Stop presence cleanup task."""
    await presence_manager.stop_cleanup_task()


@router.websocket("/session/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for collaborative session.

    Args:
        websocket: WebSocket connection
        session_id: Session ID to join
        token: JWT authentication token
        db: Database session
    """
    user = None
    role = None

    try:
        # Authenticate user
        user = await get_current_user_ws(token, db)

        # Check if session exists
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not session:
            await websocket.close(code=1008, reason="Session not found")
            return

        # Determine user role in session
        role = await get_user_role(db, session_id, user.id, session)

        # Connect user
        await connection_manager.connect(
            websocket=websocket,
            session_id=session_id,
            user_id=user.id,
            username=user.username,
            role=role
        )

        # Update presence
        presence_manager.update_presence(
            session_id=session_id,
            user_id=user.id,
            username=user.username,
            status="active"
        )

        # Record join event
        await record_event(db, session_id, user.id, "join", {})

        # Create or update participant record
        participant = db.query(SessionParticipant).filter(
            SessionParticipant.session_id == session_id,
            SessionParticipant.user_id == user.id
        ).first()

        if participant:
            participant.is_active = True
            participant.last_seen = datetime.utcnow()
        else:
            participant = SessionParticipant(
                session_id=session_id,
                user_id=user.id,
                role=role,
                joined_at=datetime.utcnow()
            )
            db.add(participant)

        db.commit()

        # Main message loop
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

            logger.info("websocket_message_received",
                       session_id=session_id,
                       user_id=user.id,
                       message_type=message.get("type"))

            # Handle message
            await handle_message(
                websocket=websocket,
                session_id=session_id,
                user=user,
                role=role,
                message=message,
                db=db
            )

            # Update last seen
            participant.last_seen = datetime.utcnow()
            db.commit()

    except WebSocketDisconnect:
        logger.info("websocket_disconnected",
                   session_id=session_id,
                   user_id=user.id if user else None)

    except Exception as e:
        logger.error("websocket_error",
                    session_id=session_id,
                    user_id=user.id if user else None,
                    error=str(e))

        try:
            await websocket.close(code=1011, reason=str(e))
        except:
            pass

    finally:
        # Cleanup
        if user:
            # Disconnect from connection manager
            await connection_manager.disconnect(websocket)

            # Remove from presence
            presence_manager.remove_user(session_id, user.id)

            # Update participant record
            participant = db.query(SessionParticipant).filter(
                SessionParticipant.session_id == session_id,
                SessionParticipant.user_id == user.id,
                SessionParticipant.is_active == True
            ).first()

            if participant:
                participant.is_active = False
                participant.left_at = datetime.utcnow()
                db.commit()

            # Record leave event
            await record_event(db, session_id, user.id, "leave", {})


async def handle_message(
    websocket: WebSocket,
    session_id: str,
    user: User,
    role: str,
    message: dict,
    db: Session
):
    """Handle incoming WebSocket message.

    Args:
        websocket: WebSocket connection
        session_id: Session ID
        user: User model
        role: User role
        message: Message dict
        db: Database session
    """
    message_type = message.get("type")

    # Chat message
    if message_type == "chat_message":
        await handle_chat_message(session_id, user, message, db)

    # Cursor update
    elif message_type == "cursor_update":
        await handle_cursor_update(session_id, user, message)

    # Viewport update
    elif message_type == "viewport_update":
        await handle_viewport_update(session_id, user, message)

    # Presence status update
    elif message_type == "presence_update":
        await handle_presence_update(session_id, user, message)

    # Code comment
    elif message_type == "code_comment":
        await handle_code_comment(session_id, user, role, message, db)

    # Reaction
    elif message_type == "reaction":
        await handle_reaction(session_id, user, message, db)

    # Session update (requires editor role)
    elif message_type == "session_update":
        if role in ["host", "editor"]:
            await handle_session_update(session_id, user, message, db)
        else:
            await send_error(websocket, "PERMISSION_DENIED", "You don't have permission to edit this session")

    # Unknown message type
    else:
        logger.warning("unknown_message_type",
                      message_type=message_type,
                      user_id=user.id)


async def handle_chat_message(session_id: str, user: User, message: dict, db: Session):
    """Handle chat message."""
    content = message.get("content", "")

    if not content.strip():
        return

    chat_manager = ChatManager(db)
    msg = chat_manager.send_message(
        session_id=session_id,
        user_id=user.id,
        username=user.username,
        content=content,
        message_type="chat"
    )

    # Broadcast to all users in session
    await connection_manager.broadcast_to_session(
        session_id,
        {
            "type": "chat_message",
            "message": msg
        }
    )

    # Record event
    await record_event(db, session_id, user.id, "chat_message", {"content": content[:100]})


async def handle_cursor_update(session_id: str, user: User, message: dict):
    """Handle cursor position update."""
    cursor_data = message.get("data", {})

    presence_manager.update_cursor(
        session_id=session_id,
        user_id=user.id,
        file=cursor_data.get("file", ""),
        line=cursor_data.get("line", 0),
        column=cursor_data.get("column", 0)
    )

    # Broadcast cursor update to others
    await connection_manager.broadcast_to_session(
        session_id,
        {
            "type": "cursor_update",
            "user_id": user.id,
            "cursor": cursor_data
        },
        exclude_user=user.id
    )


async def handle_viewport_update(session_id: str, user: User, message: dict):
    """Handle viewport update."""
    viewport_data = message.get("data", {})

    presence_manager.update_viewport(
        session_id=session_id,
        user_id=user.id,
        file=viewport_data.get("file", ""),
        start_line=viewport_data.get("start_line", 0),
        end_line=viewport_data.get("end_line", 0)
    )

    # Broadcast viewport update
    await connection_manager.broadcast_to_session(
        session_id,
        {
            "type": "viewport_update",
            "user_id": user.id,
            "viewport": viewport_data
        },
        exclude_user=user.id
    )


async def handle_presence_update(session_id: str, user: User, message: dict):
    """Handle presence status update."""
    status = message.get("status", "active")

    presence_manager.set_user_status(session_id, user.id, status)

    # Broadcast presence update
    await connection_manager.broadcast_to_session(
        session_id,
        {
            "type": "presence_update",
            "user_id": user.id,
            "status": status
        }
    )


async def handle_code_comment(session_id: str, user: User, role: str, message: dict, db: Session):
    """Handle code comment."""
    if role == "viewer":
        return  # Viewers can't comment

    data = message.get("data", {})

    chat_manager = ChatManager(db)
    comment = chat_manager.add_code_comment(
        session_id=session_id,
        user_id=user.id,
        username=user.username,
        file=data.get("file", ""),
        line=data.get("line", 0),
        content=data.get("content", ""),
        code_snippet=data.get("code_snippet")
    )

    # Broadcast comment
    await connection_manager.broadcast_to_session(
        session_id,
        {
            "type": "code_comment",
            "comment": comment
        }
    )

    # Record event
    await record_event(db, session_id, user.id, "code_comment", {
        "file": data.get("file"),
        "line": data.get("line")
    })


async def handle_reaction(session_id: str, user: User, message: dict, db: Session):
    """Handle message reaction."""
    message_id = message.get("message_id")
    emoji = message.get("emoji")
    action = message.get("action", "add")  # add or remove

    if not message_id or not emoji:
        return

    chat_manager = ChatManager(db)

    if action == "add":
        chat_manager.add_reaction(message_id, user.id, emoji)
    else:
        chat_manager.remove_reaction(message_id, user.id, emoji)

    # Broadcast reaction update
    await connection_manager.broadcast_to_session(
        session_id,
        {
            "type": "reaction_update",
            "message_id": message_id,
            "user_id": user.id,
            "emoji": emoji,
            "action": action
        }
    )


async def handle_session_update(session_id: str, user: User, message: dict, db: Session):
    """Handle session metadata update."""
    changes = message.get("changes", {})

    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        return

    # Update allowed fields
    if "tags" in changes:
        session.tags = changes["tags"]
    if "description" in changes:
        session.description = changes["description"]
    if "status" in changes:
        session.status = changes["status"]

    session.updated_at = datetime.utcnow()
    db.commit()

    # Broadcast session update
    await connection_manager.broadcast_to_session(
        session_id,
        {
            "type": "session_update",
            "changes": changes,
            "updated_by": user.id
        }
    )

    # Record event
    await record_event(db, session_id, user.id, "session_update", changes)


async def get_user_role(db: Session, session_id: str, user_id: str, session: SessionModel) -> str:
    """Determine user's role in session.

    Args:
        db: Database session
        session_id: Session ID
        user_id: User ID
        session: Session model

    Returns:
        Role string (host, editor, viewer)
    """
    # Check if user is owner
    if any(owner.id == user_id for owner in session.owners):
        return "host"

    # Check participant record
    participant = db.query(SessionParticipant).filter(
        SessionParticipant.session_id == session_id,
        SessionParticipant.user_id == user_id
    ).first()

    if participant:
        return participant.role

    # Default to viewer for team members
    if session.team_id and session.visibility == "team":
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.team_id == session.team_id:
            return "viewer"

    # No permission
    raise HTTPException(status_code=403, detail="No permission to access this session")


async def record_event(db: Session, session_id: str, user_id: str, event_type: str, event_data: dict):
    """Record session event."""
    event = SessionEvent(
        session_id=session_id,
        user_id=user_id,
        event_type=event_type,
        event_data=event_data,
        timestamp=datetime.utcnow()
    )

    db.add(event)
    db.commit()


async def send_error(websocket: WebSocket, error_code: str, message: str):
    """Send error message to client."""
    try:
        await websocket.send_json({
            "type": "error",
            "error_code": error_code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        })
    except:
        pass


# Stats endpoint for monitoring
@router.get("/stats")
async def get_collaboration_stats():
    """Get collaboration statistics."""
    return {
        "connections": connection_manager.get_stats(),
        "presence": presence_manager.get_stats()
    }
