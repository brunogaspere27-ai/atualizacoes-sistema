Title: chore: security, dev tooling, CI, UI theme and dashboard polish

Description:
This PR contains multiple non-functional and UI improvements:

- Security: removed committed `.env` containing credentials and added `.env.example`.
- Dev tooling: added `requirements-dev.txt`, `.pre-commit-config.yaml`, and a script to install dev tools.
- CI: added GitHub Actions workflow `.github/workflows/ci.yml` to run lint and tests.
- UI: added centralized theme `telas/theme.py` and refactored `main.py`, `telas/dashboard.py`, and `telas/relatorios.py` to use it.
- Migrations: added a simple migrations runner under `migrations/` and an initial migration.
- Gemma3 scaffolding: added runner and config for optional local model inference.

Notes and migration steps:
- Rotate Supabase credentials immediately — the repository previously contained secrets.
- Run dev tools installer and pre-commit locally before pushing:

```powershell
.\scripts\install_dev_tools.ps1
pre-commit run --all-files
```

- To apply migrations locally (after creating DB):

```powershell
python migrations/apply_migrations.py
```

If you want this PR opened automatically, run:

```powershell
.\scripts\commit_and_push.ps1 -createPR
```

This requires GitHub CLI (`gh`) configured and authenticated.
