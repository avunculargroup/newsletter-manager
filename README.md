# Automated Newsletter Platform

This repository implements the build plan from `BUILD_PLAN.md`: a fullstack
workflow that collects articles, summarises them with an LLM, selects imagery,
renders MJML and drafts a Mailjet campaign while exposing a Next.js dashboard
for configuration and approvals.

## Project layout

```
backend/   FastAPI app, Celery workers and workflow services
frontend/  Next.js 16 (App Router) dashboard powered by Tailwind + RSC
```

Key backend modules mirror the plan:

- `services/content_sources.py` – NewsAPI/RSS/Firecrawl ingestion with
  deduplication.
- `services/llm_service.py` – OpenRouter powered section/tone generation.
- `services/image_service.py` – Unsplash search with attribution metadata.
- `services/template_renderer.py` – MJML + Jinja2 templating.
- `services/mailjet_service.py` – Draft/create/test/send automation.
- `workflows/pipeline.py` – Orchestrates the end-to-end run and persists state
  via Supabase.
- `routers/*` – Topics CRUD, run triggers, draft previews and health probes.

The frontend aligns with the dashboard requirements (topics & sources config,
run history, live draft preview, manual trigger + schedule controls) and
communicates with the FastAPI backend via the REST endpoints described above.

## Getting started

1. Copy `.env.example` to `.env` and provide the keys described in the build
   plan (Supabase, NewsAPI, OpenRouter, Unsplash, Mailjet, Firecrawl, Redis).
2. Install backend deps: `cd backend && pip install -e .[dev]`.
3. Install frontend deps: `cd frontend && npm install`.
4. Run services (see `docker-compose.yml` for an end-to-end dev stack) or start
   them individually:

   ```bash
   # API
   uvicorn backend.app.main:app --reload --port 8000

   # Celery worker + beat (Redis required)
   celery -A backend.celery_app.celery_app worker -l INFO
   celery -A backend.celery_app.celery_app beat -l INFO

   # Frontend dashboard
   cd frontend && npm run dev
   ```

5. Visit `http://localhost:3000` to manage topics, inspect draft previews and
   trigger runs. The dashboard reads live run status and latest drafts from the
   backend and Supabase.

## Tests & linting

- Backend unit tests: `cd backend && pytest`.
- Frontend lint/type checks: `cd frontend && npm run lint && npm run check`.

## Next steps

- Connect Supabase Auth to protect the dashboard.
- Configure the scheduler (Celery beat or cron) to enqueue runs weekly.
- Wire production secrets via Doppler/AWS SM and enable observability exports
  (Supabase `run_logs` table, Sentry, etc.).
