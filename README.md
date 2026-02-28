# AutoClipper AI

Desktop-first AI clip generator for turning long-form video into short-form social clips.

## Status
- Current stage: Foundation completed (Stage 1)
- Stack: Python services + Node monorepo (pnpm + turbo)

## Project Structure
```text
apps/        # Frontend + desktop shell
services/    # API, worker, AI engine
packages/    # Shared config/database/utils
tests/       # Unit and integration tests
```

## Quick Start
1. Install Node.js 20+ and pnpm 9+
2. Install Python 3.11+
3. Install dependencies:
   - `pnpm install`
   - `services/api/.venv/Scripts/python -m pip install -r services/api/requirements.txt`
   - `services/worker/.venv/Scripts/python -m pip install -r services/worker/requirements.txt`
4. Run dev mode from root:
   - `pnpm dev`

## Testing
- Install test dependencies: `python -m pip install -r requirements-dev.txt`
- Run unit tests: `python -m pytest -q`

## Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR.

## Maintainer
- [@tofan79](https://github.com/tofan79)

## Donation
- GitHub Sponsors: https://github.com/sponsors/tofan79
- Saweria: https://saweria.co/tofan79

## Security
Please report vulnerabilities via [SECURITY.md](SECURITY.md), not public issues.

## License
This project is licensed under the MIT License. See [LICENSE](LICENSE).
