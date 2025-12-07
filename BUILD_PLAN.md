# Build Plan: Automated Newsletter Generation Platform

-## 1. Desired Outcome & Guardrails
- **Goal**: A weekly automation that ingests curated sources, drafts a polished MJML/Mailjet newsletter, and lets the user review/send via a Next.js UI without manual copy/paste.
- **Success criteria**:
  - Newsletter draft (text + images) generated end-to-end in <5 minutes for a typical topic set.
  - Mailjet campaign draft created automatically with zero manual HTML edits.
  - User can adjust topics, review/edit copy, preview final HTML, and trigger/send or schedule.
  - Pipeline reliability ≥ 95% over 8 consecutive weekly runs.
- **Guardrails**: respect Unsplash attribution, store secrets in environment/key vault, keep subscriber data only inside Mailjet/Supabase, design services so future workflows can reuse components, and keep all project code rooted directly in the repository root (no extra nested app directories).

## 2. Scope Summary (MVP)
1. Source discovery via NewsAPI/RSS plus Firecrawl MCP scraping/search.
2. AI-assisted article ranking, summarisation, and tone control via OpenRouter LLM with MCP tool-calls.
3. Image selection via Unsplash (or optional generative fallback) with attribution metadata.
4. MJML template population and Mailjet draft/test/send automation.
5. Next.js dashboard for configuration, review, approval, and scheduling.
6. Scheduler/orchestrator (Celery beat or cron) with logging, notification, and retry policies.

_Out of scope_: complex agent UX, segmentation/A-B testing, multi-channel publishing (future backlog).

## 3. Architecture Snapshot
Layer | Key Tech | Notes
----- | -------- | -----
UI | Next.js 16 (App Router, Tailwind, shadcn/ui) | Server actions/API routes talk to backend; optional next-devtools-mcp during dev for introspection.
Backend API | FastAPI + LangChain/OpenRouter SDK | Hosts workflow endpoints (generate draft, fetch status, approve/send) and wraps MCP clients.
Content Retrieval | NewsAPI/RSS clients, Firecrawl MCP server | MCP tools exposed to LLM as OpenAI-compatible functions; includes local scraper fallback.
LLM Orchestration | OpenRouter (GPT-4/Claude) with tool calling | Structured prompts for selection/summaries; handles Firecrawl tool invocations.
Images | Unsplash API (search/photos) + optional generative API | Stores attribution + URLs alongside article metadata.
Template/Email | MJML + Jinja2 renderer, Mailjet Python SDK | Produces HTML/text variants; posts to /campaigndraft lifecycle endpoints.
Storage/Auth | Supabase (Postgres + Auth) | Stores topics, run configs, draft history, logs; Supabase Auth protects dashboard.
Scheduler | Celery beat / cron worker | Triggers weekly runs, monitors retries; orchestrator can be extended to Airflow later.
Observability | Structured logging (JSON), Supabase log table, optional Sentry | Surfaced in UI + alerts (email/webhook).

## 4. Component Implementation Details
### 4.1 Configuration & Persistence
- **Data**: topic presets, keyword overrides, send schedule, API credentials metadata (stored as references to env/secrets), run history, manual edits.
- **Plan**: Supabase tables (`profiles`, `topic_presets`, `runs`, `draft_sections`, `images`). Use row-level security tied to Supabase Auth.
- **API**: FastAPI endpoints CRUD for topics, drafts; Next.js server actions call these.

### 4.2 Content Acquisition
- **Sources**: NewsAPI `get_everything`, curated RSS feeds, Firecrawl MCP (`firecrawl_scrape`, `firecrawl_search`).
- **Flow**:
  1. Scheduler triggers `collect_sources` task with topics/time window.
  2. Fetch NewsAPI batch (handle pagination + rate limits) and RSS feed pulls.
  3. For gaps, call Firecrawl via MCP client; sanitize/normalize output.
  4. Deduplicate by URL/hash, persist raw payloads for traceability.
- **Considerations**: exponential backoff on API limits, caching previous run results for fallback, configurable timeouts per source.

### 4.3 Article Selection & Summaries
- **Process**: Build candidate list → LangChain pipeline instructs LLM (via OpenRouter) to select top N stories and request extra scrapes via tool-calls if needed.
- **Prompt**: include brand voice samples, formatting schema (JSON sections with title, hook, summary, CTA, keywords, source_url).
- **Post-processing**: validate JSON schema, enforce max word counts, attach editorial notes.

### 4.4 Image Pipeline
- Primary: Unsplash `search/photos` per section keyword; store `image_url`, `thumb_url`, `photographer`, `unsplash_link`.
- Secondary: optional Stable Diffusion API call when no Unsplash result or for unique hero image.
- Embed attribution footer in MJML automatically.

### 4.5 Template Assembly
- Maintain base MJML template (header, hero, sections, CTA, footer).
- Use Jinja2 to inject dynamic content (titles, summaries, CTAs, attribution, unsubscribe note).
- Compile MJML → HTML/Text. Validate via MJML CLI before calling Mailjet.

### 4.6 Mailjet Automation
1. `POST /campaigndraft` via SDK (locale, sender, subject, list ID).
2. `POST /campaigndraft/{id}/detailcontent` with HTML + text.
3. `POST /campaigndraft/{id}/test` to send preview to configured emails; expose preview in UI.
4. `POST /campaigndraft/{id}/send` or schedule.
- Store Mailjet draft IDs + status for later audits.

### 4.7 Next.js Dashboard
- Pages: Authentication (Supabase), Topics & Sources config, Draft preview/editor (rich text + markdown diff), Schedule & History.
- Hooks into backend via REST/WebSocket for live run status.
- Provide manual trigger + override ability; show logs, errors, Unsplash credits.

### 4.8 Scheduler & Orchestration
- Celery worker handles tasks: `collect_sources`, `rank_select`, `summarize_sections`, `render_template`, `mailjet_publish`.
- Celery beat cron for weekly runs; manual trigger enqueues same workflow.
- For future scalability, abstract orchestrator so Airflow/LangGraph can plug in.

### 4.9 Observability & Resilience
- Structured logs persisted to Supabase `run_logs` (level, task, message, payload ref).
- Alerting: send email/slack/webhook on failure with a link to run detail.
- Retry strategy: per-task retries with jitter; fallback to previous successful newsletter if pipeline fails near deadline.

## 5. Delivery Phases & Exit Criteria
Phase | Duration | Key Deliverables | Exit Criteria
----- | -------- | ---------------- | -------------
0. Foundations | 3-4 days | Repo, env config, API keys, Supabase project, CI lint/unit templates | All secrets managed, pipelines deploying.
1. Data Layer & Scheduler | 1 week | Supabase schema + migrations, credential plumbing, Celery skeleton, cron schedule | Can save topics/config, run dummy scheduled job.
2. Content Acquisition | 1 week | NewsAPI/RSS ingestion, Firecrawl MCP client, dedupe/cache utilities, unit tests | Collects ≥20 articles per topic set with logs + error handling.
3. AI Selection & Summaries | 1-1.5 weeks | LangChain/OpenRouter workflow, schema validation, prompt library, tool-call integration | Produces structured sections with deterministic schema.
4. Images & Template | 0.5-1 week | Unsplash service, attribution handling, MJML template + renderer, HTML tests | Rendered HTML passes MJML validation and looks correct in preview.
5. Mailjet Integration | 0.5 week | Draft/create/test/send endpoints, status tracking | Able to create draft, send test email in sandbox.
6. Next.js Dashboard | 1 week | Auth, topics page, run history, draft preview/editor, send trigger | User can configure topics and approve/send generated draft.
7. Hardening & Launch | 1 week | End-to-end tests, logging/alerts, runbook, production-ready README, docs, training | Two consecutive successful dry-runs; stakeholders sign-off and README validated against deployment steps.

## 6. Test Strategy
- **Unit**: parsers, dedupe, prompt builders, Unsplash/Mailjet client wrappers (use VCR-style fixtures).
- **Integration**: workflow tests hitting staging APIs (flag to skip live calls in CI).
- **Contract**: JSON schema validation for LLM output, MJML snapshot tests.
- **E2E**: nightly pipeline dry-run to staging Mailjet list, captured in Supabase history.
- **Manual**: UI review, Mailjet preview tests each release.

## 7. Environment & Dependencies Checklist
- API keys: NewsAPI, OpenRouter, Firecrawl MCP token, Unsplash access key, Mailjet (public/private), Supabase service key.
- Tooling: Python 3.11+, FastAPI, LangChain, OpenRouter SDK, Celery/Redis, MJML CLI, Next.js 16, Tailwind, shadcn/ui, Supabase JS.
- Secrets management: `.env` for local, cloud secrets in deployment (e.g., Doppler, AWS SM).
- CI hooks: lint (ruff/eslint), type checks (mypy, tsc), unit test suite, Prettier/Tailwind formatter.

## 8. Risks & Mitigations (Focused)
Risk | Mitigation
---- | ----------
LLM hallucinations or off-brand tone | Few-shot prompt library, deterministic schema validation, manual UI approval before send.
API limits/downtime | Caching, retries with exponential backoff, fallback to previous draft, clear UI error surfacing.
MCP session complexity | Encapsulate MCP client, auto-handle session renewal, extensive logging of tool calls.
Image licensing | Enforce Unsplash attribution in template, log attribution metadata for audits.
Security/compliance | Store subscriber data only in Mailjet/Supabase with RLS, audit secrets, ensure unsubscribe links present.
Schedule drift | Scheduler health checks, watchdog alert if run doesn’t complete within SLA.

## 9. Decisions / Clarifications
1. **Hosting**: Deploy Next.js frontend to Vercel; run FastAPI + workers on Render (separate services).
2. **User roles**: Single role for MVP; multi-user role management deferred.
3. **Images**: Unsplash remains primary, but add optional manual image upload support in the dashboard.
4. **Notifications**: Email alerts only; recipient configured via `.env`.
5. **Approvals**: No additional approval workflow beyond existing manual review in UI.

---
_This document is the planning blueprint; no implementation work has been started._
