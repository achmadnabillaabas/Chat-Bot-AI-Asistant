# Integrasi RAGFlow untuk SAPI Telegram

Dokumen ini hanya untuk chatbot Telegram pada `bot.py`. Ia tidak mengubah atau menjalankan aplikasi dashboard pada `dashboard-ai/`.

## Ringkasan integrasi

RAGFlow dijalankan sebagai layanan terpisah melalui Docker Compose upstream. Alur pesan: Telegram → `bot.py` → (jika diaktifkan) RAGFlow chat assistant yang terhubung ke Knowledge Base/dataset → jawaban ke Telegram. Tanpa `RAGFLOW_CHAT_ID`, bot tetap menggunakan jalur 9Router yang sudah ada.

Integrasi memanfaatkan API resmi RAGFlow, bukan menyalin kode internalnya. API key, chat ID, dokumen, dan data RAGFlow tetap berada pada instalasi lokal.

## Requirement

- Docker Desktop untuk Windows dengan WSL2/Linux containers, atau Docker Engine + Docker Compose v2 pada Linux.
- RAGFlow upstream menyebut konfigurasi awal rekomendasi 4 CPU core, 16 GB RAM, dan 50 GB ruang disk; model lokal dan pemrosesan dokumen dapat memerlukan resource tambahan.
- Linux host: `vm.max_map_count=262144` sesuai panduan deploy RAGFlow. Periksa panduan resmi untuk prasyarat platform sebelum deploy.
- Python 3.11+ (bot memakai standard library; package baru tidak diperlukan).
- Node.js/npm dan 9Router untuk fallback/chat standar.
- Telegram bot token, RAGFlow API key, dan RAGFlow chat assistant ID.
- Model chat dan embedding yang sudah dikonfigurasi di RAGFlow; Knowledge Base/dataset dan dokumen yang telah selesai diproses.
- Koneksi internet saat pertama kali mengambil image RAGFlow.

## Langkah setup

1. Install dan jalankan Docker Desktop, alokasikan sekurang-kurangnya resource yang direkomendasikan RAGFlow, lalu verifikasi:

   ```bash
   docker --version
   docker compose version
   docker info
   ```

2. Clone repository RAGFlow upstream secara terpisah dari repo chatbot, lalu jalankan Compose yang dipelihara upstream:

   ```bash
   git clone https://github.com/infiniflow/ragflow.git
   cd ragflow/docker
   docker compose -f docker-compose.yml up -d
   docker compose -f docker-compose.yml ps
   ```

   Ikuti panduan upstream untuk release/tag yang dipilih, pengaturan host, port, dan langkah khusus platform. Jangan salin source/Compose RAGFlow ke `dashboard-ai/` atau repo bot.

3. Buka antarmuka RAGFlow di `http://localhost` (port dapat berbeda jika konfigurasi upstream diubah). Selesaikan inisialisasi, buat API key, konfigurasi model chat/embedding, buat dataset dan chat assistant yang menggunakannya.

4. Unggah dokumen di UI RAGFlow dan tunggu parsing/indexing selesai. Salin API key dan ID chat assistant dari instalasi tersebut.

5. Atur environment variables secara lokal, jangan masukkan nilainya ke Git:

   ```text
   RAGFLOW_BASE_URL=http://localhost
   RAGFLOW_API_KEY=<API key lokal RAGFlow>
   RAGFLOW_CHAT_ID=<ID chat assistant RAGFlow>
   ```

   `RAGFLOW_BASE_URL` harus menunjuk ke base URL publik API RAGFlow. Jangan menambahkan `/api/v1` kecuali implementasi konfigurasi meminta base path tersebut.

6. Atur variabel bot yang telah dipakai sebelumnya (`TELEGRAM_BOT_TOKEN`, `ROUTER9_API_KEY`, `ROUTER9_BASE_URL`, dan `ROUTER9_MODEL`). Ketika konfigurasi RAGFlow lengkap, bot memilih RAGFlow untuk jawaban; tanpa `RAGFLOW_CHAT_ID`, bot tetap memakai 9Router. Hanya jalankan satu proses polling bot per Telegram token.

7. Jalankan `python bot.py`, kirim `/start`, lalu uji pertanyaan yang jawabannya memang ada di dokumen. Pastikan RAGFlow menampilkan references/sumber untuk respons tersebut dan bot tetap menjawab pertanyaan umum melalui fallback 9Router jika pilihan fallback diimplementasikan.

## API dan keamanan

Untuk RAGFlow 1.0 API, dokumentasi saat ini menggunakan `POST /api/v1/openai/{chat_id}/chat/completions` dengan `Authorization: Bearer <RAGFLOW_API_KEY>`, body OpenAI-compatible (`model`, `messages`, `stream: false`). Alias `/api/v1/chats_openai/{chat_id}/chat/completions` dihapus pada RAGFlow 1.0; jangan menggunakannya pada integrasi baru. Verifikasi endpoint sesuai versi RAGFlow yang dipasang.

Jangan commit API key atau Telegram token. Jangan membuka port RAGFlow ke internet tanpa autentikasi, firewall, dan TLS yang benar. Volume Docker RAGFlow menyimpan dokumen dan metadata; backup sebelum menghapus volume. `docker compose down -v` menghapus data persisten dan tidak diperlukan untuk menghentikan layanan.

## Troubleshooting

- Container/UI/API tidak tersedia: dari folder `ragflow/docker`, cek `docker compose -f docker-compose.yml ps` dan `docker compose -f docker-compose.yml logs --tail=100`.
- HTTP 401/403: verifikasi API key pada instalasi RAGFlow yang sama dengan `RAGFLOW_BASE_URL`.
- HTTP 404: cek URL dasar, chat ID, dan versi endpoint RAGFlow; versi 1.0 menggunakan `/api/v1/openai/...`.
- Jawaban tidak menyertakan basis dokumen: pastikan chat assistant terhubung ke dataset yang berisi dokumen dengan status parsing/indexing selesai.
- Jangan menghapus volume untuk memperbaiki error sebelum backup dan mengetahui dampaknya.

## Referensi

- RAGFlow upstream: <https://github.com/infiniflow/ragflow>
- RAGFlow HTTP API: <https://ragflow.io/docs/dev/http_api_reference>
- RAGFlow Docker deployment: <https://ragflow.io/docs/dev/deploy_local_using_docker>
