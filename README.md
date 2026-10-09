# SAPI — Chat Bot AI Assistant

Chatbot kelompok berbasis **Hermes Agent** yang dapat digunakan melalui Telegram. Repository ini berisi dokumentasi proyek, pembagian tugas, rencana pengerjaan, serta panduan instalasi dan penggunaan.

> Status: tahap perencanaan dan dokumentasi. Detail provider/model dapat disesuaikan pada konfigurasi lokal.

## Tujuan Proyek

1. Menyediakan chatbot AI yang dapat menjawab percakapan pengguna.
2. Menghubungkan chatbot dengan Hermes Agent.
3. Menyediakan akses chatbot melalui Telegram.
4. Mendokumentasikan instalasi agar proyek dapat dicoba oleh pengguna lain.
5. Mengatur pekerjaan kelompok melalui to-do list dan milestone.

## Fitur Utama

- Percakapan dengan model AI melalui Hermes Agent.
- Akses chatbot dari Telegram.
- Konfigurasi provider/model secara lokal.
- Panduan instalasi, konfigurasi, penggunaan, dan troubleshooting.
- Dokumentasi pembagian pekerjaan dua anggota.

## Arsitektur Singkat

```text
Pengguna Telegram
        |
        v
Telegram Bot API
        |
        v
Hermes Agent / Gateway
        |
        v
Provider model AI atau model lokal
```

## Panduan Cepat

- [Requirement](docs/REQUIREMENTS.md)
- [Instalasi](docs/INSTALLATION.md)
- [Konfigurasi provider/router](docs/PROVIDER_SETUP.md)
- [Koneksi Hermes](docs/HERMES_SETUP.md)
- [Integrasi Telegram](docs/TELEGRAM_SETUP.md)
- [Rencana proyek](PROJECT_PLAN.md)
- [To-do list](TODO.md)
- [Kontribusi](CONTRIBUTING.md)

## Keamanan

Jangan commit API key, token Telegram, password, atau file `.env`. Gunakan `.env.example` sebagai template dan simpan nilai rahasia hanya di konfigurasi lokal.

## Anggota Kelompok

- **Achmad Nabilla Abas** — pemilik repository, pengembangan dan dokumentasi.
- **Collaborator** — isi nama dan tanggung jawab anggota kedua pada bagian ini.

## Lisensi

Tambahkan lisensi proyek sesuai kesepakatan kelompok atau instruksi dosen.
