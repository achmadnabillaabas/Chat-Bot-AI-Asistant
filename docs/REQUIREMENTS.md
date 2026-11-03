# Requirement

## Software

- Windows 10/11, macOS, Linux, atau WSL2.
- Node.js dan npm untuk memasang 9Router.
- Docker Desktop dengan WSL2/Linux containers (Windows), atau Docker Engine dan Docker Compose v2 (Linux), jika fitur RAGFlow digunakan.
- RAGFlow rekomendasi awal: 4 CPU core, 16 GB RAM, dan 50 GB disk; kebutuhan nyata tergantung beban parsing, jumlah dokumen, dan model.
- Python 3.11 atau lebih baru.
- `pip`, `git`, dan `curl`.
- Akun/provider AI yang dikonfigurasi di 9Router.

## Akun dan kredensial

- Provider AI atau subscription yang didukung 9Router.
- Akun Telegram.
- Token bot Telegram dari BotFather.
- Jika RAG diaktifkan: RAGFlow API key, chat assistant ID, serta model chat/embedding yang dikonfigurasi di RAGFlow.

## Pemeriksaan

```bash
node --version
npm --version
python --version
pip --version
git --version
curl --version
```

9Router berjalan lokal pada endpoint default `http://localhost:20128/v1`. API key dan token dimasukkan melalui konfigurasi lokal, bukan disimpan di repository.
