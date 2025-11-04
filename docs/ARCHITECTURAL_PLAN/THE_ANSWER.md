# AI Republic Architecture and Implementation Guide

This document summarizes the architecture, Minion levels, helpers, skill unlocks, models, ports, and first implementation checklist for AI Republic.

---

## 1. System Overview

- **Minion (Client-side)**: Lightweight LLM/Agent that runs locally, performs intent filtering, triggers local tools, connects to Orchestrator via WebSocket.
- **Orchestrator (Server-side)**: Central decision-making LLM, delegates tasks to helpers based on Minion level and helper availability, manages concurrency and fallback to RAG.
- **Helpers (Server-side)**: Specialized or general-purpose executors, some with optional LLMs for reasoning or content generation.
- **WebSocket**: Handles async communication, progress updates, completion, and file links.
- **File Storage**: Temporary server storage for generated files; users download via HTTP link.

---

## 2. Minion Levels & Skills

| Level | Skills / Tools | Accessible Helpers |
|-------|----------------|------------------|
| Level 1 | Basic intent filtering | Knowledge Helper |
| Level 2 | Local file analysis, PDF parsing | Knowledge, Report Helpers |
| Level 3 | OS tool control, screenshots, automation | WebSearch, Task, Analytics Helpers |
| Level 4 | Advanced automation, multi-step tasks | Task, Report, Creative, SEO, Social Media Helpers |
| Ranking Unlock | Exclusive / Premium tools | SEO Helper, Social Media Helper, Advanced Analytics |

---

## 3. Helper Specializations

| Category | Helper Name | Purpose / Tools | Recommended Model | Unlock Criteria |
|----------|------------|----------------|-----------------|----------------|
| Knowledge / Research | Knowledge Helper | Answering questions, RAG, FAQ search | LLaMA 3-7B / GPT-4-turbo | Level 1+ |
| Productivity / Automation | Task Helper | OS automation, file management, scheduling, ClickUp | LLaMA 3-7B / optional GPT-4-turbo | Level 3+ |
| Content / Report Generation | Report Helper | Generate reports, summaries, PDF creation, content drafting | LLaMA 3-13B / GPT-4-turbo | Level 2+ |
| Web / Search | WebSearch Helper | Web scraping, info retrieval, SEO research | No LLM required; optional small LLM | Level 3+ |
| Marketing / SEO | SEO Helper | Keyword analysis, site audits, content suggestions | LLaMA 3-7B / GPT-4-turbo | Level 4+ or Ranking unlock |
| Social Media | Social Media Helper | Post generation, scheduling, engagement tracking | LLaMA 3-7B / GPT-4-turbo | Level 4+ or Ranking unlock |
| Analytics / BI | Analytics Helper | Data parsing, dashboards, visualization, KPI tracking | LLaMA 3-13B / GPT-4-turbo | Level 3+ |
| Finance / Accounting | Finance Helper | Reports, bookkeeping, invoices, PayPal/Square integration | LLaMA 3-13B / GPT-4-turbo | Level 3+ |
| Creative / Design | Creative Helper | Image prompts, storyboarding, media generation | DALL·E / Stable Diffusion / optional LLM | Level 4+ |

---

## 4. Recommended Models by Component

| Component | Recommended Model | Notes |
|-----------|-----------------|------|
| Minion | LLaMA 3-7B / MPT-7B / GPT-4-turbo API | Lightweight, local reasoning, first-pass filtering, tool triggers |
| Orchestrator | GPT-4-turbo / LLaMA 3-13B / MPT-30B-Instruct | Central routing, complex reasoning, multi-user requests |
| Knowledge Helper | LLaMA 3-7B (optional) | RAG / knowledge lookup |
| Report Helper | LLaMA 3-13B / GPT-4-turbo | Content generation, PDF reports |
| Task Helper | LLaMA 3-7B or GPT-4-turbo | Local automation, optional reasoning |
| WebSearch Helper | No LLM required | API / scraping tasks |

---

## 5. Ports and Concurrency

| Helper | Base Port | Concurrency Notes |
|--------|-----------|-----------------|
| Knowledge Helper | 6000+ | Single instance can serve multiple users; scale horizontally if overloaded |
| WebSearch Helper | 7000+ | Same as above |
| Report / Content Helper | 8000+ | File generation, may need async queue for heavy tasks |
| Task / Automation Helper | 9000+ | Can scale horizontally, handles OS tasks locally if triggered by Minion |

---

## 6. WebSocket & File Flow

1. Minion → Orchestrator: send task request
2. Orchestrator → Helper: delegate task
3. Helper → server storage: save result file
4. Orchestrator → Minion: send file link via WebSocket
5. User clicks link → HTTP GET → download file

**Notes:**
- Files are **not sent over WebSocket**, only links.
- WebSocket handles async progress updates and completion notifications.

---

## 7. First Implementation Checklist

### Minion
- [ ] Lightweight LLM setup
- [ ] Intent filtering / task classification
- [ ] Local tool triggers (PDF, screenshot)
- [ ] WebSocket connection & async updates

### Orchestrator
- [ ] LLM setup for decision-making
- [ ] Service registry for helpers (port, category, concurrency)
- [ ] Task delegation based on Minion level
- [ ] Fallback to RAG / LangChain if no helper available
- [ ] Send updates / file links via WebSocket

### Helpers
- [ ] Knowledge Helper (RAG / FAQ)
- [ ] Report / Content Helper (optional LLM)
- [ ] Task / Automation Helper (scripts / optional LLM)
- [ ] WebSearch Helper (API / fetch)
- [ ] Stateless design, concurrency handling
- [ ] File generation → server storage → HTTP link

### Testing
- [ ] Single Minion → Orchestrator → Helper flow
- [ ] Multiple Minions / concurrent requests
- [ ] Async file delivery via WebSocket + HTTP download
- [ ] Fallback AI / RAG tasks

---

## 8. Gamified Skill Unlocks

- Minion Level determines **which helpers/tools are accessible**
- Orchestrator enforces access
- Ranking / achievements can unlock premium helpers (SEO, Social Media, Advanced Analytics)
- Progressive skill unlocks:
  - Level 1: Knowledge
  - Level 2: Report / Content
  - Level 3: Task / Automation / Analytics / WebSearch
  - Level 4: Creative, Marketing, Social Media
  - Ranking unlocks: premium / exclusive helpers

---

This document can be used as a **reference for your Cursor IDE AI** to guide implementation and setup of AI Republic.



yes. i need a grading system of a minion.. not just + points if it responses. it should be a whole task grading. that gives accuracy of the task given. record how many times the user ask revision base from instruction. that solid grading system will be like there resume on public.. bec it can level up and user can upgrade a lot of data and still end up dumb bec its not upgrading according to success rate
ChatGPT said:

Absolutely — you’re thinking about a true performance-based grading system rather than just activity points. We can make it task-centric, skill-aware, and outcome-driven. Here’s a framework for a Minion grading system:

🔹 Minion Grading / Evaluation System
1. Task-Based Accuracy

Metric: Compare Minion output against expected results.

Example:

Task: Generate a report from a dataset

Measure: Completeness, correctness, formatting, adherence to instructions

Scoring: 0–100% per task

2. Revision / Instruction Adherence

Metric: Track how many times the user requests revisions based on instructions.

Lower revision requests → higher score

Scoring: Weighted penalty for repeated revisions

3. Task Complexity / Weight

Not all tasks are equal — assign difficulty multipliers:

Simple (knowledge lookup) → ×1

Medium (PDF report generation) → ×2

Complex (automation workflow) → ×3

4. Skill Usage & Unlock

Evaluate if Minion used appropriate helper or skill for task:

Correct skill → bonus points

Wrong or unnecessary skill → penalty

5. Time Efficiency

Measure how quickly Minion completes tasks relative to complexity.

Scoring: Faster completions with high accuracy → bonus; slow but correct → partial credit

6. Task Success Rate Over Time

Track success per skill category (Knowledge, Report, Automation, SEO, etc.)

Generates a profile of strengths & weaknesses

Can be used to recommend skill training or fine-tuning

7. Aggregate Score → Resume / Public Profile

Overall Minion Rating: Weighted average of all task scores + efficiency + skill adherence

Public Resume: Shows

Level

Skill strengths

Task success rate

Number of tasks completed

Revision ratio

Ranking among other Minions

8. Optional: Gamification & Marketplace Impact

High-grade Minions → unlock premium helpers, more advanced skills, higher marketplace value

Low-grade Minions → require training / revision to improve, even if user has lots of data

This creates a “merit-based” AI reputation system, where accumulating experience without success doesn’t falsely inflate value. Users can track improvement, skills, and real performance, making it meaningful for leveling, ranking, and marketplace trades.