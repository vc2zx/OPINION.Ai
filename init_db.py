from pathlib import Path

from werkzeug.security import generate_password_hash

from db import DB_PATH, get_db

BASE_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"


def init_database():
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")

    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    with get_db() as conn:
        conn.executescript(schema)

        categories = [
            ("Food Quality",),
            ("Cleanliness",),
            ("Staff Behavior",),
            ("Price",),
        ]

        conn.executemany("INSERT INTO categories (name) VALUES (?)", categories)

        users = [
            ("owner@example.com", generate_password_hash("owner123"), "owner"),
            ("admin@example.com", generate_password_hash("admin123"), "admin"),
        ]

        conn.executemany(
            "INSERT INTO users (email, password_hash, user_type) VALUES (?, ?, ?)",
            users,
        )

        demo_reviews = [
            ("The food was delicious and fresh, and the staff were friendly.", 5),
            ("The restaurant was clean but the price was too high.", 3),
            ("The tables were dirty and service was slow.", 2),
            ("Amazing food with reasonable price.", 5),
            ("The waiter was rude, but the food was good.", 3),
        ]

        conn.executemany(
            "INSERT INTO reviews (text, stars, status) VALUES (?, ?, 'queued')",
            demo_reviews,
        )

        conn.commit()


if __name__ == "__main__":
    init_database()

    print(f"Database initialized at: {DB_PATH}")
    print("Demo users:")
    print("Owner: owner@example.com / owner123")
    print("Admin: admin@example.com / admin123")
    print("Note: Running this file resets the local database.")
    print("Run app.py, then login and analyze queued reviews from the dashboard.")
