# AI Republic – System Architecture Plan (Spirits, Orchestrator, Traits/LoRA, Grading)

This plan consolidates THE_ANSWER, the Minion Tools Orchestration design, and the Traits/LoRA point system into a single implementation roadmap aligned with the current V2 (Flask + SQLAlchemy + PostgreSQL) stack.

Terminology
- Minion: The user-visible agent (dispatcher/aggregator)
- Spirit: Specialized, non-visible helper that executes a focused set of tools (a “hidden minion”)
- Orchestrator: Server-side decision layer that routes tasks from Minion to Spirits

Executive Summary
- One visible Minion, many Spirits behind it. Minion stays lightweight, delegates execution.
- Tool access is governed by Minion level and rank (XP/RPG-style gating).
- Traits/LoRA point system controls voice/personality evolution with slots and intensity points.
- A grading system evaluates outcomes per task (accuracy, revisions, complexity, efficiency, skill selection) and feeds XP/rank progression and a public “resume.”
- All metrics, states, and events are persisted in PostgreSQL (JSONB for flexible fields), surfaced via REST and WebSocket progress.

Current State (V2)
- Backend (5001) is PostgreSQL + SQLAlchemy; minions stored in `external_api_models`.
- Frontend is Vue + Vite; URL config centralized in `src/config/api.js`.
- Minion creation persists core fields; capabilities/parameters/tags JSON handled; some fields inferred client-side.
- Training endpoints exist (placeholder) and repositories exist for external training jobs.
- Toast notifications now added for consistent UX.

Target Architecture Overview
- Visible Minion (UI): Single chat and dashboard.
- Orchestrator (API):
  - Intent parsing and task decomposition.
  - Spirit selection based on Minion level/rank/tool permissions.
  - Parallel Spirit execution, result aggregation, fallback strategy.
  - Progress via WebSocket, files over HTTP links.
- Spirits:
  - Knowledge, Report, Builder, Connector, Checker, Strategist (see MinionToolsOrchestrationArchitecture.md).
  - Registered in a tool registry; dynamically loaded by the orchestrator.
- Grading & History:
  - Task-level scoring persisted.
  - Revision tracking and difficulty multipliers.
  - Aggregated scores form Minion resume and ranking.
- Traits/LoRA System:
  - Slots unlocked by training level; intensity points distributed with compatibility bonuses and conflict penalties.

Core Components (Server)
- Tool Registry: JSON/DB-backed registry of available tools with metadata, permissions, and resource hints.
- Orchestrator Service: Given a task, selects Spirits, executes, aggregates, and emits events.
- Spirit Runners: Thin adapters per specialization with uniform interface (execute_task).
- Grading Engine: Computes task score using rubric from THE_ANSWER.
- History/Event Logger: Writes immutable events (created, trained, executed, graded) and snapshots.

Data Model Additions (PostgreSQL)
Note: Use JSON/JSONB for new flexible fields.
- external_api_models (existing)
  - Add columns (if not present):
    - quantization VARCHAR(50) NULL
    - model_stats JSONB NULL  // snapshot at creation: { parameters, quantization, context_length, max_tokens, provider }
    - training_level INT DEFAULT 1
    - total_training_sessions INT DEFAULT 0
    - trait_points_available INT DEFAULT 10
    - trait_points_spent INT DEFAULT 0

- minion_task_events (NEW)
  - id PK, user_id FK, minion_id FK, type (created|task_started|task_completed|graded|trained),
  - payload JSONB, score NUMERIC(5,2) NULL, complexity INT NULL,
  - revisions INT DEFAULT 0, duration_ms INT NULL,
  - created_at TIMESTAMP DEFAULT now()

- minion_task_scores (NEW) – denormalized per-task score breakdown
  - id PK, event_id FK, minion_id FK
  - accuracy_score INT, revision_penalty INT, complexity_multiplier NUMERIC(3,2),
  - skill_adherence INT, time_efficiency INT
  - aggregate_score NUMERIC(5,2)

- minion_resume (NEW) – current computed profile for quick reads
  - minion_id PK
  - overall_rating NUMERIC(5,2)
  - tasks_completed INT, success_rate NUMERIC(5,2)
  - strengths JSONB, weaknesses JSONB
  - last_updated TIMESTAMP

- traits_loadout (NEW)
  - id PK, minion_id FK, slots INT, points_available INT, points_spent INT
  - trait_intensities JSONB  // { friendly: 4, creative: 3, supportive: 3 }
  - compatibility_score NUMERIC(5,2), effectiveness_bonus NUMERIC(5,2)

API Surface (Initial)
- Minions
  - POST /api/v2/external-models → create minion (accepts parameters, quantization; store `model_stats` snapshot and emit created event)
  - GET /api/v2/users/:user_id/minions → list minions (return `model_stats` merged)
  - GET /api/v2/users/:user_id/minions/:id → minion details

- Orchestrator & Tasks (Phase 2)
  - POST /api/v2/tasks → create task for a minion; orchestrator delegates to Spirits
  - GET /api/v2/tasks/:id → task status/result
  - WS /ws → progress streaming

- History & Grading
  - GET /api/v2/minions/:id/history → list `minion_task_events`
  - POST /api/v2/minions/:id/grade → submit rubric inputs (if manual), compute/store scores
  - GET /api/v2/minions/:id/resume → precomputed `minion_resume`

- Traits/LoRA
  - GET /api/v2/minions/:id/traits → current loadout
  - POST /api/v2/minions/:id/traits → update distribution (enforce slot/points rules)

Orchestration Flow (High-Level)
1. UI sends user request → POST /tasks
2. Orchestrator parses intent → splits into sub-tasks
3. Select Spirits based on minion level/rank and registry permissions
4. Run Spirits in parallel; stream progress via WS
5. Aggregate outputs; return final result
6. Log event(s); compute provisional grade if auto

Grading System (from THE_ANSWER) [See reference]
- Metrics
  - Task Accuracy (0–100)
  - Revision Count (penalty)
  - Task Complexity Multiplier (×1, ×2, ×3)
  - Skill Adherence (bonus/penalty for correct tools)
  - Time Efficiency (bonus for faster completion)
- Aggregation
  - Weighted score per task → rolling success rate
  - Public resume fields: level, strengths, tasks completed, revision ratio, rankings
- Storage
  - Raw event in `minion_task_events`
  - Breakdown in `minion_task_scores`
  - Periodic recompute into `minion_resume`

Traits/LoRA Point System (from traits_point_system_lora.md)
- Slots unlock by training level (Level 10 → 1 slot, 15 → 2, 20 → 3, 25 → 4, 30+ → 5)
- Intensity points allocated with synergy bonuses and conflict penalties
- Store current loadout and derived scores in `traits_loadout`
- Training jobs (external_training_jobs) attach LoRA configs and write an event

Frontend Integration
- Minion Profile:
  - Show Parameters, Quantization, Context, Max Tokens from `model_stats`
  - History timeline (events), current resume rating, strengths/weaknesses
  - Traits editor (enforce slots/points, show compatibility score)
- Minion Builder:
  - On create → include quantization if available; backend stores snapshot
  - Show computed stats consistently
- Notifications: Use toast service for task/run/grade outcomes
- WebSocket: Live progress updates for multi-spirit execution

Implementation Priorities (Milestones)
- P0 – Persistence & Retrieval
  - Add `model_stats` snapshot at minion creation (parameters, quantization, context_length, max_tokens, provider)
  - Extend GET minions to merge `model_stats` server-side (avoid client inference)
  - Minimal history: write “created” event on create

- P1 – History & Grading Foundations
  - Create tables: `minion_task_events`, `minion_task_scores`, `minion_resume`
  - Endpoints: GET history, POST grade, GET resume
  - Update training flow to log events (start, complete, fail)

- P2 – Orchestrator + Spirits (MVP)
  - Registry: static registry file → DB later
  - Implement 2–3 Spirits (Knowledge, Report, Connector) with uniform interface
  - Orchestrator service + POST /tasks + WS progress
  - Aggregate + fallback logic

- P3 – Traits/LoRA
  - Add `traits_loadout` and endpoints (get/update)
  - Enforce slot/points rules; compute compatibility/effectiveness
  - Integrate with external_training_jobs for LoRA configs

- P4 – Resume & Marketplace Readiness
  - Nightly job to recompute `minion_resume`
  - Expose public resume summary; ranking leaderboard scaffold

- P5 – Hardening & Scale
  - Move registry to DB, add caching, add observability, optimize queries

Migrations & Schema Notes
- Use JSONB for new flexible fields (`model_stats`, trait_intensities, strengths/weaknesses, payloads).
- Keep current schema; add new tables/columns (no destructive changes).
- Add indexes where necessary (minion_id, created_at, user_id, status).

Open Questions / Risks
- Manual vs auto grading weights: expose admin-configurable rubric?
- Privacy of public “resume”: opt-in or defaults?
- Spirit sandboxing and rate-limits per user?
- Cross-spirit dependency management and retries.

Appendix – References
- THE_ANSWER (grading system and public resume)
- Minion Tools Orchestration Architecture (Spirits pattern)
- Traits Point System (slots, intensity, synergy)
