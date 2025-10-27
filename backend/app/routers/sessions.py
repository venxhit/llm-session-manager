"""Sessions router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import SessionModel

router = APIRouter()


@router.get("/")
async def list_sessions(db: Session = Depends(get_db)):
    """List all sessions."""
    sessions = db.query(SessionModel).all()
    return {
        "sessions": [
            {
                "id": s.id,
                "type": s.type,
                "status": s.status,
                "token_count": s.token_count,
                "health_score": s.health_score,
                "start_time": s.start_time.isoformat(),
            }
            for s in sessions
        ]
    }


@router.get("/{session_id}")
async def get_session(session_id: str, db: Session = Depends(get_db)):
    """Get a specific session by ID."""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "id": session.id,
        "pid": session.pid,
        "type": session.type,
        "status": session.status,
        "start_time": session.start_time.isoformat() if session.start_time else None,
        "last_activity": session.last_activity.isoformat() if session.last_activity else None,
        "working_directory": session.working_directory,
        "token_count": session.token_count,
        "token_limit": session.token_limit,
        "health_score": session.health_score,
        "message_count": session.message_count,
        "file_count": session.file_count,
        "error_count": session.error_count,
        "tags": session.tags or [],
        "project_name": session.project_name,
        "description": session.description,
        "visibility": session.visibility,
        "shared_at": session.shared_at.isoformat() if session.shared_at else None,
    }
