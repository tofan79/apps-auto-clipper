# Maintainer Operations

Checklist operasional maintainer untuk menjaga repo tetap sehat.

## 1. Security First
- Rotate credential yang pernah terpapar
- Simpan secret hanya di GitHub Secrets / local `.env`
- Jangan pernah commit secret real

## 2. Branch Protection (`main`)
Path: `Settings -> Branches -> Add rule`

Aktifkan:
- Require a pull request before merging
- Require approvals: minimal 1
- Dismiss stale approvals saat push baru
- Require status checks to pass before merging
- Include administrators (opsional tapi direkomendasikan)
- Block force pushes

## 3. PR Governance
- Wajib pakai PR template
- Gunakan label `triage` untuk issue baru
- Set milestone per tahap roadmap
- Gunakan project board untuk status delivery

## 4. Discussions Setup
- Kategori minimal:
  - Announcements
  - Q&A
  - Ideas
  - Show and Tell

## 5. Release Readiness
Sebelum cut release:
- Semua blocker issue close/defer
- Changelog update
- CI hijau
- Security check tidak ada high-risk terbuka
- Tag release semver (`v0.x.y`)

## 6. Contributor Experience
- Jaga issue tetap up-to-date
- Pecah task besar jadi issue kecil
- Tandai issue pemula dengan `good first issue`
- Balas PR/issue secara konsisten
