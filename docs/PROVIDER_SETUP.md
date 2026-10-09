# Konfigurasi OpenRouter

## Apa itu OpenRouter?

OpenRouter adalah router API yang menyediakan akses ke banyak model melalui endpoint yang kompatibel dengan OpenAI. Satu API key dapat digunakan untuk memilih model yang berbeda, sesuai saldo, limit, dan ketersediaan.

## Membuat API key

1. Buka <https://openrouter.ai/> dan buat akun.
2. Buka menu **Keys**.
3. Pilih **Create Key**.
4. Salin key satu kali dan simpan di password manager.
5. Tambahkan kredit atau pilih model gratis jika tersedia.

Jangan masukkan key ke Git, README, screenshot, atau chat publik.

## Menghubungkan ke Hermes

Jalankan:

```bash
hermes setup
```

Pilih **OpenRouter** bila tersedia, masukkan API key ketika diminta, lalu pilih model. Jika wizard versi Anda berbeda, lihat:

```bash
hermes model --help
hermes config --help
```

Model ditentukan oleh Hermes/provider. Contoh model OpenRouter harus mengikuti ID yang tampil di dashboard OpenRouter, bukan nama pendek buatan sendiri.

## Pengujian provider

```bash
hermes doctor
hermes chat -q "Tulis satu kalimat untuk menguji koneksi OpenRouter."
```

Jika gagal, periksa saldo, nama model, API key, dan endpoint provider. API key yang pernah tampil di log harus segera dicabut.
