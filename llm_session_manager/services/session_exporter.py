"""Session Exporter - Bridge CLI sessions to Web collaboration."""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional
import structlog

# Add backend to path for imports and change to backend dir so .env is found
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))
original_cwd = os.getcwd()
os.chdir(backend_path)

from backend.app.database import SessionLocal
from backend.app.models import SessionModel as WebSession, Team, User

# Change back to original directory
os.chdir(original_cwd)

logger = structlog.get_logger()


class SessionExporter:
    """Export CLI sessions to web collaboration database."""

    def __init__(self):
        """Initialize exporter with database connection."""
        self.db = None

    def get_db(self):
        """Get or create database session."""
        if self.db is None:
            self.db = SessionLocal()
        return self.db

    def export_session(self, cli_session, owner_user_id: str = "user_alice") -> str:
        """
        Export a CLI session to web collaboration database.

        Args:
            cli_session: Session object from CLI discovery
            owner_user_id: User ID who owns this session

        Returns:
            Web session ID
        """
        db = self.get_db()

        try:
            # Check if session already exists
            existing = db.query(WebSession).filter(
                WebSession.id == cli_session.id
            ).first()

            if existing:
                logger.info("session_already_exported",
                           session_id=cli_session.id)
                # Update existing session
                self._update_session(existing, cli_session, db)
                return existing.id

            # Get or create default team
            team = db.query(Team).filter(Team.name == "Test Team").first()
            if not team:
                logger.warning("no_team_found", creating_default=True)
                team = Team(
                    name="Test Team",
                    description="Default team for shared sessions",
                    settings={}
                )
                db.add(team)
                db.commit()
                db.refresh(team)

            # Create new web session
            web_session = WebSession(
                id=cli_session.id,
                pid=cli_session.pid,
                type=cli_session.type.value if hasattr(cli_session.type, 'value') else str(cli_session.type),
                status=cli_session.status.value if hasattr(cli_session.status, 'value') else str(cli_session.status),
                start_time=cli_session.start_time,
                last_activity=cli_session.last_activity,
                working_directory=cli_session.working_directory,
                token_count=cli_session.token_count,
                token_limit=cli_session.token_limit,
                health_score=cli_session.health_score,
                message_count=cli_session.message_count,
                file_count=cli_session.file_count,
                error_count=cli_session.error_count,
                tags=cli_session.tags if hasattr(cli_session, 'tags') else [],
                project_name=cli_session.project_name if hasattr(cli_session, 'project_name') else None,
                description=cli_session.description if hasattr(cli_session, 'description') else None,
                team_id=team.id,
                visibility="team",
                shared_at=datetime.utcnow(),
                hostname="localhost"
            )

            db.add(web_session)
            db.commit()
            db.refresh(web_session)

            logger.info("session_exported",
                       session_id=web_session.id,
                       token_count=web_session.token_count,
                       health_score=web_session.health_score)

            return web_session.id

        except Exception as e:
            logger.error("export_failed",
                        session_id=cli_session.id,
                        error=str(e))
            db.rollback()
            raise

    def _update_session(self, web_session, cli_session, db):
        """Update existing web session with latest CLI data."""
        try:
            # Update dynamic fields
            web_session.last_activity = cli_session.last_activity
            web_session.token_count = cli_session.token_count
            web_session.health_score = cli_session.health_score
            web_session.message_count = cli_session.message_count
            web_session.file_count = cli_session.file_count
            web_session.error_count = cli_session.error_count
            web_session.status = cli_session.status.value if hasattr(cli_session.status, 'value') else str(cli_session.status)

            db.commit()
            db.refresh(web_session)

            logger.info("session_updated",
                       session_id=web_session.id,
                       token_count=web_session.token_count)

        except Exception as e:
            logger.error("update_failed",
                        session_id=cli_session.id,
                        error=str(e))
            db.rollback()
            raise

    def sync_session_update(self, cli_session) -> bool:
        """
        Sync a single update from CLI to web.

        Args:
            cli_session: Updated session from CLI

        Returns:
            True if successful
        """
        db = self.get_db()

        try:
            web_session = db.query(WebSession).filter(
                WebSession.id == cli_session.id
            ).first()

            if web_session:
                self._update_session(web_session, cli_session, db)
                return True
            else:
                logger.warning("session_not_found_for_sync",
                              session_id=cli_session.id)
                return False

        except Exception as e:
            logger.error("sync_failed",
                        session_id=cli_session.id,
                        error=str(e))
            return False

    def unexport_session(self, session_id: str) -> bool:
        """
        Remove a session from web collaboration.

        Args:
            session_id: Session ID to unexport

        Returns:
            True if successful
        """
        db = self.get_db()

        try:
            web_session = db.query(WebSession).filter(
                WebSession.id == session_id
            ).first()

            if web_session:
                # Update visibility instead of deleting
                web_session.visibility = "private"
                web_session.shared_at = None
                db.commit()

                logger.info("session_unexported", session_id=session_id)
                return True
            else:
                logger.warning("session_not_found", session_id=session_id)
                return False

        except Exception as e:
            logger.error("unexport_failed",
                        session_id=session_id,
                        error=str(e))
            db.rollback()
            return False

    def get_exported_sessions(self):
        """
        Get all currently exported sessions.

        Returns:
            List of exported web sessions
        """
        db = self.get_db()

        try:
            sessions = db.query(WebSession).filter(
                WebSession.visibility == "team",
                WebSession.shared_at.isnot(None)
            ).all()

            return sessions

        except Exception as e:
            logger.error("get_exported_failed", error=str(e))
            return []

    def close(self):
        """Close database connection."""
        if self.db:
            self.db.close()
            self.db = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
