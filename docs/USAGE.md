# Menjalankan chatbot

Implementasi chatbot ada di `bot.py`. Program ini menggunakan long polling Telegram dan standard library Python; tidak perlu framework tambahan.

## Linux/macOS/WSL2

```bash
export OPENROUTER_API_KEY="or-..."
export TELEGRAM_BOT_TOKEN="123456:..."
export OPENROUTER_MODEL="openai/gpt-4o-mini"
python3 bot.py
```

## Windows PowerShell

```powershell
$env:OPENROUTER_API_KEY="or-..."
$env:TELEGRAM_BOT_TOKEN="123456:..."
$env:OPENROUTER_MODEL="openai/gpt-4o-mini"
python bot.py
```

Buka bot di Telegram, kirim `/start`, lalu kirim pesan biasa. Hentikan dengan `Ctrl+C`.

## Catatan

- Jangan menjalankan dua proses bot memakai token yang sama.
- Token dan API key hanya berlaku pada terminal saat environment variable diset.
- Respons Telegram dibatasi 4096 karakter.
- `requirements.txt` sengaja tidak berisi package: proyek memakai standard library.
