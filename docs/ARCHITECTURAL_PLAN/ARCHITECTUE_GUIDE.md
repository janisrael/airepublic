# AI Republic Architecture and Implementation Guide

This document summarizes the architecture, Minion levels, helpers, skill unlocks, models, ports, and first implementation checklist for AI Republic.

# VERY IMPORTANT: Read this conversation please.

https://chatgpt.com/share/68e0b24f-bfd0-8009-88c6-51154b49f462
---

## 1. System Overview

* **Minion (Client-side)**: Lightweight LLM/Agent that runs locally, performs intent filtering, triggers local tools, connects to Orchestrator via WebSocket.
* **Orchestrator (Server-side)**: Central decision-making LLM, delegates tasks to helpers based on Minion level and helper availability, manages concurrency and fallback to RAG.
* **Helpers (Server-side)**: Specialized or general-purpose executors, some with optional LLMs for reasoning or content generation.
* **WebSocket**: Handles async communication, progress updates, completion, and file links.
* **File Storage**: Temporary server storage for generated files; users download via HTTP link.

---

## 2. Minion Levels & Skills

| Level          | Skills / Tools                           | Accessible Helpers                                  |
| -------------- | ---------------------------------------- | --------------------------------------------------- |
| Level 1        | Basic intent filtering                   | Knowledge Helper                                    |
| Level 2        | Local file analysis, PDF parsing         | Knowledge, Report Helpers                           |
| Level 3        | OS tool control, screenshots, automation | WebSearch, Task, Analytics Helpers                  |
| Level 4        | Advanced automation, multi-step tasks    | Task, Report, Creative, SEO, Social Media Helpers   |
| Ranking Unlock | Exclusive / Premium tools                | SEO Helper, Social Media Helper, Advanced Analytics |

---

## 3. Helper Specializations

| Category                    | Helper Name         | Purpose / Tools                                             | Recommended Model                        | Unlock Criteria            |
| --------------------------- | ------------------- | ----------------------------------------------------------- | ---------------------------------------- | -------------------------- |
| Knowledge / Research        | Knowledge Helper    | Answering questions, RAG, FAQ search                        | LLaMA 3-7B / GPT-4-turbo                 | Level 1+                   |
| Productivity / Automation   | Task Helper         | OS automation, file management, scheduling, ClickUp         | LLaMA 3-7B / optional GPT-4-turbo        | Level 3+                   |
| Content / Report Generation | Report Helper       | Generate reports, summaries, PDF creation, content drafting | LLaMA 3-13B / GPT-4-turbo                | Level 2+                   |
| Web / Search                | WebSearch Helper    | Web scraping, info retrieval, SEO research                  | No LLM required; optional small LLM      | Level 3+                   |
| Marketing / SEO             | SEO Helper          | Keyword analysis, site audits, content suggestions          | LLaMA 3-7B / GPT-4-turbo                 | Level 4+ or Ranking unlock |
| Social Media                | Social Media Helper | Post generation, scheduling, engagement tracking            | LLaMA 3-7B / GPT-4-turbo                 | Level 4+ or Ranking unlock |
| Analytics / BI              | Analytics Helper    | Data parsing, dashboards, visualization, KPI tracking       | LLaMA 3-13B / GPT-4-turbo                | Level 3+                   |
| Finance / Accounting        | Finance Helper      | Reports, bookkeeping, invoices, PayPal/Square integration   | LLaMA 3-13B / GPT-4-turbo                | Level 3+                   |
| Creative / Design           | Creative Helper     | Image prompts, storyboarding, media generation              | DALL·E / Stable Diffusion / optional LLM | Level 4+                   |

---

## 4. Recommended Models by Component

| Component        | Recommended Model                            | Notes                                                             |
| ---------------- | -------------------------------------------- | ----------------------------------------------------------------- |
| Minion           | LLaMA 3-7B / MPT-7B / GPT-4-turbo API        | Lightweight, local reasoning, first-pass filtering, tool triggers |
| Orchestrator     | GPT-4-turbo / LLaMA 3-13B / MPT-30B-Instruct | Central routing, complex reasoning, multi-user requests           |
| Knowledge Helper | LLaMA 3-7B (optional)                        | RAG / knowledge lookup                                            |
| Report Helper    | LLaMA 3-13B / GPT-4-turbo                    | Content generation, PDF reports                                   |
| Task Helper      | LLaMA 3-7B or GPT-4-turbo                    | Local automation, optional reasoning                              |
| WebSearch Helper | No LLM required                              | API / scraping tasks                                              |

---

## 5. Ports and Concurrency

| Helper                   | Base Port | Concurrency Notes                                                          |
| ------------------------ | --------- | -------------------------------------------------------------------------- |
| Knowledge Helper         | 6000+     | Single instance can serve multiple users; scale horizontally if overloaded |
| WebSearch Helper         | 7000+     | Same as above                                                              |
| Report / Content Helper  | 8000+     | File generation, may need async queue for heavy tasks                      |
| Task / Automation Helper | 9000+     | Can scale horizontally, handles OS tasks locally if triggered by Minion    |

---

## 6. WebSocket & File Flow

1. Minion → Orchestrator: send task request
2. Orchestrator → Helper: delegate task
3. Helper → server storage: save result file
4. Orchestrator → Minion: send file link via WebSocket
5. User clicks link → HTTP GET → download file

**Notes:**

* Files are **not sent over WebSocket**, only links.
* WebSocket handles async progress updates and completion notifications.

---

## 7. First Implementation Checklist

### Minion

* [ ] Lightweight LLM setup
* [ ] Intent filtering / task classification
* [ ] Local tool triggers (PDF, screenshot)
* [ ] WebSocket connection & async updates

### Orchestrator

* [ ] LLM setup for decision-making
* [ ] Service registry for helpers (port, category, concurrency)
* [ ] Task delegation based on Minion level
* [ ] Fallback to RAG / LangChain if no helper available
* [ ] Send updates / file links via WebSocket

### Helpers

* [ ] Knowledge Helper (RAG / FAQ)
* [ ] Report / Content Helper (optional LLM)
* [ ] Task / Automation Helper (scripts / optional LLM)
* [ ] WebSearch Helper (API / fetch)
* [ ] Stateless design, concurrency handling
* [ ] File generation → server storage → HTTP link

### Testing

* [ ] Single Minion → Orchestrator → Helper flow
* [ ] Multiple Minions / concurrent requests
* [ ] Async file delivery via WebSocket + HTTP download
* [ ] Fallback AI / RAG tasks

---

## 8. Gamified Skill Unlocks

* Minion Level determines **which helpers/tools are accessible**
* Orchestrator enforces access
* Ranking / achievements can unlock premium helpers (SEO, Social Media, Advanced Analytics)
* Progressive skill unlocks:

  * Level 1: Knowledge
  * Level 2: Report / Content
  * Level 3: Task / Automation / Analytics / WebSearch
  * Level 4: Creative, Marketing, Social Media
  * Ranking unlocks: premium / exclusive helpers

---

This document can be used as a **reference for your Cursor IDE AI** to guide implementation and setup of AI Republic.
