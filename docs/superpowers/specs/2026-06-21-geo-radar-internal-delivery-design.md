# GEO Radar Internal Delivery Tool Design

## Summary

GEO Radar is an internal sales and delivery tool for AI search visibility services. It helps the team diagnose a prospect's current visibility in AI answers, compare that visibility with competitors, preserve evidence snapshots, and generate a report that can be used for sales, delivery, and renewal.

The first version is not a customer-facing SaaS. Customers do not log in. The internal team creates projects, runs checks, and shares report links or PDFs.

## Goals

- Turn a brand inquiry into a clear AI search visibility diagnosis.
- Give sales a fast way to prove demand and support service proposals.
- Give delivery a repeatable monthly report workflow.
- Reuse existing GEOFlow capabilities where practical, especially AI model configuration, visibility checks, content production, and distribution.
- Keep the first release narrow enough to ship and use in real sales conversations.

## Non-Goals

- Customer self-service login.
- Online payment or subscription billing.
- Agent or reseller white-label portals.
- Video editing, cloud clipping, or social media publishing.
- Fully automatic optimization without human approval.
- Replacing the existing GEOFlow content engineering system.

## Users

Sales users create prospect projects, run quick checks, and export sales reports.

Delivery users run standard or monthly checks, review evidence snapshots, and produce client-facing delivery reports.

Operators review visibility gaps and convert them into content, knowledge base, or distribution actions.

Admins configure AI model providers, report templates, and internal settings.

## Core Workflow

1. Create a project for a prospect or client.
2. Enter brand, company, website, industry, region, competitors, and conversion targets.
3. Generate or import prompt questions.
4. Run AI visibility checks across selected providers.
5. Analyze brand mentions, competitor mentions, answer position, sentiment, citations, and conversion target exposure.
6. Save evidence snapshots for important answers.
7. Generate a GEO score and recommended actions.
8. Export a report link or PDF.
9. Repeat monthly and compare with prior runs.

## Product Structure

### Project List

The project list is the internal home page. It shows all sales and delivery projects with status, latest GEO score, latest run time, owner, and quick actions.

Required fields:

- Client name
- Brand name
- Industry
- Region
- Latest GEO score
- Latest run time
- Status: lead, quoted, won, active, paused, lost
- Owner

Quick actions:

- View project
- Run check
- Open latest report
- Create monthly report

### Project Creation

Project creation captures the minimum information needed to run a useful visibility check.

Required fields:

- Client company name
- Brand name
- Industry
- Region

Optional fields:

- Website URL
- Main products or services
- Brand description
- Contact name
- Contact phone or WeChat
- Competitor names and websites
- Conversion targets such as website, phone, WeChat, address, or form URL

### Project Dashboard

The dashboard gives a decision-focused view, not raw logs.

Top metrics:

- GEO score
- Brand mention rate
- Average recommended position
- Competitor pressure
- AI platform coverage
- Website exposure count
- Contact exposure count
- Citation count

Decision blocks:

- Biggest visibility gap
- Strongest competitor
- Most valuable missing prompt
- Highest risk AI misunderstanding
- Next recommended action

### Prompt Library

Each project has a prompt library used for checks. Prompts can be generated, edited, disabled, and prioritized.

Prompt intents:

- Brand query
- Industry recommendation
- Regional recommendation
- Purchase decision
- Competitor comparison
- Pain-point solution
- Alternative solution
- Conversion intent

Prompt examples:

- "{region}有哪些靠谱的{industry}公司？"
- "{brand_name}怎么样？"
- "{competitor}和{brand_name}哪个更适合？"
- "遇到{pain_point}应该找哪家公司？"

### Run Check

The run screen lets the user choose scope and providers.

Run modes:

- Quick check: 10 prompts across 3 providers.
- Standard check: 30 prompts across 5 providers.
- Deep check: up to 100 prompts across selected providers.

Initial providers:

- Doubao
- DeepSeek
- Qwen
- Tencent Yuanbao or Hunyuan
- ERNIE or Wenxin

Future providers:

- Kimi
- iFlytek Spark
- Baidu AI surfaces
- Quark AI
- ChatGPT
- Gemini

Runs should be queued so long checks do not block the browser. Each result must store enough raw context to support later review without exposing API keys.

### Results

The result table is the operational view of a run.

Columns:

- Prompt
- Provider
- Brand mentioned
- Brand position
- Competitor mentions
- Sentiment
- Citation URLs
- Conversion target hits
- Risk tags
- Score
- Snapshot

Result details show:

- Full answer text
- Highlighted brand mentions
- Highlighted competitor mentions
- Citation URLs
- Conversion target matches
- Raw provider metadata
- Error details when a provider fails

### Snapshots

Snapshots are shareable evidence records for selected results.

Snapshot content:

- Project and brand
- Provider
- Prompt
- Query time
- Original AI answer
- Highlighted brand and competitors
- Citation URLs
- Conversion target hits
- Risk tags

Snapshots use public tokens, not customer accounts. Token links should be unguessable and revocable.

### Reports

Reports are the main sales and delivery artifact.

Report types:

- Sales diagnosis report
- Monthly delivery report
- Renewal risk report

Sales report sections:

1. Cover
2. Executive conclusion
3. GEO score
4. AI platform performance
5. Competitor comparison
6. Prompt-level evidence
7. Snapshot highlights
8. Visibility gaps
9. Recommended 90-day optimization plan
10. Service package and next step

Monthly report sections:

1. Cover
2. Month-over-month score changes
3. Brand mention trend
4. Competitor pressure trend
5. New evidence snapshots
6. Completed optimization actions
7. Next month action plan

Reports can be viewed as HTML and exported to PDF.

## GEO Scoring

The first scoring model uses a transparent weighted formula:

- Brand mention rate: 30 percent
- Recommended position: 20 percent
- Platform coverage: 15 percent
- Competitor pressure: 15 percent
- Conversion target exposure: 10 percent
- Citation and source coverage: 10 percent

Score levels:

- 0-39: Weak AI visibility
- 40-59: Basic but unstable visibility
- 60-79: Competitive visibility
- 80-100: Strong AI search presence

The score should be explainable in the report. Users should see which component pulled the score down.

## Recommended Actions

The tool should turn gaps into practical actions.

Action categories:

- Website content improvement
- Knowledge base improvement
- FAQ generation
- Comparison article generation
- Case study generation
- Third-party source or distribution action
- Conversion target cleanup
- AI misunderstanding correction

In the first release, actions are recommendations only. They do not publish automatically.

## Data Model

### projects

- id
- client_name
- brand_name
- website_url
- industry
- region
- description
- contact_name
- contact_phone
- status
- owner_id
- latest_score
- latest_run_at
- created_at
- updated_at

### competitors

- id
- project_id
- name
- website_url
- created_at
- updated_at

### conversion_targets

- id
- project_id
- type
- value
- label
- created_at
- updated_at

### prompts

- id
- project_id
- question
- intent
- priority
- is_active
- created_at
- updated_at

### runs

- id
- project_id
- mode
- status
- prompt_count
- provider_count
- result_count
- geo_score
- brand_mention_rate
- average_position
- competitor_pressure
- platform_coverage
- conversion_exposure
- citation_coverage
- started_at
- completed_at
- summary
- created_at
- updated_at

### results

- id
- run_id
- prompt_id
- provider_key
- provider_name
- provider_region
- answer_text
- brand_mentioned
- brand_position
- competitor_mentions
- sentiment
- citation_urls
- conversion_hits
- risk_tags
- score
- raw_payload
- created_at
- updated_at

### snapshots

- id
- result_id
- public_token
- title
- html_content
- revoked_at
- created_at
- updated_at

### reports

- id
- project_id
- run_id
- type
- title
- public_token
- report_html
- pdf_path
- revoked_at
- created_at
- updated_at

## Architecture

The recommended implementation is a focused module inside the existing Laravel-based GEOFlow codebase, not a new standalone framework.

Recommended stack:

- Laravel backend
- Blade and Tailwind views for the first release
- PostgreSQL database
- Laravel queues for long runs
- Existing AiModel provider configuration
- Existing GEO visibility service as the starting point
- HTML report rendering with first-release PDF export

Module boundaries:

- Project management handles client and brand data.
- Prompt generation handles question creation and editing.
- Visibility runs handle provider calls and result storage.
- Result analysis handles mention, position, sentiment, citations, risks, and scoring.
- Snapshot publishing handles evidence links.
- Reporting handles sales and monthly report rendering.
- Recommendation generation maps result gaps to suggested actions.

## Error Handling

Provider failures should not fail the entire run. Each provider error becomes a failed result row with a clear message.

Run statuses:

- queued
- running
- completed
- completed_with_errors
- failed

The report should clearly separate unavailable provider data from negative visibility results. A failed model call is not the same as a brand not being mentioned.

API keys must never be exposed in result payloads, snapshots, reports, logs, or browser-rendered HTML.

## Security

Only internal authenticated admins can manage projects and runs.

Shared snapshot and report links use unguessable public tokens.

Shared links can be revoked.

Reports must not include provider raw payloads unless explicitly marked internal.

Customer contact information stays internal and should not appear in public reports unless deliberately included.

## Testing

Core tests:

- Project creation validation.
- Prompt generation produces expected intents.
- Mock run creates expected runs and results.
- Real provider failures are stored as result errors.
- Scoring formula is stable and explainable.
- Snapshot tokens are unique and revocable.
- Report pages do not expose API keys.
- PDF export succeeds for a sample report.

Manual checks:

- Create project.
- Add competitors and conversion targets.
- Generate prompts.
- Run mock check.
- Run limited real check.
- Open result details.
- Create snapshot.
- Generate sales report.
- Export PDF.

## MVP Scope

The MVP includes:

- Project list and creation
- Competitor and conversion target management
- Prompt generation and editing
- Quick, standard, and deep run modes
- Result analysis
- GEO score
- Snapshot evidence pages
- Sales report page
- PDF export

The MVP excludes:

- Customer login
- Online payment
- Agent portals
- Full reseller white-labeling
- Automatic publishing
- Video workflows
- Advanced team roles

## Follow-On Phases

Phase 2:

- Monthly report comparison.
- Trend charts.
- Renewal risk indicators.
- Content action approval workflow.

Phase 3:

- Connect recommended actions to GEOFlow article generation.
- Generate FAQ, comparison, and case study drafts from visibility gaps.
- Attach actions to delivery reports.

Phase 4:

- Add optional customer-facing read-only portal.
- Add white-label report branding.
- Add package and pricing templates.

## First-Release Decisions

- Build as a Laravel module inside the existing GEOFlow codebase.
- Render reports as HTML first, then export the same report view to PDF using the most reliable renderer already available in the deployment environment.
- First-release providers are Doubao, DeepSeek, Qwen, Tencent Yuanbao or Hunyuan, and ERNIE or Wenxin. Kimi, Spark, Baidu AI surfaces, Quark AI, ChatGPT, and Gemini move to later phases unless the configured model list already supports them with no extra adapter work.
- First-release reports use fixed templates with generated narrative text. Editable narrative blocks are a phase 2 feature.
