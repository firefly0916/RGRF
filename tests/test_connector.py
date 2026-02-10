import os
import unittest
from unittest.mock import patch

from llm.connector import LLMConnector


class TestConnector(unittest.TestCase):
    @patch("llm.connector.openai.OpenAI")
    def test_normalizes_base_url(self, mock_client):
        LLMConnector(
            api_key="test",
            base_url="https://openrouter.ai/api/v1/chat/completions",
        )
        _, kwargs = mock_client.call_args
        self.assertEqual(kwargs.get("base_url"), "https://openrouter.ai/api/v1")

    @patch.dict(
        os.environ,
        {"OPENROUTER_HTTP_REFERER": "https://example.com", "OPENROUTER_APP_NAME": "rgrf"},
        clear=True,
    )
    @patch("llm.connector.openai.OpenAI")
    def test_sets_openrouter_headers(self, mock_client):
        LLMConnector(api_key="test", base_url="https://openrouter.ai/api/v1")
        _, kwargs = mock_client.call_args
        headers = kwargs.get("default_headers")
        self.assertEqual(headers, {"HTTP-Referer": "https://example.com", "X-Title": "rgrf"})
