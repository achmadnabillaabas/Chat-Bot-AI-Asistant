# SAPI — Chatbot AI Telegram berbasis Hermes Agent

SAPI adalah chatbot AI yang dapat digunakan melalui Telegram. Repository ini bukan hanya dokumentasi: `bot.py` adalah implementasi chatbot yang dapat langsung dijalankan. Proyek ini juga mendokumentasikan jalur alternatif menggunakan **Hermes Agent** dan menghubungkan **OpenRouter** sebagai provider model AI.

> OpenRouter adalah nama layanan yang digunakan. Jika yang dimaksud “9router” adalah layanan lain, gunakan panduan provider tersebut; alur integrasinya tetap sama.

## Tujuan

- Membuat chatbot AI yang bisa dicoba pengguna lain tanpa menebak langkah instalasi.
- Menjelaskan requirement, instalasi OpenRouter, instalasi Hermes Agent, konfigurasi model, dan koneksi Telegram.
- Menyediakan troubleshooting untuk masalah umum.

## Alur sistem

```text
Pengguna Telegram
      ↓
Telegram Bot API
      ↓
Hermes Agent Gateway
      ↓
OpenRouter API
      ↓
Model AI yang dipilih
```

## Requirement

- Windows 10/11, macOS, Linux, atau WSL2.
- Python 3.11+ dan `pip`.
- Git.
- Koneksi internet.
- Akun [OpenRouter](https://openrouter.ai/) dan API key.
- Akun Telegram dan bot token dari [@BotFather](https://t.me/BotFather).
- Hermes Agent versi terbaru.

Periksa instalasi:

```bash
python --version
pip --version
git --version
```

## Instalasi cepat

```bash
git clone https://github.com/achmadnabillaabas/Chat-Bot-AI-Asistant.git
cd Chat-Bot-AI-Asistant
```

Panduan lengkap:

1. [Requirement dan persiapan](docs/REQUIREMENTS.md)
2. [Instalasi Hermes Agent](docs/INSTALLATION.md)
3. [Konfigurasi OpenRouter](docs/PROVIDER_SETUP.md)
4. [Konfigurasi Hermes](docs/HERMES_SETUP.md)
5. [Membuat dan menghubungkan Telegram Bot](docs/TELEGRAM_SETUP.md)
6. [Menjalankan dan menguji chatbot](docs/USAGE.md)
7. [Troubleshooting](docs/TROUBLESHOOTING.md)

## Ringkasan konfigurasi

1. Buat API key di OpenRouter.
2. Buat bot melalui BotFather dan simpan tokennya.
3. Instal Hermes Agent.
4. Jalankan `hermes setup`, pilih provider OpenRouter, model, dan masukkan API key melalui prompt.
5. Aktifkan Telegram pada konfigurasi Hermes sesuai dokumentasi versi yang terpasang.
6. Jalankan gateway Hermes.
7. Buka bot di Telegram dan kirim `/start`.

Jangan menaruh API key atau token Telegram di repository. Gunakan `.env.example` hanya sebagai referensi; file `.env` tetap lokal.

## Struktur dokumentasi

```text
docs/
├── REQUIREMENTS.md
├── INSTALLATION.md
├── PROVIDER_SETUP.md
├── HERMES_SETUP.md
├── TELEGRAM_SETUP.md
├── USAGE.md
└── TROUBLESHOOTING.md
```

## Status proyek

Dokumentasi dan integrasi dasar sedang dikembangkan. Nama perintah Hermes dapat berubah antarversi; selalu periksa `hermes --help` dan dokumentasi resmi.

## Pengembangan

- [Rencana proyek](PROJECT_PLAN.md)
- [To-do list](TODO.md)
- [Kontribusi](CONTRIBUTING.md)

## Keamanan

Jangan commit `API key`, token Telegram, password, atau `.env`. Jika token bocor, cabut melalui OpenRouter/BotFather dan buat token baru.

## Lisensi

Lisensi proyek belum ditentukan. Tambahkan lisensi setelah disepakati kelompok.
