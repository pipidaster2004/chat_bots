import unittest
from unittest.mock import Mock
from bot.handlers.message_start import MessageStart
from bot.handlers.handler import HandlerStatus


class TestMessageStart(unittest.TestCase):

    def setUp(self):
        self.handler = MessageStart()
        self.mock_storage = Mock()
        self.mock_messenger = Mock()

    def test_can_handle_start_command(self):
        update = {"message": {"text": "/start"}}
        result = self.handler.can_handle(
            update, "/start", self.mock_storage, self.mock_messenger
        )

        self.assertTrue(result)

    def test_can_handle_other_command(self):
        update = {"message": {"text": "/help"}}
        result = self.handler.can_handle(
            update, "/help", self.mock_storage, self.mock_messenger
        )
        self.assertFalse(result)

    def test_handle_sends_welcome_messages(self):
        update = {
            "message": {"text": "/start", "from": {"id": 123}, "chat": {"id": 456}}
        }

        result = self.handler.handle(
            update, "/start", self.mock_storage, self.mock_messenger
        )
        self.assertEqual(result, HandlerStatus.STOP)
        self.assertEqual(self.mock_messenger.sendMessage.call_count, 2)
        self.mock_storage.add_message.assert_called_once_with(123, "/start")
