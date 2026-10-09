# Hermes Agent (opsional)

Versi utama chatbot ini adalah `bot.py`, sehingga dapat dijalankan langsung melalui 9Router tanpa Hermes Agent. Hermes dipakai sebagai alternatif agent/gateway jika ingin tool calling, session, memory, dan channel tambahan.

## Instalasi

Ikuti dokumentasi resmi Hermes: <https://hermes-agent.nousresearch.com/docs/getting-started/installation>

Setelah terpasang:

```bash
hermes --help
hermes setup
hermes doctor
```

Untuk provider, gunakan endpoint OpenAI-compatible 9Router:

```text
http://localhost:20128/v1
```

Gunakan panduan konfigurasi provider Hermes versi Anda untuk mengisi base URL, model, dan credential. Dokumentasi resmi 9Router: <https://9router.com/>.

`bot.py` dan Hermes adalah dua jalur yang berbeda; pilih salah satu agar token Telegram tidak dipakai dua proses.
