# Repository Admin Setup

Langkah ini dilakukan di GitHub UI oleh owner repo.

## 1. Aktifkan Features
Path: `Repository -> Settings -> General -> Features`

Pastikan aktif:
- Issues
- Discussions
- Projects

## 2. Workflow Permissions
Path: `Repository -> Settings -> Actions -> General`

Pastikan:
- Actions diizinkan untuk run
- `Workflow permissions` minimal `Read and write permissions` (agar workflow bisa membuat labels/issues)

## 3. Jalankan Bootstrap Community Workflow
Path: `Repository -> Actions -> Bootstrap Community`

Pilih:
- `Run workflow`

Hasil yang diharapkan:
- Label standar otomatis terbuat/ter-update
- 10 issue awal Stage 2 otomatis dibuat jika belum ada
