# Winner Bot

Professional signals bot and dashboards.

## Quick Start (Backend)

- Copy `.env.example` to `.env` and fill values
- Create venv and install dependencies

```
python -m venv .venv
source .venv/bin/activate
pip install -r bot/requirements.txt
uvicorn bot.bot:app --reload --port 8000
```

Endpoints:
- `/signals/latest`
- `/signals/history`
- `/user/status?email=you@example.com`
- `/admin/metrics` (requires `X-API-Key` header)
- `/contact`, `/terms`, `/privacy`

## Repo Structure

See `docs/spec.md` for full details.