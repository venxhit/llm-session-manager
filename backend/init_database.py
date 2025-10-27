#!/usr/bin/env python3
"""Initialize database with test users and team for collaboration testing."""

import sys
import os

# Change to script directory so .env file is found
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
sys.path.insert(0, script_dir)

from app.database import engine, Base, SessionLocal
from app.models import Team, User, SessionModel
from app.auth import get_password_hash
from datetime import datetime

def init_database():
    """Initialize database with test data."""

    print()
    print("="*70)
    print("Initializing Database for Real-Time Collaboration")
    print("="*70)
    print()

    # Create tables
    print("📋 Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully")
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False

    # Create database session
    db = SessionLocal()

    try:
        # Check if test team already exists
        existing_team = db.query(Team).filter(Team.name == "Test Team").first()
        if existing_team:
            print("⚠️  Test team already exists, cleaning up old data...")
            # Delete old users
            db.query(User).filter(User.team_id == existing_team.id).delete()
            db.query(Team).filter(Team.id == existing_team.id).delete()
            db.commit()

        # Create test team
        print("\n👥 Creating test team...")
        team = Team(
            name="Test Team",
            description="Team for testing real-time collaboration features",
            settings={}
        )
        db.add(team)
        db.commit()
        db.refresh(team)
        print(f"✅ Team created: {team.name} (ID: {team.id})")

        # Create test users
        print("\n👤 Creating test users...")
        test_password = "testpassword123"  # Same password for all test users

        users_data = [
            {
                "email": "alice@test.com",
                "username": "alice",
                "full_name": "Alice (Host)",
                "role": "admin",
                "user_id": "user_alice"
            },
            {
                "email": "bob@test.com",
                "username": "bob",
                "full_name": "Bob (Editor)",
                "role": "member",
                "user_id": "user_bob"
            },
            {
                "email": "charlie@test.com",
                "username": "charlie",
                "full_name": "Charlie (Viewer)",
                "role": "viewer",
                "user_id": "user_charlie"
            }
        ]

        created_users = []
        for user_data in users_data:
            user = User(
                id=user_data["user_id"],
                email=user_data["email"],
                username=user_data["username"],
                full_name=user_data["full_name"],
                password_hash=get_password_hash(test_password),
                team_id=team.id,
                role=user_data["role"],
                is_active=True,
                is_verified=True,
                preferences={}
            )
            db.add(user)
            created_users.append(user)
            print(f"  ✅ {user.username} ({user.role}) - {user.email}")

        db.commit()

        # Create a test session
        print("\n📝 Creating test session...")
        test_session = SessionModel(
            id="test_session_001",
            pid=12345,
            type="claude",
            status="active",
            start_time=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            working_directory="/Users/test/project",
            team_id=team.id,
            visibility="team",
            project_name="Real-Time Collaboration Test",
            description="Test session for collaboration features",
            tags=["test", "collaboration"]
        )
        db.add(test_session)
        db.commit()
        db.refresh(test_session)
        print(f"✅ Test session created: {test_session.id}")

        print()
        print("="*70)
        print("✅ Database Initialized Successfully!")
        print("="*70)
        print()
        print("Test Users Created:")
        print("-" * 70)
        for user in created_users:
            print(f"  • {user.username:15} | {user.email:25} | {user.role}")
        print()
        print(f"Test Team: {team.name}")
        print(f"Test Session: {test_session.id}")
        print()
        print("Login Credentials:")
        print("-" * 70)
        print(f"  Password (all users): {test_password}")
        print()
        print("Next Steps:")
        print("-" * 70)
        print("  1. Generate JWT tokens:  python3 generate_tokens.py")
        print("  2. Start backend:        uvicorn app.main:app --reload")
        print("  3. Start frontend:       cd frontend && npm run dev")
        print("  4. Open browser:         http://localhost:3000")
        print()

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
