# Instalasi Hermes Agent

## 1. Instalasi Windows

Hermes Agent paling aman dijalankan melalui WSL2 jika installer native Windows tidak tersedia pada versi yang digunakan.

### Opsi A — WSL2

Buka PowerShell sebagai Administrator:

```powershell
wsl --install
```

Restart komputer, buka Ubuntu, lalu jalankan:

```bash
sudo apt update
sudo apt install -y curl git python3 python3-pip
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

Tutup dan buka kembali terminal, lalu periksa:

```bash
hermes --help
```

### Opsi B — installer resmi

Gunakan instruksi terbaru pada [dokumentasi instalasi Hermes](https://hermes-agent.nousresearch.com/docs/getting-started/installation). Jangan mengunduh installer dari sumber tidak resmi.

## 2. Setup awal

```bash
hermes setup
```

Ikuti wizard untuk memilih provider dan model. Untuk pemeriksaan instalasi:

```bash
hermes doctor
hermes --help
```

## 3. Catatan Windows

Jalankan seluruh perintah Hermes di terminal WSL2 jika perintah `hermes` tidak dikenali di Windows. Simpan project di filesystem WSL, atau akses repository Windows melalui `/mnt/c/Users/<nama>/Documents/...`.
