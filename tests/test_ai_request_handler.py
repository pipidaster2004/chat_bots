import unittest
from unittest.mock import Mock
from bot.handlers.request import AIRequestHandler
from bot.handlers.handler import HandlerStatus


class TestAIRequestHandler(unittest.TestCase):

    def setUp(self):
        self.mock_ai_client = Mock()
        self.handler = AIRequestHandler(self.mock_ai_client)
        self.mock_storage = Mock()
        self.mock_messenger = Mock()

    def test_can_handle_with_ai_selected(self):
        update = {"message": {"text": "Hello AI", "from": {"id": 123}}}
        self.mock_storage.get_user_state.return_value = {
            "selected_model": "deepseek-ai/DeepSeek-R1"
        }
        result = self.handler.can_handle(
            update, "Hello AI", self.mock_storage, self.mock_messenger
        )
        self.assertTrue(result)
        self.mock_storage.get_user_state.assert_called_once_with(123)

    def test_can_handle_without_ai_selected(self):
        update = {"message": {"text": "Hello", "from": {"id": 123}}}
        self.mock_storage.get_user_state.return_value = {}
        result = self.handler.can_handle(
            update, "Hello", self.mock_storage, self.mock_messenger
        )
        self.assertFalse(result)

    def test_can_handle_command_message(self):
        update = {"message": {"text": "/start", "from": {"id": 123}}}
        result = self.handler.can_handle(
            update, "/start", self.mock_storage, self.mock_messenger
        )
        self.assertFalse(result)

    def test_handle_calls_ai_client(self):
        update = {
            "message": {
                "text": "Tell me about Python",
                "from": {"id": 123},
                "chat": {"id": 456},
            }
        }
        self.mock_storage.get_user_state.return_value = {
            "selected_model": "deepseek-ai/DeepSeek-R1"
        }
        self.mock_messenger.sendMessage.return_value = {"message_id": 789}
        self.mock_ai_client.make_request.return_value = (
            "Python is a programming language..."
        )
        result = self.handler.handle(
            update, "Tell me about Python", self.mock_storage, self.mock_messenger
        )
        self.assertEqual(result, HandlerStatus.STOP)
        self.mock_ai_client.make_request.assert_called_once_with(
            "deepseek-ai/DeepSeek-R1", "Tell me about Python"
        )
        self.mock_storage.add_message.assert_called_once_with(
            123, "Tell me about Python"
        )
        self.mock_messenger.sendMessage.assert_any_call(
            chat_id=456, text="Processing your request..."
        )
        self.mock_messenger.sendMessage.assert_any_call(
            chat_id=456, text="Python is a programming language..."
        )
        self.mock_messenger.deleteMessage.assert_called_once_with(
            chat_id=456, message_id=789
        )

    def test_handle_ai_error(self):
        update = {
            "message": {
                "text": "Tell me something",
                "from": {"id": 123},
                "chat": {"id": 456},
            }
        }

        self.mock_storage.get_user_state.return_value = {
            "selected_model": "deepseek-ai/DeepSeek-R1"
        }

        self.mock_messenger.sendMessage.return_value = {"message_id": 789}
        self.mock_ai_client.make_request.side_effect = Exception("API Error")
        result = self.handler.handle(
            update, "Tell me something", self.mock_storage, self.mock_messenger
        )
        self.assertEqual(result, HandlerStatus.STOP)
        self.mock_messenger.sendMessage.assert_any_call(
            chat_id=456, text="Error processing your request. Please try again."
        )
