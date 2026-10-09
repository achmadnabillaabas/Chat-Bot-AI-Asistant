# Hermes Agent (opsional)

Versi utama chatbot ini adalah `bot.py`, sehingga dapat dijalankan tanpa Hermes Agent. Hermes dipakai sebagai alternatif agent/gateway jika ingin tool calling, session, memory, dan channel tambahan.

## Instalasi

Ikuti dokumentasi resmi Hermes: <https://hermes-agent.nousresearch.com/docs/getting-started/installation>

Setelah terpasang:

```bash
hermes --help
hermes setup
hermes doctor
```

Gunakan panduan Hermes untuk menghubungkan provider OpenRouter dan channel Telegram. `bot.py` dan Hermes adalah dua jalur yang berbeda; pilih salah satu agar token Telegram tidak dipakai dua proses.
