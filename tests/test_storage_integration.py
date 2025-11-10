import unittest
import tempfile
import os
from unittest.mock import patch
from bot.infrastructure.storage_sqlite import StorageSqlite
from bot.handlers.history import HistoryHandler
from bot.domain.messenger import Messenger
from bot.handlers.handler import HandlerStatus


class TestStorageIntegration(unittest.TestCase):

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

        self.mock_messenger = unittest.mock.Mock(spec=Messenger)

    def tearDown(self):
        """Очистка после каждого теста"""
        self.env_patcher.stop()
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

    def test_history_handler_integration(self):
        """Тест интеграции HistoryHandler с хранилищем"""

        handler = HistoryHandler()

        test_messages = ["First message", "Second message", "Third message"]

        for msg in test_messages:
            self.storage.add_message(12345, msg)

        update = {
            "message": {
                "text": "/history",
                "from": {"id": 12345},
                "chat": {"id": 67890},
            }
        }

        result = handler.handle(update, "/history", self.storage, self.mock_messenger)

        self.assertEqual(result, HandlerStatus.STOP)

        self.mock_messenger.sendMessage.assert_called_once()

        call_args = self.mock_messenger.sendMessage.call_args
        message_text = call_args[1]["text"]
        self.assertIn("Последние 5 сообщений", message_text)
        self.assertIn("First message", message_text)
        self.assertIn("Second message", message_text)
        self.assertIn("Third message", message_text)

    def test_user_state_persistence(self):
        """Тест сохранения и восстановления состояния пользователя"""

        user_id = 12345
        initial_state = {
            "selected_model": "deepseek-ai/DeepSeek-R1",
            "conversation_count": 5,
        }

        self.storage.set_user_state(user_id, initial_state)

        retrieved_state = self.storage.get_user_state(user_id)
        self.assertEqual(retrieved_state, initial_state)

        updated_state = {
            "selected_model": "google/gemma-2-9b-it",
            "conversation_count": 6,
            "new_field": "test",
        }
        self.storage.set_user_state(user_id, updated_state)

        retrieved_state = self.storage.get_user_state(user_id)
        self.assertEqual(retrieved_state, updated_state)
