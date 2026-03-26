"""
MySQL Setup & Seed Script
DMMMSU-SLUC Disaster/Emergency Incident Report Monitoring System

Run once before starting the Flask app:
    python mysql_setup.py

Requirements: mysql-connector-python, werkzeug
"""

import os
import sys

# Try importing required packages
try:
    import mysql.connector
    from mysql.connector import errorcode
except ImportError:
    sys.exit("❌  mysql-connector-python not installed. Run: pip install mysql-connector-python")

try:
    from werkzeug.security import generate_password_hash
except ImportError:
    sys.exit("❌  werkzeug not installed. Run: pip install werkzeug")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv optional; fall back to os.environ

# ---------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------
DB_HOST     = os.environ.get("DB_HOST", "127.0.0.1")
DB_PORT     = int(os.environ.get("DB_PORT", 3307))
DB_USER     = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_NAME     = os.environ.get("DB_NAME", "campus_incidents_db")

SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "schema.sql")


def get_connection(database=None):
    """Return a mysql.connector connection."""
    kwargs = dict(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        charset="utf8mb4",
    )
    if database:
        kwargs["database"] = database
    return mysql.connector.connect(**kwargs)


def run_schema(cursor, sql_file: str):
    """Execute SQL file."""
    with open(sql_file, "r", encoding="utf-8") as f:
        raw = f.read()

    statements = [s.strip() for s in raw.split(";") if s.strip()]
    for stmt in statements:
        if stmt.upper().startswith("USE "):
            continue
        cursor.execute(stmt)


def seed_users(cursor, conn):
    """Insert default users safely."""
    users = [
        {
            "email":      "admin@dmmmsu.edu.ph",
            "password":   generate_password_hash("admin123"),
            "first_name": "System",
            "last_name":  "Administrator",
            "role":       "admin",
            "phone":      None,
            "is_active":  1,
        },
        {
            "email":      "staff@dmmmsu.edu.ph",
            "password":   generate_password_hash("staff123"),
            "first_name": "Salvador P.",
            "last_name":  "Llavorre",
            "role":       "staff",
            "phone":      "09171534850",
            "is_active":  1,
        },
    ]

    inserted = 0

    for u in users:
        # ✅ FIX: use user_id instead of id
        cursor.execute(
            "SELECT user_id FROM users WHERE email = %s LIMIT 1",
            (u["email"],)
        )

        if cursor.fetchone():
            print(f"   ↳ User already exists, skipping: {u['email']}")
            continue

        # ✅ FIX: remove user_id (AUTO_INCREMENT handles it)
        cursor.execute(
            """INSERT INTO users
               (email, password_hash, first_name, last_name, role, phone, is_active)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                u["email"],
                u["password"],
                u["first_name"],
                u["last_name"],
                u["role"],
                u["phone"],
                u["is_active"],
            ),
        )

        inserted += 1
        print(f"   ✅ Created user: {u['email']} (role={u['role']})")

    conn.commit()
    return inserted


def main():
    print("=" * 60)
    print("  DMMMSU-SLUC Incident System — MySQL Setup")
    print("=" * 60)
    print(f"  Host    : {DB_HOST}:{DB_PORT}")
    print(f"  User    : {DB_USER}")
    print(f"  Database: {DB_NAME}")
    print("-" * 60)

    # Step 1 – Create database
    print("\n[1/3] Creating database (if not exists)…")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        conn.commit()
        cursor.close()
        conn.close()
        print(f"   ✅ Database `{DB_NAME}` ready.")
    except mysql.connector.Error as err:
        sys.exit(f"❌  Cannot connect to MySQL: {err}")

    # Step 2 – Run schema
    print("\n[2/3] Running schema.sql…")
    if not os.path.exists(SCHEMA_FILE):
        sys.exit(f"❌  schema.sql not found at: {SCHEMA_FILE}")

    conn = get_connection(database=DB_NAME)
    cursor = conn.cursor()

    try:
        run_schema(cursor, SCHEMA_FILE)
        conn.commit()
        print("   ✅ Tables created (or already up-to-date).")
    except mysql.connector.Error as err:
        sys.exit(f"❌  Schema error: {err}")
    finally:
        cursor.close()

    # Step 3 – Seed users
    print("\n[3/3] Seeding default users…")
    cursor = conn.cursor()

    try:
        seed_users(cursor, conn)
    except mysql.connector.Error as err:
        sys.exit(f"❌  Seed error: {err}")
    finally:
        cursor.close()
        conn.close()

    print("\n" + "=" * 60)
    print("  ✅ Setup complete!")
    print()
    print("  Default credentials")
    print("    Admin : admin@dmmmsu.edu.ph  /  admin123")
    print("    Staff : staff@dmmmsu.edu.ph  /  staff123")
    print()
    print("  ⚠️ Change these passwords before deploying!")
    print("=" * 60)


if __name__ == "__main__":
    main()