# Menjalankan chatbot

## 1. Jalankan 9Router

```bash
npm install -g 9router
9router
```

Pastikan dashboard 9Router dapat dibuka di `http://localhost:20128/dashboard` dan provider sudah dikonfigurasi.

## 2. Jalankan chatbot

Linux/macOS/WSL2:

```bash
export ROUTER9_BASE_URL="http://localhost:20128/v1"
export ROUTER9_API_KEY="your-local-9router-key"
export ROUTER9_MODEL="auto"
export TELEGRAM_BOT_TOKEN="123456:..."
python3 bot.py
```

Windows PowerShell:

```powershell
$env:ROUTER9_BASE_URL="http://localhost:20128/v1"
$env:ROUTER9_API_KEY="your-local-9router-key"
$env:ROUTER9_MODEL="auto"
$env:TELEGRAM_BOT_TOKEN="123456:..."
python bot.py
```

Buka bot di Telegram, kirim `/start`, lalu kirim pesan biasa. Hentikan dengan `Ctrl+C`.

## Catatan

- Jangan menjalankan dua proses bot memakai token yang sama.
- 9Router harus tetap berjalan selama chatbot digunakan.
- Model `auto` dipilih oleh 9Router; gunakan ID model dari dashboard jika diperlukan.
- Respons Telegram dibatasi 4096 karakter.
- `requirements.txt` sengaja tidak berisi package: proyek memakai standard library.
