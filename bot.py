"""Minimal Telegram chatbot using the OpenRouter-compatible Chat Completions API."""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


ROUTER9_BASE_URL = os.getenv("ROUTER9_BASE_URL", "http://localhost:20128/v1").rstrip("/")
API_URL = f"{ROUTER9_BASE_URL}/chat/completions"
TELEGRAM_URL = "https://api.telegram.org/bot{}/{}"
MODEL = os.getenv("ROUTER9_MODEL", "auto")
SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT", "Kamu adalah SAPI, asisten AI yang membantu dan menjawab dalam bahasa Indonesia."
)


def request_json(url, payload, headers=None, timeout=60):
    data = json.dumps(payload).encode()
    request = urllib.request.Request(url, data=data, headers=headers or {}, method="POST")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read())


def ask_model(user_text):
    key = os.environ.get("ROUTER9_API_KEY", "")
    result = request_json(
        API_URL,
        {"model": MODEL, "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_text}]},
        {"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
    )
    return result["choices"][0]["message"]["content"]


def telegram(token, method, payload=None):
    return request_json(TELEGRAM_URL.format(token, method), payload or {})


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token or not os.environ.get("ROUTER9_API_KEY"):
        print("Set TELEGRAM_BOT_TOKEN and ROUTER9_API_KEY first.", file=sys.stderr)
        return 2
    offset = 0
    print(f"SAPI berjalan dengan model {MODEL}")
    while True:
        try:
            updates = telegram(token, "getUpdates", {"timeout": 30, "offset": offset}).get("result", [])
            for update in updates:
                offset = update["update_id"] + 1
                message = update.get("message", {})
                chat_id = message.get("chat", {}).get("id")
                text = message.get("text", "").strip()
                if not chat_id or not text:
                    continue
                if text == "/start":
                    answer = "Halo. Saya SAPI. Kirim pertanyaan untuk memulai."
                else:
                    try:
                        answer = ask_model(text)
                    except (KeyError, urllib.error.URLError, json.JSONDecodeError) as error:
                        print(f"Model error: {error}", file=sys.stderr)
                        answer = "Maaf, layanan AI sedang bermasalah. Coba lagi nanti."
                telegram(token, "sendMessage", {"chat_id": chat_id, "text": answer[:4096]})
        except (urllib.error.URLError, TimeoutError) as error:
            print(f"Telegram error: {error}", file=sys.stderr)
            time.sleep(5)


if __name__ == "__main__":
    raise SystemExit(main())
