#!/usr/bin/env python3
"""Database migration script to add missing columns to sessions table."""

import sqlite3
import sys
from pathlib import Path


def migrate_database(db_path: str = "data/sessions.db"):
    """Add missing columns to sessions table.

    Args:
        db_path: Path to SQLite database file.
    """
    print(f"🔧 Migrating database: {db_path}")

    # Check if database exists
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        print("💡 Database will be created with correct schema on first use.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get current columns
    cursor.execute("PRAGMA table_info(sessions)")
    columns = {row[1] for row in cursor.fetchall()}
    print(f"📊 Current columns: {columns}")

    migrations_applied = []

    # Add tags column if missing
    if 'tags' not in columns:
        print("➕ Adding 'tags' column...")
        cursor.execute("""
            ALTER TABLE sessions
            ADD COLUMN tags TEXT DEFAULT '[]'
        """)
        migrations_applied.append("tags")

    # Add project_name column if missing
    if 'project_name' not in columns:
        print("➕ Adding 'project_name' column...")
        cursor.execute("""
            ALTER TABLE sessions
            ADD COLUMN project_name TEXT
        """)
        migrations_applied.append("project_name")

    # Add description column if missing
    if 'description' not in columns:
        print("➕ Adding 'description' column...")
        cursor.execute("""
            ALTER TABLE sessions
            ADD COLUMN description TEXT
        """)
        migrations_applied.append("description")

    # Commit changes
    conn.commit()

    # Verify migrations
    cursor.execute("PRAGMA table_info(sessions)")
    new_columns = {row[1] for row in cursor.fetchall()}

    conn.close()

    if migrations_applied:
        print(f"✅ Migration complete! Added columns: {', '.join(migrations_applied)}")
        print(f"📊 New columns: {new_columns}")
    else:
        print("✅ Database already up to date! No migrations needed.")

    print("\n🎉 Database ready for tagging features!")


if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else "data/sessions.db"
    migrate_database(db_path)
