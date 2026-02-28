# Contributing Guide

Thanks for contributing to AutoClipper AI.

## Workflow
1. Fork the repository
2. Create a branch from `main`
3. Make focused changes
4. Add/update tests
5. Open a Pull Request

## Branch Naming
- `feat/<short-description>`
- `fix/<short-description>`
- `docs/<short-description>`
- `chore/<short-description>`

## Commit Message Style
- `feat: add job queue cancellation`
- `fix: handle missing config file`
- `docs: update setup instructions`

## Pull Request Checklist
- [ ] Scope is clear and small
- [ ] Tests added or updated
- [ ] No secrets or local files included
- [ ] Documentation updated if needed

## Development Setup
- `pnpm install`
- Setup service virtualenvs
- Install Python dependencies from each service `requirements.txt`
- Run project: `pnpm dev`

## Code Standards
- Keep modules single-responsibility
- Keep public APIs typed
- Avoid hardcoded OS-specific paths
- Log all I/O failures with useful context
