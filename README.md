# Boldr · Self-Improving Customer Intelligence Engine
**Echelon 2026 · AI Workflow Competition**

> Turn every customer question into product and marketing intelligence — automatically.

---

## The Challenge

Build an AI workflow that transforms Boldr's reactive customer support into a self-improving intelligence engine — one that answers questions, identifies knowledge gaps, routes to human CS when needed, and generates marketing signals automatically.

---

## What We Built

The **Boldr Intelligence Engine** is a four-workflow automation system built on n8n that:

- **Answers known questions instantly** via a single LLM call grounded in Boldr's full knowledge base
- **Routes edge cases to CS** — low-confidence queries are held, answered by a human, then redrafted in brand voice before reaching the customer
- **Adds a CS approval gate** — even high-confidence answers go to a CS agent for approval before being sent
- **Extracts marketing intelligence** from every ticket — buyer persona, classification, and marketing signal — rolling up into weekly theme clusters and monthly briefs

See [`architecture.md`](./architecture.md) for the full system diagram.

---

## Live Demo

The system runs on a Telegram bot. Every customer message triggers the full pipeline in real time:

1. Customer sends a question via Telegram
2. LLM classifies, matches KB, and drafts a brand-voiced reply
3. CS receives the draft for approval via Telegram
4. On approval, the reply is sent to the customer
5. On rejection, the ticket enters the CS queue for a manual answer

---

## System Architecture

```
Customer (Telegram)
        |
        v
  Intelligence Engine (n8n WF1)
        |
        v
  LLM — FPT AI Factory / Qwen
  (classification + KB match + draft reply + persona + marketing signal)
        |
   _____|_____
  |           |
High conf.  Low conf.
  |           |
  v           v
CS approval  CS queue
(Telegram    (Google Sheets)
 command)         |
  |               v
  |         CS fills answer
  |               |
  |               v
  |         WF2: Redraft + Send
  |
  v
Customer receives reply
        |
        v
  Google Sheets (cs_queue, kb_log)
        |
   _____|_____
  |           |
  v           v
WF3 (Sun)   WF4 (1st of month)
Weekly      Monthly
themes      marketing brief
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| Automation / orchestration | n8n Cloud |
| LLM inference | FPT AI Factory — Qwen reasoning model |
| Customer interface | Telegram Bot API |
| Data layer | Google Sheets (4 tabs) |
| Knowledge base | 41 structured KB entries (JSON) |

---

## Workflows

### WF1 — Intelligence Engine
**Trigger:** Telegram message from customer

Every inbound message is processed by a single LLM call returning structured JSON:

```json
{
  "classification": "engraving",
  "buyer_persona": "Gift Buyer",
  "kb_match": "yes",
  "confidence_score": 0.95,
  "draft_reply": "...",
  "summary": "...",
  "marketing_signal": "...",
  "marketing_flag": "yes"
}
```

High confidence replies go to CS for Telegram approval (`/approve_ID` or `/reject_ID`). Low confidence tickets are logged to the CS queue for a human answer.

### WF2 — CS Handoff Loop
**Trigger:** Schedule (every 5 min) + Telegram approval commands

Polls `cs_queue` for answered rows, redrafts the reply in brand voice, sends to the customer, and logs to `kb_log`. The approval handler catches `/approve` and `/reject` commands from CS and routes accordingly.

### WF3 — Weekly Theme Clustering
**Trigger:** Every Sunday at 11pm

Reads all tickets from the past 7 days, extracts top 5 themes, the biggest pain point, marketing signals, and KB gaps. Writes to `weekly_themes` tab.

### WF4 — Monthly Marketing Brief
**Trigger:** 1st of each month at 8am

Synthesises 4 weeks of theme data into a structured marketing brief: executive summary, top concerns, content gaps, campaign angle suggestions, and recommended KB updates. Sent to the team via Telegram.

---

## Knowledge Base

41 structured entries in `workflow/kb_entries.json` covering:

- Engraving pricing and policies (caseback, buckle, CJK/Arabic, custom logo, rush, corrections)
- Servicing tiers (battery, regulation, full service standard/premium, crystal, polish, water resistance)
- Product specs (titanium grades, lume variants, strap materials, water resistance ratings)
- Order and shipping policies (returns, customs, gift wrapping, corporate orders)
- CS operations (tone guidelines, escalation rules, amendment policy)

All 41 entries are embedded directly in the LLM system prompt — no vector database needed, fully explainable.

---

## Buyer Personas

| Persona | Trigger Signals | Marketing Angle |
|---|---|---|
| Gift Buyer | Engraving, gift wrap, anniversary | Seasonal gifting campaigns |
| Health-Conscious Buyer | BPA-free, nickel-free, hypoallergenic | "Safe for sensitive skin" badge |
| Enthusiast / Collector | Grade 5 titanium, movement specs, limited editions | Collector content and drops |
| Active / Outdoor Buyer | Water resistance, shock, rubber strap | Adventure lifestyle content |
| Sustainability Advocate | Carbon offset, eco packaging, vegan straps | Develop sustainability angle |

---

## Google Sheet Structure

| Tab | Purpose |
|---|---|
| `cs_queue` | All tickets — pending, pending_approval, answered |
| `kb_log` | CS-answered questions and their redrafted replies |
| `weekly_themes` | LLM-generated weekly theme clusters |
| `marketing_briefs` | Monthly marketing briefs |

---

## Folder Structure

```
.
├── README.md
├── architecture.md              # Full system architecture diagram
├── n8n.md                       # Node-by-node n8n build spec
├── Boldr Data/                  # Source data provided by organisers
│   ├── 01_customer_tickets.csv
│   ├── 03a_rate_card_engraving.csv
│   ├── 03b_rate_card_servicing.csv
│   ├── 04_faq_document.pdf
│   ├── 05a_SOP.docx
│   └── 05b_product_reference.docx
├── workflow/
│   └── kb_entries.json          # 41 knowledge base entries
└── e27-boldr-challenge-AlphaBeta/
    └── phase5_outputs/          # Sample generated outputs
```

---

## Setup Notes

All credentials (Telegram bot token, FPT API key, Google Sheets OAuth) are stored as n8n credentials and are not committed to this repository.

To run this system you need:

- An n8n Cloud account (or self-hosted n8n)
- A Telegram bot token (via @BotFather)
- An FPT AI Factory API key with access to the Qwen model
- A Google account with a Sheet structured per the tab layout above

See `n8n.md` for the complete node-by-node build spec for all four workflows.

---

## Team

- Tejas Chavan — tejasdotchavan@gmail.com
- *(add teammate)*
