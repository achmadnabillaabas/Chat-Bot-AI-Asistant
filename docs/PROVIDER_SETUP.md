# Konfigurasi 9Router

9Router adalah gateway lokal OpenAI-compatible. 9Router meneruskan request ke provider AI yang dikonfigurasi dan menyediakan endpoint default:

```text
http://localhost:20128/v1
```

## Instalasi dan menjalankan 9Router

```bash
npm install -g 9router
9router
```

Dashboard tersedia di `http://localhost:20128/dashboard`. Ikuti dashboard untuk mengatur provider, OAuth/API key, fallback, dan model.

## Pengaturan project

Salin `.env.example`, lalu set environment variable:

```bash
export ROUTER9_BASE_URL="http://localhost:20128/v1"
export ROUTER9_API_KEY="your-local-9router-key"
export ROUTER9_MODEL="auto"
```

9Router dapat memakai konfigurasi lokal tanpa API key. Jika instalasi Anda tidak meminta key, tetap isi `ROUTER9_API_KEY` dengan nilai yang diminta dokumentasi/ dashboard 9Router.

## Pengujian endpoint

```bash
curl http://localhost:20128/v1/models
```

Jika endpoint membutuhkan key:

```bash
curl http://localhost:20128/v1/models \
  -H "Authorization: Bearer $ROUTER9_API_KEY"
```

## Catatan

Model `auto` menyerahkan pemilihan/fallback kepada 9Router. Gunakan model ID yang tampil pada dashboard jika ingin memilih model tertentu. Dokumentasi resmi: <https://9router.com/> dan <https://github.com/decolua/9router>.
