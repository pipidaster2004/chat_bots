import json
import os
import sqlite3
from dotenv import load_dotenv

from bot.domain.storage import Storage

load_dotenv()


class StorageSqlite(Storage):
    def recreate_database() -> None:
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            with connection:
                connection.execute("DROP TABLE IF EXISTS telegram_updates")
                connection.execute("DROP TABLE IF EXISTS messages")
                connection.execute("DROP TABLE IF EXISTS user_states")
                connection.execute("DROP TABLE IF EXISTS users")

                connection.execute(
                    """
                        CREATE TABLE IF NOT EXISTS telegram_updates
                            (
                                id INTEGER PRIMARY KEY,
                                payload TEXT NOT NULL
                            )
                    """
                )
                connection.execute(
                    """
                        CREATE TABLE IF NOT EXISTS messages
                            (
                                id INTEGER PRIMARY KEY,
                                telegram_id INTEGER NOT NULL,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                message TEXT DEFAULT NULL
                            )
                    """
                )
                connection.execute(
                    """
                        CREATE TABLE IF NOT EXISTS users
                            (
                                id INTEGER PRIMARY KEY,
                                telegram_id INTEGER UNIQUE NOT NULL,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
                    """
                )
                connection.execute(
                    """
                        CREATE TABLE IF NOT EXISTS user_states
                            (
                                id INTEGER PRIMARY KEY,
                                telegram_id INTEGER UNIQUE NOT NULL,
                                state_data TEXT NOT NULL,
                                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
                            )
                    """
                )

    def persist_update(self, update: dict) -> None:
        json_data = json.dumps(update, ensure_ascii=False, indent=2)
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            connection.execute(
                "INSERT INTO telegram_updates (payload) VALUES (?)", (json_data,)
            )

    def ensure_user_exists(self, telegram_id: int) -> None:
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            cursor = connection.execute(
                "SELECT 1 FROM users WHERE telegram_id = ?", (telegram_id,)
            )
            if cursor.fetchone() is None:
                connection.execute(
                    "INSERT INTO users (telegram_id) VALUES (?)", (telegram_id,)
                )

    def get_user(self, telegram_id: int) -> dict | None:
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            with connection:
                cursor = connection.execute(
                    "SELECT id, telegram_id, created_at FROM users WHERE telegram_id = ?",
                    (telegram_id,),
                )
                result = cursor.fetchone()
                if result:
                    return {
                        "id": result[0],
                        "telegram_id": result[1],
                        "created_at": result[2],
                    }
                return None

    def add_message(self, telegram_id: int, message_text: str) -> None:
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            connection.execute(
                """
                    INSERT INTO messages (telegram_id, message)
                    VALUES (?, ?)
                """,
                (telegram_id, message_text),
            )

    def get_last_messages(self, telegram_id: int, limit: int = 5):
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            cursor = connection.execute(
                """
                    SELECT message, created_at
                    FROM messages
                    WHERE telegram_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """,
                (telegram_id, limit),
            )
            return cursor.fetchall()

    def set_user_state(self, telegram_id: int, state: dict) -> None:
        state_json = json.dumps(state, ensure_ascii=False)

        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            self.ensure_user_exists(telegram_id)
            cursor = connection.execute(
                "SELECT 1 FROM user_states WHERE telegram_id = ?", (telegram_id,)
            )

            if cursor.fetchone() is None:
                connection.execute(
                    """
                    INSERT INTO user_states (telegram_id, state_data)
                    VALUES (?, ?)
                    """,
                    (telegram_id, state_json),
                )
            else:
                connection.execute(
                    """
                    UPDATE user_states 
                    SET state_data = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE telegram_id = ?
                    """,
                    (state_json, telegram_id),
                )

    def get_user_state(self, telegram_id: int) -> dict:
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            cursor = connection.execute(
                "SELECT state_data FROM user_states WHERE telegram_id = ?",
                (telegram_id,),
            )
            result = cursor.fetchone()

            if result and result[0]:
                try:
                    return json.loads(result[0])
                except json.JSONDecodeError:
                    print(f"Error decoding JSON state for user {telegram_id}")
                    return {}
            return {}

    def clear_user_state(self, telegram_id: int) -> None:
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            connection.execute(
                "DELETE FROM user_states WHERE telegram_id = ?", (telegram_id,)
            )

    def get_all_users_with_state(self):
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            cursor = connection.execute(
                """
                SELECT u.telegram_id, us.state_data, us.updated_at
                FROM users u
                LEFT JOIN user_states us ON u.telegram_id = us.telegram_id
                """
            )
            return cursor.fetchall()
