# Workflow

This repo describes an **automated newsletter generation workflow**: collect sources → draft copy + images → render email → create a Mailjet campaign draft → review/approve → send/schedule.

## Roles & systems

- **Scheduler/orchestrator**: triggers the weekly run (or manual run).
- **Backend API/worker**: executes the pipeline steps.
- **Next.js UI**: configuration + review/approval.
- **Content sources**: NewsAPI, RSS feeds, and scraping/search via Firecrawl (MCP).
- **LLM via OpenRouter**: ranking + summarisation + structured drafting with tool-calls.
- **Images**: Unsplash (with attribution) and/or optional generative fallback.
- **Template**: MJML + templating (e.g., Jinja2) compiled to responsive HTML.
- **Email delivery**: Mailjet campaign draft lifecycle (create → content → test → send/schedule).
- **Storage/observability**: Supabase tables for configs, run history, drafts, logs.

## High-level flow

```text
Configure topics/schedule (UI)
        |
        v
Scheduler triggers run (weekly or manual)
        |
        v
Collect + dedupe sources (NewsAPI/RSS/Firecrawl)
        |
        v
Rank/select stories (LLM)
        |
        v
Fetch full text as needed (local scrape or Firecrawl)
        |
        v
Draft sections (LLM → validated structured output)
        |
        v
Select images + attribution (Unsplash)
        |
        v
Render MJML template → compile to HTML + text
        |
        v
Create Mailjet campaign draft + upload content
        |
        v
Send test email + show preview
        |
        v
Human review/edit in UI
        |
        v
Approve → Send now or schedule
        |
        v
Persist status + logs + alerts
```

## Step-by-step workflow

### 1) Configure (UI)
- **Inputs**: topic presets, keywords, preferred sources, voice/tone settings, send schedule, test-recipient emails.
- **Persistence**: store configuration and per-run overrides so a run can be reproduced and audited.

### 2) Trigger a run (scheduled or manual)
- Scheduler enqueues a run with a unique `run_id`.
- Backend records a **run record** (start time, config snapshot, initial status).

### 3) Collect sources
- Pull candidates from:
  - **NewsAPI** queries for the configured time window.
  - **RSS** feeds.
  - **Firecrawl MCP** search/scrape when RSS/NewsAPI coverage is insufficient.
- Normalize items to a common schema (title, url, published_at, source, excerpt, raw payload reference).
- **Deduplicate** by URL/canonical URL and/or content hash.

### 4) Rank and select stories
- Provide the candidate set to the LLM (via OpenRouter) with a structured selection prompt.
- LLM may request additional context via tool-calls (e.g., Firecrawl scrape/search) before final selection.
- Output is a validated structured list (e.g., top N stories with rationale/keywords).

### 5) Enrich and extract full text
- For each selected story, fetch article body:
  - Use local extraction (e.g., BeautifulSoup/newspaper-style extraction) when possible.
  - Use Firecrawl structured extraction when sites are difficult.
- Store extracted text (or a reference) for traceability.

### 6) Draft newsletter sections
- LLM generates per-section content in your brand voice with a strict schema (title, hook, summary, CTA, link).
- Validate schema + enforce length constraints; if invalid, retry with a corrective prompt.

### 7) Select images
- For each section, derive search keywords and query **Unsplash**.
- Persist image metadata needed for compliance:
  - photographer name
  - Unsplash attribution link
  - image URL(s)
- If no suitable results, optionally fall back to a generative image provider (policy-dependent).

### 8) Render email (MJML → HTML/text)
- Populate a base MJML template (header/hero, sections, footer).
- Ensure:
  - attribution footer is present when using Unsplash images
  - unsubscribe/legal placeholders are compatible with Mailjet
- Compile MJML to final HTML and generate a text alternative.

### 9) Create Mailjet campaign draft
- Create a draft campaign (sender, subject, list/segment, locale).
- Upload HTML + text content.
- Send a **test email** to configured recipients.
- Persist Mailjet draft IDs and status on the run.

### 10) Review, edit, and approve (UI)
- UI shows:
  - draft preview (HTML + text)
  - per-section content and images
  - run logs and warnings
- Human can edit copy/subject and regenerate specific steps if supported.

### 11) Send or schedule
- On approval, trigger Mailjet send immediately or schedule for a specific time.
- Record final send status and timestamps.

## Logging, retries, and failure handling

- **Logging**: each step writes structured logs (step name, duration, key IDs, error payload refs).
- **Retries**: network/API calls should use exponential backoff + jitter; LLM schema failures should retry with constrained corrective prompting.
- **Idempotency**: runs should be replay-safe (e.g., avoid creating multiple Mailjet drafts unless explicitly requested; store `mailjet_draft_id` per `run_id`).
- **Fallbacks**: when sources are unavailable or the run fails late, optionally fall back to the previous successful draft for continuity.

## Security and data boundaries

- Store secrets in environment/secrets management (not in the DB).
- Do not store subscriber contact data outside Mailjet.
- Keep audit trails (run configs, chosen sources, tool calls, Mailjet IDs) to support debugging and compliance.
