# Contributor Start Here

Panduan singkat untuk kontribusi pertama.

## 1. Baca Dokumen Inti
1. `README.md`
2. `docs/app_spec.md`
3. `docs/engineering_standards.md`
4. `CONTRIBUTING.md`
5. `SECURITY.md`

## 2. Setup Lokal
1. Copy `.env.dev.example` menjadi `.env`
   - perangkat low-spec: pakai `LLM_PROVIDER=openrouter`
   - isi `OPENROUTER_API_KEY` dan opsional `OPENROUTER_MODEL`
2. Install dependency:
   - `pnpm install`
   - `services/api/.venv/Scripts/python -m pip install -r services/api/requirements.txt`
   - `services/worker/.venv/Scripts/python -m pip install -r services/worker/requirements.txt`
3. Jalankan app:
   - `pnpm dev`

## 3. Pilih Task
- Buka Issues dan filter label:
  - `good first issue`
  - `help wanted`
  - `stage-2` sampai `stage-7`

## 4. Alur PR
1. Buat branch: `feat/<nama-task>` atau `fix/<nama-task>`
2. Kerjakan perubahan kecil dan fokus
3. Tambahkan/ubah test bila perlu
4. Submit PR dengan template yang tersedia

## 5. Definisi PR Siap Review
- Scope jelas
- Tidak ada secret/credential
- Tidak ada file lokal/runtime ikut commit
- Lulus CI
