# Integrasi Telegram

## 1. Membuat bot

1. Buka Telegram dan cari `@BotFather`.
2. Kirim `/newbot`.
3. Isi nama tampilan bot.
4. Isi username yang berakhiran `bot`.
5. Salin token yang diberikan.
6. Simpan token di password manager; jangan commit ke Git.

Jika token bocor, gunakan `/revoke` di BotFather lalu buat token baru.

## 2. Menghubungkan ke Hermes

Buka konfigurasi messaging Hermes atau dashboard Hermes, pilih Telegram, lalu masukkan token melalui mekanisme secret yang tersedia. Ikuti dokumentasi resmi karena nama opsi dapat berubah antarversi:

<https://hermes-agent.nousresearch.com/docs/user-guide/messaging>

Jangan menebak nama environment variable atau mengedit YAML secara manual jika wizard Hermes menyediakan konfigurasi otomatis.

## 3. Menguji bot

1. Jalankan gateway Hermes.
2. Buka username bot di Telegram.
3. Kirim `/start`.
4. Kirim `Halo`.
5. Pastikan balasan berasal dari model yang dipilih di Hermes.

## Keamanan

Batasi akses bot jika diperlukan, jangan mengirim data sensitif, dan cabut token bila muncul di log, screenshot, commit, atau pesan publik.
