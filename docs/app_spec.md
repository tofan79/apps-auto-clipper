# AutoClipper AI - App Spec

Dokumen ini adalah spesifikasi produk dan teknis level tinggi untuk contributor.

## 1. Project Overview
**AutoClipper AI** adalah aplikasi desktop berbasis AI yang mengotomatiskan proses pembuatan short-form video clips dari konten video panjang (YouTube atau file lokal).

### Fitur Utama
| Fitur | Deskripsi |
|---|---|
| Video Ingestion | Download YouTube atau input file lokal |
| AI Transcription | Transkripsi otomatis dengan word-level timestamps |
| Viral Hook Detection | Deteksi momen viral secara multi-signal |
| Auto Face Framing | Reframe 16:9 ke 9:16 dengan face tracking |
| Karaoke Subtitles | Subtitle dinamis word-highlight otomatis |
| Platform Metadata | Generate judul, caption, hashtag per platform |
| LAN Monitoring | Pantau progres dari HP via browser |
| Offline Mode | Berfungsi penuh tanpa internet (Ollama) |

### Target Platform
- Windows: `.exe` installer (NSIS via Electron Builder)
- Linux: `.AppImage` portable

## 2. Engineering Standards
Standar detail ada di [engineering_standards.md](engineering_standards.md). Ringkasan:
- SOLID principles untuk arsitektur
- Type safety ketat (TypeScript strict + Python type hints)
- Validation gate pada semua input user
- Rule kualitas kode dan test coverage minimum
- Performance guard untuk workload panjang

## 3. Tech Stack

### Frontend
| Teknologi | Versi | Fungsi |
|---|---|---|
| Next.js | 14+ | UI framework |
| TypeScript | 5+ | Type safety |
| TanStack Query | v5 | Server state management |
| Zustand | latest | Client state management |
| Shadcn/UI + Tailwind | latest | UI components + styling |
| Zod | latest | Input validation |

### Backend
| Teknologi | Versi | Fungsi |
|---|---|---|
| FastAPI | 0.110+ | REST API & WebSocket |
| Python | 3.11+ | Runtime |
| Pydantic | v2 | Schema & validation |
| SQLAlchemy | 2.0 | ORM |
| Task queue | latest | In-process queue manager (Redis optional) |
| Redis | 7+ | Optional broker for future scaling |

### AI & Video Engine
| Teknologi | Fungsi |
|---|---|
| Faster-Whisper | Transkripsi |
| MediaPipe | Face detection & tracking |
| yt-dlp | YouTube download |
| FFmpeg | Video processing & rendering |
| Ollama | Local LLM runtime (offline) |
| OpenRouter | Online fallback |

### Desktop Wrapper
| Teknologi | Fungsi |
|---|---|
| Electron | Desktop shell |
| Electron Builder | Packaging & installer |

## 4. System Architecture

```text
ELECTRON DESKTOP SHELL
  -> IPC Bridge (whitelist only)
NEXT.JS FRONTEND
  -> REST + WebSocket
FASTAPI MASTER API
  -> Background Worker (queue + checkpoint + guard)
  -> AI Engine (transcribe + hook detect + render)
  -> LLM Provider (Ollama default, OpenRouter fallback)
```

### Binding Rules
- Default: API bind ke `127.0.0.1:8000`
- LAN mode: bind ke `0.0.0.0:8000` + token auth wajib aktif
- Frontend dev: port `3000` dengan proxy ke backend

## 5. Expected Output
Setiap job yang selesai menghasilkan:
- N clip `.mp4`
- Subtitle karaoke embedded
- Thumbnail per clip
- Viral score summary
- Metadata platform (YouTube, TikTok, Instagram, Facebook)

Kriteria kualitas output:
- Tidak ada black area pada blur-landscape mode
- Framing stabil dan tidak jitter
- Subtitle sinkron terhadap kata
- Hasil konsisten untuk input dan setting yang sama

## 6. Scope v1
- Desktop shell + local services
- Queue aman untuk single-user
- Checkpoint resume saat crash
- Profile low-spec (minimum 4 core, 8GB)
- GPU detect + CPU fallback
- First-run setup

## 7. Definition of Done (Release Candidate)
- Pipeline end-to-end jalan di minimum spec tanpa crash
- Video 2 jam bisa selesai diproses
- Resume checkpoint berfungsi setelah proses di-kill
- Queue berjalan berurutan dan stabil
- Clip output lengkap dengan subtitle + metadata
- Installer berjalan di mesin bersih

## 8. Contributor Read Order
1. `README.md`
2. `docs/app_spec.md`
3. `docs/engineering_standards.md`
4. `CONTRIBUTING.md`
5. `SECURITY.md`
