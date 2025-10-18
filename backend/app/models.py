"""SQLAlchemy models for team dashboard."""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from .database import Base


def generate_uuid():
    """Generate UUID string."""
    return str(uuid.uuid4())


# Association tables
session_owners = Table(
    'session_owners',
    Base.metadata,
    Column('session_id', String, ForeignKey('sessions.id'), primary_key=True),
    Column('user_id', String, ForeignKey('users.id'), primary_key=True)
)


class Team(Base):
    """Team model."""
    __tablename__ = "teams"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    settings = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    members = relationship("User", back_populates="team")
    sessions = relationship("SessionModel", back_populates="team")
    insights = relationship("SharedInsight", back_populates="team")
    metrics = relationship("TeamMetric", back_populates="team")


class User(Base):
    """User model."""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)

    # Team association
    team_id = Column(String, ForeignKey("teams.id"))
    role = Column(String, default="member")  # admin, member, viewer

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

    # Settings
    preferences = Column(JSON, default=dict)

    # Relationships
    team = relationship("Team", back_populates="members")
    owned_sessions = relationship(
        "SessionModel",
        secondary=session_owners,
        back_populates="owners"
    )
    shared_insights = relationship("SharedInsight", back_populates="author")


class SessionModel(Base):
    """Extended Session model for team dashboard."""
    __tablename__ = "sessions"

    # Core fields (from CLI version)
    id = Column(String, primary_key=True, default=generate_uuid)
    pid = Column(Integer, nullable=False)
    type = Column(String, nullable=False)  # SessionType enum
    status = Column(String, nullable=False)  # SessionStatus enum
    start_time = Column(DateTime, nullable=False)
    last_activity = Column(DateTime, nullable=False)
    working_directory = Column(String, nullable=False)

    # Token tracking
    token_count = Column(Integer, default=0)
    token_limit = Column(Integer, default=200000)

    # Health metrics
    health_score = Column(Float, default=100.0)
    message_count = Column(Integer, default=0)
    file_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)

    # Organization
    tags = Column(JSON, default=list)  # List of tags
    project_name = Column(String)
    description = Column(Text)

    # Team features (NEW)
    team_id = Column(String, ForeignKey("teams.id"))
    visibility = Column(String, default="private")  # private, team, public
    shared_at = Column(DateTime)
    hostname = Column(String)  # Machine hostname

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    team = relationship("Team", back_populates="sessions")
    owners = relationship(
        "User",
        secondary=session_owners,
        back_populates="owned_sessions"
    )
    history = relationship("SessionHistory", back_populates="session", cascade="all, delete-orphan")
    insights = relationship("SharedInsight", back_populates="session")


class SessionHistory(Base):
    """Session history for tracking changes over time."""
    __tablename__ = "session_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)

    # Metrics snapshot
    token_count = Column(Integer, nullable=False)
    health_score = Column(Float, nullable=False)
    status = Column(String, nullable=False)

    # Timestamp
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    session = relationship("SessionModel", back_populates="history")


class TeamMetric(Base):
    """Team-wide metrics aggregation."""
    __tablename__ = "team_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(String, ForeignKey("teams.id"), nullable=False)

    # Metric data
    metric_type = Column(String, nullable=False)  # token_usage, session_count, etc.
    value = Column(Float, nullable=False)
    metadata = Column(JSON, default=dict)

    # Timestamp
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    team = relationship("Team", back_populates="metrics")


class SharedInsight(Base):
    """Shared insights and learnings."""
    __tablename__ = "shared_insights"

    id = Column(String, primary_key=True, default=generate_uuid)
    team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    session_id = Column(String, ForeignKey("sessions.id"))

    # Content
    insight_type = Column(String, nullable=False)  # learning, pattern, recommendation
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(JSON, default=list)

    # Attribution
    shared_by = Column(String, ForeignKey("users.id"), nullable=False)

    # Engagement
    upvotes = Column(Integer, default=0)
    views = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    team = relationship("Team", back_populates="insights")
    session = relationship("SessionModel", back_populates="insights")
    author = relationship("User", back_populates="shared_insights")


class SessionParticipant(Base):
    """Track participants in collaborative sessions."""
    __tablename__ = "session_participants"

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Role in session
    role = Column(String, nullable=False)  # host, editor, viewer

    # Timestamps
    joined_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    left_at = Column(DateTime)
    last_seen = Column(DateTime, default=datetime.utcnow)

    # Status
    is_active = Column(Boolean, default=True)

    # Relationships
    session = relationship("SessionModel", backref="participants")
    user = relationship("User", backref="participated_sessions")


class SessionMessage(Base):
    """Chat messages and comments in sessions."""
    __tablename__ = "session_messages"

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Message type
    message_type = Column(String, nullable=False)  # chat, comment, system

    # Content
    content = Column(Text, nullable=False)
    metadata = Column(JSON, default=dict)  # {mentions: [], reactions: {}, code_ref: {...}}

    # Threading
    parent_id = Column(String, ForeignKey("session_messages.id", ondelete="CASCADE"))

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)

    # Relationships
    session = relationship("SessionModel", backref="messages")
    user = relationship("User", backref="messages")
    replies = relationship("SessionMessage", backref="parent", remote_side=[id])


class SessionEvent(Base):
    """Track events in collaborative sessions."""
    __tablename__ = "session_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"))

    # Event data
    event_type = Column(String, nullable=False)  # join, leave, edit, cursor_move, etc.
    event_data = Column(JSON, nullable=False, default=dict)

    # Timestamp
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    session = relationship("SessionModel", backref="events")
    user = relationship("User", backref="events")
