# Troubleshooting

## `hermes: command not found`

Terminal belum memuat PATH atau Hermes dipasang di WSL. Tutup-buka terminal, cek instalasi, dan jalankan dari WSL2 jika menggunakan Windows.

## `hermes setup` gagal

Jalankan `hermes doctor`, periksa koneksi internet, lalu pastikan versi Hermes terbaru. Jangan membagikan API key pada laporan error.

## OpenRouter mengembalikan 401/403

API key salah, dicabut, atau tidak memiliki izin. Buat key baru dan masukkan melalui `hermes setup`.

## OpenRouter mengembalikan 402

Saldo atau limit akun tidak mencukupi. Periksa billing OpenRouter atau pilih model gratis yang tersedia.

## Model tidak ditemukan

Gunakan ID model yang masih tampil di OpenRouter. Model dapat berubah atau tidak tersedia pada provider tertentu.

## Telegram tidak membalas

Periksa token BotFather, pastikan gateway sedang berjalan, pastikan channel Telegram aktif, dan jalankan `hermes doctor`. Cabut token jika pernah bocor.

## Masih gagal

Kumpulkan versi (`hermes --help`), sistem operasi, perintah yang dijalankan, dan pesan error tanpa secret. Lihat issue repository atau dokumentasi resmi Hermes.
