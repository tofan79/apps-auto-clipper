# Engineering Standards

Dokumen ini adalah aturan teknis untuk menjaga kualitas kontribusi.

## 1. SOLID Principles
- S - Single Responsibility: 1 modul = 1 tanggung jawab utama
- O - Open Closed: extensible tanpa ubah behavior lama
- L - Liskov Substitution: implementasi provider saling substitusi
- I - Interface Segregation: interface spesifik, tidak gemuk
- D - Dependency Inversion: depend ke abstraction, bukan concrete class

## 2. Type Safety
- Frontend: TypeScript strict mode, hindari `any`
- Backend: Python 3.11+ dengan type hints
- API contract: OpenAPI via FastAPI
- Input validation: Zod di frontend, Pydantic di backend

## 3. Code Quality Rules
- Hindari fungsi terlalu panjang, refactor bila kompleks
- Tidak pakai magic numbers tanpa konstanta bernama
- Naming convention:
  - Python: `snake_case`
  - TypeScript: `camelCase`
- Public function wajib punya docstring singkat
- Tambah test untuk perubahan logic penting

## 4. Performance Constraints
| Parameter | Nilai |
|---|---|
| Max video duration | 2 jam |
| Max concurrent jobs | 2 (configurable) |
| Whisper default model | `small` |
| FFmpeg render preset | `veryfast` |
| Target render speed | <= 1.2x real-time (GPU mode) |

## 5. Reliability Requirements
- Semua I/O harus ada error handling + logging
- Path handling wajib aman dari traversal
- Worker wajib support checkpoint/resume
- Memory/disk guard tidak boleh di-bypass

## 6. Security Baseline
- Electron hardening:
  - `contextIsolation: true`
  - `sandbox: true`
  - `nodeIntegration: false` di renderer
- IPC whitelist only
- Secret tidak boleh hardcoded
- API key wajib encrypted at-rest

## 7. Test Baseline
- Unit test untuk logic core
- Integration test untuk API + queue + checkpoint
- Pipeline integration untuk ingest -> transcribe -> render
- System test untuk skenario real (30 menit, 2 jam, crash recovery)
