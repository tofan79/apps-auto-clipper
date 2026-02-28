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
- Roadmap issues Stage 2 sampai Stage 7 otomatis dibuat jika belum ada

## 4. Branch Protection untuk `main`
Path: `Settings -> Branches -> Add branch protection rule`

Rekomendasi minimum:
- Require pull request before merge
- Require 1 approval
- Require status checks to pass
- Block force pushes

## 5. Aktifkan Discussions Categories
Path: `Discussions -> Categories`

Buat kategori:
- Announcements
- Q&A
- Ideas
- Show and Tell

## 6. Milestones dan Project Board
- Buat milestone per stage roadmap (Stage 2 ... Stage 7)
- Buat project board sederhana:
  - Backlog
  - Ready
  - In Progress
  - Review
  - Done

## 7. Security Hygiene
- Rotate credential yang pernah terpapar
- Pastikan tidak ada secret real di history commit berikutnya
