<p align="center">
  <img src="image.png" alt="SAPI Telegram AI Chatbot" width="100%">
</p>

# SAPI — Chatbot AI Telegram berbasis 9Router

SAPI adalah chatbot AI yang dapat digunakan melalui Telegram. Repository ini bukan hanya dokumentasi: `bot.py` adalah implementasi chatbot yang dapat langsung dijalankan. Proyek ini menggunakan **9Router** sebagai gateway AI lokal dan menyediakan Hermes Agent sebagai jalur alternatif.

> 9Router dijalankan sebagai gateway lokal yang kompatibel dengan OpenAI API.

## Tujuan

- Membuat chatbot AI yang bisa dicoba pengguna lain.
- Menjelaskan requirement, instalasi 9Router, konfigurasi model, dan koneksi Telegram.
- Menyediakan troubleshooting untuk masalah umum.

## Alur sistem

```text
Pengguna Telegram
      ↓
Telegram Bot API
      ↓
bot.py
      ↓
9Router lokal (localhost:20128/v1)
      ↓
Provider/model AI yang dipilih di 9Router
```

Hermes Agent bukan dependency wajib untuk `bot.py`. Pilih salah satu jalur agar token Telegram tidak dipakai dua proses.

## Requirement

- Windows 10/11, macOS, Linux, atau WSL2.
- Node.js/npm untuk 9Router.
- Python 3.11+.
- Git dan koneksi internet.
- Provider AI atau subscription yang dikonfigurasi di 9Router.
- Akun Telegram dan bot token dari [@BotFather](https://t.me/BotFather).

## Instalasi cepat

```bash
git clone https://github.com/achmadnabillaabas/Chat-Bot-AI-Asistant.git
cd Chat-Bot-AI-Asistant
npm install -g 9router
9router
```

Buka dashboard 9Router di `http://localhost:20128/dashboard`, konfigurasi provider/model, lalu ikuti:

1. [Requirement](docs/REQUIREMENTS.md)
2. [Instalasi](docs/INSTALLATION.md)
3. [Konfigurasi 9Router](docs/PROVIDER_SETUP.md)
4. [Konfigurasi Hermes opsional](docs/HERMES_SETUP.md)
5. [Telegram Bot](docs/TELEGRAM_SETUP.md)
6. [Menjalankan chatbot](docs/USAGE.md)
7. [Troubleshooting](docs/TROUBLESHOOTING.md)

## Jalankan chatbot

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

## Keamanan

Jangan commit API key, token Telegram, password, atau `.env`. Jika credential bocor, cabut melalui 9Router/provider atau BotFather dan buat credential baru.

## Pengembangan

- [Rencana proyek](PROJECT_PLAN.md)
- [To-do list](TODO.md)

## Lisensi

Lisensi proyek belum ditentukan.
