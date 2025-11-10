import unittest
import os
import sqlite3
import tempfile
from unittest.mock import patch
from bot.infrastructure.storage_sqlite import StorageSqlite


class TestStorageSqlite(unittest.TestCase):

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()

        self.env_patcher = patch.dict(
            os.environ, {"SQLITE_DATABASE_PATH": self.temp_db.name}
        )
        self.env_patcher.start()

        self.storage = StorageSqlite()

        StorageSqlite.recreate_database()

    def tearDown(self):
        """Очистка после каждого теста"""
        self.env_patcher.stop()
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

    def test_persist_update(self):
        """Тест сохранения update в базу"""

        test_update = {
            "update_id": 123,
            "message": {"message_id": 456, "text": "Test message"},
        }

        self.storage.persist_update(test_update)

        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.execute("SELECT payload FROM telegram_updates")
            result = cursor.fetchone()

            self.assertIsNotNone(result)
            saved_data = result[0]
            self.assertIn('"update_id": 123', saved_data)
            self.assertIn('"text": "Test message"', saved_data)

    def test_ensure_user_exists_new_user(self):
        """Тест создания нового пользователя"""

        self.storage.ensure_user_exists(12345)

        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.execute(
                "SELECT telegram_id FROM users WHERE telegram_id = ?", (12345,)
            )
            result = cursor.fetchone()

            self.assertIsNotNone(result)
            self.assertEqual(result[0], 12345)

    def test_ensure_user_exists_existing_user(self):
        """Тест что пользователь не создается повторно"""

        self.storage.ensure_user_exists(12345)
        self.storage.ensure_user_exists(12345)

        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM users WHERE telegram_id = ?", (12345,)
            )
            count = cursor.fetchone()[0]

            self.assertEqual(count, 1)

    def test_get_user_existing(self):
        """Тест получения существующего пользователя"""

        self.storage.ensure_user_exists(12345)

        user = self.storage.get_user(12345)

        self.assertIsNotNone(user)
        self.assertEqual(user["telegram_id"], 12345)
        self.assertIn("id", user)
        self.assertIn("created_at", user)

    def test_get_user_nonexistent(self):
        """Тест получения несуществующего пользователя"""

        user = self.storage.get_user(99999)

        self.assertIsNone(user)

    def test_add_message(self):
        """Тест добавления сообщения"""

        self.storage.ensure_user_exists(12345)

        self.storage.add_message(12345, "Test message text")

        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.execute(
                "SELECT telegram_id, message FROM messages WHERE telegram_id = ?",
                (12345,),
            )
            result = cursor.fetchone()

            self.assertIsNotNone(result)
            self.assertEqual(result[0], 12345)
            self.assertEqual(result[1], "Test message text")

    def test_set_user_state_new(self):
        """Тест установки состояния для нового пользователя"""

        self.storage.ensure_user_exists(12345)
        test_state = {
            "selected_model": "deepseek-ai/DeepSeek-R1",
            "last_activity": "2024-01-01",
        }

        self.storage.set_user_state(12345, test_state)

        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.execute(
                "SELECT state_data FROM user_states WHERE telegram_id = ?", (12345,)
            )
            result = cursor.fetchone()

            self.assertIsNotNone(result)
            saved_state = result[0]
            self.assertIn('"selected_model": "deepseek-ai/DeepSeek-R1"', saved_state)
            self.assertIn('"last_activity": "2024-01-01"', saved_state)

    def test_set_user_state_update_existing(self):
        """Тест обновления существующего состояния"""
        self.storage.ensure_user_exists(12345)
        initial_state = {"selected_model": "old_model"}
        updated_state = {"selected_model": "new_model", "updated": True}

        self.storage.set_user_state(12345, initial_state)

        self.storage.set_user_state(12345, updated_state)

        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.execute(
                "SELECT state_data FROM user_states WHERE telegram_id = ?", (12345,)
            )
            result = cursor.fetchone()

            self.assertIsNotNone(result)
            saved_state = result[0]
            self.assertIn('"selected_model": "new_model"', saved_state)
            self.assertIn('"updated": true', saved_state)
            self.assertNotIn("old_model", saved_state)

    def test_get_user_state_existing(self):
        """Тест получения существующего состояния"""
        self.storage.ensure_user_exists(12345)
        test_state = {
            "selected_model": "deepseek-ai/DeepSeek-R1",
            "settings": {"notifications": True},
        }
        self.storage.set_user_state(12345, test_state)

        retrieved_state = self.storage.get_user_state(12345)

        self.assertEqual(retrieved_state, test_state)

    def test_get_user_state_nonexistent(self):
        """Тест получения состояния для несуществующего пользователя"""
        state = self.storage.get_user_state(99999)

        self.assertEqual(state, {})

    def test_get_user_state_no_state(self):
        """Тест получения состояния когда состояние не установлено"""
        self.storage.ensure_user_exists(12345)

        state = self.storage.get_user_state(12345)

        self.assertEqual(state, {})

    def test_clear_user_state(self):
        """Тест очистки состояния пользователя"""
        self.storage.ensure_user_exists(12345)
        test_state = {"selected_model": "test_model"}
        self.storage.set_user_state(12345, test_state)

        self.storage.clear_user_state(12345)

        state = self.storage.get_user_state(12345)
        self.assertEqual(state, {})

    def test_get_all_users_with_state(self):
        """Тест получения всех пользователей с состояниями"""
        users_data = [
            (11111, {"model": "model1"}),
            (22222, {"model": "model2"}),
            (33333, None),
        ]

        for user_id, state in users_data:
            self.storage.ensure_user_exists(user_id)
            if state:
                self.storage.set_user_state(user_id, state)

        users_with_states = self.storage.get_all_users_with_state()

        self.assertEqual(len(users_with_states), 3)

        for user_data in users_with_states:
            self.assertEqual(len(user_data), 3)
            telegram_id, state_data, updated_at = user_data
            self.assertIn(telegram_id, [11111, 22222, 33333])

            if telegram_id == 33333:
                self.assertIsNone(state_data)
            else:
                self.assertIsNotNone(state_data)
