# Troubleshooting

## `9router: command not found`

Pastikan Node.js/npm terpasang dan instalasi global berhasil:

```bash
npm install -g 9router
9router
```

## Endpoint 9Router tidak bisa diakses

Pastikan proses `9router` masih berjalan, lalu uji:

```bash
curl http://localhost:20128/v1/models
```

Periksa juga `ROUTER9_BASE_URL` dan port pada dashboard.

## Error 401/403

Periksa `ROUTER9_API_KEY`. Jika instalasi lokal tidak membutuhkan key, gunakan nilai yang disediakan konfigurasi 9Router. Jangan mengirim key dalam issue publik.

## Model tidak ditemukan

Gunakan `ROUTER9_MODEL=auto` atau model ID yang tampil pada dashboard 9Router.

## Telegram tidak membalas

Periksa token BotFather, pastikan `bot.py` berjalan, pastikan 9Router berjalan, dan pastikan tidak ada proses bot lain memakai token yang sama.

## Masih gagal

Kumpulkan versi (`node --version`, `python --version`), perintah, endpoint tanpa credential, dan pesan error tanpa secret.
