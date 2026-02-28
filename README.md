# AutoClipper AI

Desktop-first AI clip generator for turning long-form video into short-form social clips.

## Status
- Current stage: Foundation completed (Stage 1)
- Stack: Python services + Node monorepo (pnpm + turbo)

## Public Blueprint
- Product direction and expected output: [App Specification](docs/app_spec.md)
- Engineering rules and constraints: [Engineering Standards](docs/engineering_standards.md)
- Contributor onboarding: [Contributor Start Here](docs/contributor_start_here.md)
- Maintainer operations: [Maintainer Operations](docs/maintainer_ops.md)
- Repo admin setup: [Repository Admin Setup](docs/repo_admin_setup.md)

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
3. Setup local env file:
   - copy `.env.dev.example` to `.env`
4. Install dependencies:
   - `pnpm install`
   - `services/api/.venv/Scripts/python -m pip install -r services/api/requirements.txt`
   - `services/worker/.venv/Scripts/python -m pip install -r services/worker/requirements.txt`
5. Run dev mode from root:
   - `pnpm dev`

## Testing
- Install test dependencies: `python -m pip install -r requirements-dev.txt`
- Run unit tests: `python -m pytest -q`

## Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR.

## Maintainer
- [@tofan79](https://github.com/tofan79)

## Security
Please report vulnerabilities via [SECURITY.md](SECURITY.md), not public issues.

## License
This project is licensed under the MIT License. See [LICENSE](LICENSE).
