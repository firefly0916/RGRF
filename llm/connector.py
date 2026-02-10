import os
import openai
import time


def _normalize_base_url(base_url):
    if not base_url:
        return None
    url = base_url.rstrip("/")
    for suffix in ("/chat/completions", "/completions"):
        if url.endswith(suffix):
            url = url[: -len(suffix)]
            break
    return url


def _default_headers_from_env():
    headers = {}
    referer = os.getenv("OPENROUTER_HTTP_REFERER") or os.getenv("OPENROUTER_REFERER")
    if referer:
        headers["HTTP-Referer"] = referer
    title = (
        os.getenv("OPENROUTER_APP_NAME")
        or os.getenv("OPENROUTER_X_TITLE")
        or os.getenv("OPENROUTER_TITLE")
    )
    if title:
        headers["X-Title"] = title
    return headers or None

class LLMConnector:
    def __init__(self, api_key, base_url=None):
        # 支持 OpenAI, Kimi, DeepSeek 等兼容接口
        normalized_base_url = _normalize_base_url(base_url)
        default_headers = _default_headers_from_env()
        client_kwargs = {"api_key": api_key}
        if normalized_base_url:
            client_kwargs["base_url"] = normalized_base_url
        if default_headers:
            client_kwargs["default_headers"] = default_headers
        self.client = openai.OpenAI(**client_kwargs)

    def send_request(self, prompt, model, temperature=0.7):
        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    timeout=30
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"API Error ({model}): {e}. Attempt {attempt+1}/3")
                time.sleep(2)
        return "ERROR: API failed after retries."
