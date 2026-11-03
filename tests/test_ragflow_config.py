import os
import unittest
from unittest.mock import patch

import bot


class RagflowConfigurationTests(unittest.TestCase):
    def test_uses_ragflow_only_when_base_key_and_chat_id_are_configured(self):
        with patch.dict(os.environ, {
            "RAGFLOW_BASE_URL": "http://ragflow.local",
            "RAGFLOW_API_KEY": "secret",
            "RAGFLOW_CHAT_ID": "chat-id",
        }, clear=False):
            self.assertTrue(bot.ragflow_enabled())

    def test_keeps_router_fallback_when_ragflow_is_unconfigured(self):
        with patch.dict(os.environ, {
            "RAGFLOW_BASE_URL": "",
            "RAGFLOW_API_KEY": "",
            "RAGFLOW_CHAT_ID": "",
        }, clear=False):
            self.assertFalse(bot.ragflow_enabled())

    def test_ragflow_request_uses_chat_completion_api_and_non_streaming(self):
        with patch.object(bot, "request_json", return_value={
            "choices": [{"message": {"content": "grounded reply"}}]
        }) as request:
            result = bot.ask_ragflow("question")

        self.assertEqual(result, "grounded reply")
        args, kwargs = request.call_args
        self.assertEqual(args[0], "http://localhost/api/v1/openai/chat-1/chat/completions")
        self.assertEqual(args[1]["messages"][0]["content"], "question")
        self.assertFalse(args[1]["stream"])
        self.assertEqual(args[2]["Authorization"], "Bearer test-key")


if __name__ == "__main__":
    unittest.main()
