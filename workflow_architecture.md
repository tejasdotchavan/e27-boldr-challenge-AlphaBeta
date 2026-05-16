# Workflow Architecture · Boldr Intelligence Engine
**Echelon 2026 · AI Workflow Competition**
> Authored: May 16, 2026 · Last updated: May 16, 2026

---

## 1. Automation Platform

**Chosen platform: n8n (self-hosted Cloud via n8n.cloud)**

**Instance**: `tejasdotchavan.app.n8n.cloud`

n8n was chosen as the automation platform for the following reasons:

- **Visual-first canvas**: Node-based builder makes the 7-step loop easy to demonstrate to judges without needing a technical walkthrough
- **Webhook trigger**: Receives inbound customer enquiries instantly via HTTP POST
- **OpenAI-compatible node**: The built-in OpenAI node supports custom base URLs and credentials, allowing seamless integration with FPT AI Factory's OpenAI-compatible inference API — no custom HTTP node required
- **Parallel branching**: A single node output can fan out to multiple downstream nodes simultaneously (used for Step 1 → Step 1b parallel execution)
- **Native integrations**: Supports Google Sheets, Slack, Gmail, Shopify, and Notion — all relevant to Boldr's stack
- **Free tier available**: Suitable for competition demonstration without production infrastructure costs

### AI Model: Qwen3-32B via FPT AI Factory

All AI inference steps use **Qwen3-32B** served through **FPT AI Factory** (FPT AI Marketplace):

| Setting | Value |
|---------|-------|
| Provider | FPT AI Factory (FPT Cloud) |
| API Base URL | `https://mkp-api.fptcloud.com/v1` |
| Model ID | `Qwen3-32B` |
| n8n Credential | "FPT AI Factory (Qwen)" (custom OpenAI credential) |

> **Note on Qwen3-32B output**: The model produces `<think>` tags (chain-of-thought / extended thinking) before its final answer. In production, these should be stripped from responses before presenting to CS agents or customers. For competition demonstration, the full output (including `<think>` blocks) is visible in the n8n execution log.

---

## 2. The 7-Step Intelligence Loop

This is the core of the engine. Each incoming customer enquiry flows through all 7 steps in sequence. The loop is "self-improving" because Steps 5 and 6 continuously feed new knowledge back into the KB.

```
┌─────────────────────────────────────────────────────────────────┐
│                    INBOUND TICKET                               │
│         (email / chat / WhatsApp / Instagram DM)               │
│         → routed via webhook POST to n8n                       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1 — INGESTION & CLASSIFICATION                           │
│  Extract: intent, question type, order ID?                     │
│  Output: structured ticket object (JSON)                       │
│  Model: Qwen3-32B via FPT AI Factory                          │
└───────────────┬─────────────────────────────┬───────────────────┘
                │                             │ (parallel branch)
                ▼                             ▼
┌──────────────────────────┐  ┌──────────────────────────────────┐
│  STEP 1b — TAG PERSONA   │  │  STEP 2 — KNOWLEDGE BASE SEARCH  │
│  Classify buyer persona  │  │  Query KB with extracted intent  │
│  into 1 of 7 types       │  │  Return: KB chunks + confidence  │
│  Model: Qwen3-32B        │  │  Model: Qwen3-32B                │
└──────────────────────────┘  └──────────────┬───────────────────┘
                                             │
                                ┌────────────┴────────────┐
                                │                         │
                          KB match found?           No match found
                          (confidence ≥ 0.75)       (confidence < 0.75)
                                │                         │
                                ▼                         ▼
┌──────────────────────────┐  ┌──────────────────────────────────┐
│  STEP 3 — DRAFT REPLY    │  │  STEP 4 — FLAG KNOWLEDGE GAP     │
│  Generate reply using    │  │  Log unanswered question to gap  │
│  KB content + brand      │  │  log, route ticket to CS human   │
│  voice prompt            │  │  queue. No hallucination.        │
│  Queue for human review  │  └──────────────┬───────────────────┘
└──────────────┬───────────┘                 │
               │                             ▼
               │                ┌──────────────────────────────────┐
               │                │  STEP 5 — AUTO-DRAFT KB ENTRY    │
               │                │  AI drafts a proposed KB entry   │
               │                │  from the novel question.        │
               │                │  Queued for 1-click CS approval  │
               │                └──────────────┬───────────────────┘
               │                               │
               └──────────────┬────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 6 — WEEKLY THEME CLUSTERING                              │
│  Group novel questions from the week by theme                  │
│  Output: theme clusters with ticket counts + persona tags      │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 7 — MONTHLY MARKETING BRIEF                              │
│  Synthesise weekly clusters into a marketing intelligence      │
│  brief with buyer persona tags and product page gap flags      │
└─────────────────────────────────────────────────────────────────┘
```

### Step-by-Step Detail

#### Step 1 — Ingestion & Classification
- **Trigger**: Webhook POST to n8n (simulates inbound email / chat message)
- **Action**: Pass raw message to Qwen3-32B with the classification prompt (see Section 4)
- **Webhook data path**: Message body is accessed at `$('Webhook').item.json.body.message_body` — the n8n Webhook node wraps POST body under a `body` key
- **Output** (structured JSON):
  ```json
  {
    "ticket_id": "TKT-xxxx",
    "channel": "email",
    "customer_name": "...",
    "subject": "...",
    "message_body": "...",
    "question_type": "materials_safety | engraving | strap_compatibility | servicing | order_status | product_general | knowledge_gap",
    "buyer_persona": "health_conscious | gifter | enthusiast | transactional | owner_aftercare | prospect | niche_buyer",
    "contains_order_id": true,
    "order_id": "BLD-XXXXX",
    "requires_shopify_lookup": true,
    "language": "en"
  }
  ```
- **Routing rule**: If `requires_shopify_lookup = true`, skip Steps 2–3 and route directly to human CS queue with Shopify order data pre-fetched

#### Step 1b — Tag Persona (parallel branch from Step 1)
- **Trigger**: Runs in parallel with Step 2 immediately after Step 1 completes
- **Action**: Pass customer message to Qwen3-32B with the persona classification prompt
- **Input expression**: `{{ $('Webhook').item.json.body.message_body }}`
- **Output** (JSON):
  ```json
  {
    "buyer_persona": "health_conscious",
    "confidence": "high",
    "reason": "Customer is asking about BPA content in watch straps — a material safety concern"
  }
  ```
- **7 Persona Types** (derived from `01_customer_tickets.csv` — `08_buyer_personas.csv` was not present in the provided data):

  | Persona | Signal keywords |
  |---------|----------------|
  | `health_conscious` | BPA-free, nickel-free, hypoallergenic, dye safety, titanium grade, skin reactions |
  | `gifter` | Engraving, gift wrapping, personalisation, occasions, sending as a gift |
  | `enthusiast` | Watch specs, movement type, strap compatibility, limited editions, technical details |
  | `niche_buyer` | Magnetic resistance, lume safety, ISO ratings, depth ratings, niche certifications |
  | `owner_aftercare` | Servicing, repairs, water resistance re-testing, warranty, older model support |
  | `prospect` | Price matching, availability, stock, comparisons, new purchase consideration |
  | `transactional` | Shipping, customs, delivery times, express options, order logistics |

- **Validated**: Vikram Allen BPA ticket → `health_conscious` (high confidence) ✓ — confirmed in live n8n execution

#### Step 2 — Knowledge Base Search
- **Method**: Semantic vector search (embedding the customer query, searching against embedded KB chunks)
- **KB sources queried**: FAQ document, engraving rate card, servicing rate card, product reference (see Section 3 for full KB structure)
- **Output**: Top 3 matching KB chunks + a confidence score (0–1)
- **Threshold**: If top result confidence < 0.75, treat as no match → route to Step 4

#### Step 3 — Draft Reply
- **Trigger**: KB match found with confidence ≥ 0.75
- **Action**: Pass matched KB chunks + original message to Qwen3-32B with the reply drafting prompt (see Section 4)
- **Output**: Draft reply in Boldr brand voice, with a pre-filled subject line
- **Human gate**: Draft is placed in a Google Sheets "Pending Approval" queue. CS agent reviews, edits if needed, clicks Approve → triggers send via Gmail API. Nothing is auto-sent.

#### Step 4 — Flag Knowledge Gap
- **Trigger**: KB match confidence < 0.75, or `requires_shopify_lookup = true`
- **Action**: Log the ticket to the Knowledge Gap Log (Google Sheets) with: question, persona tag, channel, date, and a flag for "never asked before" vs "asked before but unanswered"
- **CS notification**: Slack or email ping to CS team with the ticket details and a direct link to reply
- **No hallucination rule**: The engine never drafts a reply if it cannot find a KB match. It only routes to humans.

#### Step 5 — Auto-Draft KB Entry
- **Trigger**: After Step 4 logs a knowledge gap AND the CS agent sends a manual reply
- **Action**: Once CS marks the ticket as resolved, the engine reads the CS reply and uses Qwen3-32B to draft a proposed KB entry in the standard format (question + answer + persona tags + source)
- **Output**: Proposed KB entry pushed to a "KB Inbox" sheet for 1-click approval by team lead
- **On approval**: Entry is added to the live KB and its embedding is indexed — the system now knows the answer for next time

#### Step 6 — Weekly Theme Clustering
- **Trigger**: Scheduled run every Monday at 9am SGT
- **Action**: Pull all knowledge gap tickets from the past 7 days, pass to Qwen3-32B with the clustering prompt
- **Output**: A cluster report listing: theme name, example questions, ticket count, dominant persona, and a "frequency trend" flag (new this week / recurring / escalating)
- **Delivered to**: CS team lead via email or Slack digest

#### Step 7 — Monthly Marketing Brief
- **Trigger**: Scheduled run on the 1st of each month
- **Action**: Pull all weekly cluster reports from the past 4 weeks, synthesise into a marketing intelligence brief
- **Output**: A structured doc with: top themes by volume, persona breakdown, product page gaps (questions customers ask that aren't answered on the website), and suggested content or FAQ additions
- **Delivered to**: Marketing team via email (or dropped into a shared Notion page)

---

## 3. Knowledge Base Structure

The KB is the engine's single source of truth. It is structured as a set of documents chunked into retrievable entries, each with metadata for filtering.

### KB Entry Format

Every KB entry follows this schema:

```
ID:           kb-001
Category:     materials_safety
Question:     Are Boldr watch straps BPA-free?
Answer:       Yes. All Boldr FKM rubber and silicone straps are 100% BPA-free...
Source:       04_faq_document.pdf — page 1
Personas:     health_conscious, prospect
Last updated: 2026-05-16
```

### KB Categories (mapped to question types)

| Category | Sources | Entry Count (est.) |
|----------|---------|-------------------|
| `materials_safety` | FAQ p.1, Product Reference | ~10 |
| `engraving` | FAQ p.2, Rate Card 03a, SOP 4.2 | ~12 |
| `strap_compatibility` | FAQ p.2–3, Product Reference, SOP 4.3 | ~10 |
| `servicing` | FAQ p.3, Rate Card 03b, SOP 4.4 | ~12 |
| `order_status` | FAQ p.4, SOP 4.5 | ~6 (process-only; no live data) |
| `product_general` | FAQ p.4, Product Reference | ~8 |
| `returns_warranty` | FAQ p.4, SOP 4.6 | ~6 |
| `gifting` | FAQ p.4 | ~4 |

### Storage & Retrieval

- **Storage**: Google Sheets (simple, auditable, easy for CS team to edit without technical skill) + OpenAI-compatible embeddings via FPT AI Factory
- **Indexing**: Each KB entry is embedded on creation/update and stored with its vector in a lightweight vector store (Supabase with pgvector, or Pinecone free tier)
- **Query flow**: Customer message → embed query → cosine similarity search → return top 3 chunks → pass to Qwen3-32B for reply drafting

### KB Maintenance Rules

- Rate cards take precedence over SOP when there is a pricing conflict (e.g. engraving 21–40 chars: use SGD 40 from rate card, not SGD 35 from SOP)
- Any entry updated after a CS approval goes through a review gate — no direct edits from the engine
- Entries are tagged with a `confidence` flag: `verified` (from official docs) vs `cs_approved` (from resolved tickets)

---

## 4. Prompt Templates

Four core prompts power the engine. All use **Qwen3-32B via FPT AI Factory**.

---

### Prompt 1 — Ingestion & Classification

```
You are a customer service classifier for Boldr Supply Co., a premium titanium watch brand based in Singapore.

Your job is to analyse an inbound customer enquiry and extract structured data from it.

**Customer message:**
{{message_body}}

**Instructions:**
1. Identify the primary question type from this list:
   - materials_safety (BPA, nickel, hypoallergenic, lume, certifications)
   - engraving (characters, pricing, fonts, corrections, turnaround)
   - strap_compatibility (lug width, quick-release, swimming, leather care)
   - servicing (battery, full service, regulation, international)
   - order_status (tracking, shipping, wrong item, cancellation, refund)
   - product_general (warranty, return policy, model comparison, gifting, bulk)
   - knowledge_gap (if the question does not clearly fit any of the above)

2. Identify the buyer persona:
   - health_conscious (safety, materials, certifications)
   - gifter (engraving, gift wrapping, occasions)
   - enthusiast (specs, compatibility, limited editions)
   - transactional (order, shipping, tracking, refund)
   - owner_aftercare (servicing, maintenance, repairs)
   - prospect (comparing models, pricing, return policy)
   - niche_buyer (unusual or highly specific questions)

3. Check if the message contains a Boldr order ID (format: BLD-XXXXX). If yes, extract it.

4. Determine if this ticket requires a live Shopify lookup (true if it's about a specific order, tracking, refund, or wrong item).

**Output JSON only — no explanation:**
{
  "question_type": "...",
  "buyer_persona": "...",
  "contains_order_id": true/false,
  "order_id": "BLD-XXXXX or null",
  "requires_shopify_lookup": true/false,
  "summary": "One sentence summary of what the customer is asking"
}
```

---

### Prompt 1b — Persona Tagger (Step 1b system prompt, live in n8n)

```
You are a buyer persona classifier for Boldr Supply Co., a premium titanium watch brand.

Classify the customer message into exactly ONE of these 7 personas based on their primary concern:

- health_conscious: Asks about material safety, BPA-free, nickel-free, hypoallergenic, dye safety, titanium grade, skin reactions
- gifter: Asks about engraving, gift wrapping, personalisation, occasions, sending as a gift
- enthusiast: Asks about watch specs, movement type, strap compatibility, limited editions, technical details, wrist size fit
- niche_buyer: Asks about edge-case technical specs — magnetic resistance, lume safety, ISO ratings, depth ratings, niche certifications
- owner_aftercare: Asks about servicing, repairs, water resistance re-testing, warranty, older model support
- prospect: Asks about price matching, availability, stock, comparisons, new purchase consideration
- transactional: Asks about shipping, customs, delivery times, express options, order logistics

Respond with ONLY a valid JSON object in this exact format, no other text:
{"buyer_persona": "<persona_label>", "confidence": "<high|medium|low>", "reason": "<one sentence>"}
```

---

### Prompt 2 — KB Search Relevance Check

```
You are a relevance assessor for a customer service knowledge base.

**Customer query:**
{{customer_summary}}

**KB entry:**
{{kb_entry_text}}

Rate how well this KB entry answers the customer query on a scale of 0.0 to 1.0.
- 1.0 = Directly and completely answers the question
- 0.75 = Mostly answers the question, minor gaps
- 0.5 = Partially relevant
- 0.25 = Tangentially related
- 0.0 = Not relevant

Output a single JSON object:
{
  "score": 0.0–1.0,
  "reason": "One sentence explanation"
}
```

---

### Prompt 3 — Draft Reply

```
You are a customer service agent for Boldr Supply Co., a premium titanium watch brand.

**Brand voice:**
- Friendly but not overly casual — we are a premium brand
- Direct — answer the question clearly, do not pad with filler
- Helpful — if you cannot fully answer, say so and offer next steps
- Never make promises about timelines or pricing that are not in the KB
- Open with: "Hi [Name], thanks for reaching out! Happy to help with that."
- Avoid: "Great question!", "Dear Sir/Madam"

**Customer name:** {{customer_name}}
**Customer message:** {{message_body}}
**Relevant KB content:** {{kb_chunks}}

**Instructions:**
Write a reply that:
1. Directly answers the customer's question using only the KB content provided
2. Matches the brand voice guidelines above
3. If the KB content covers only part of the question, answer what you can and note that the rest will be followed up by a team member
4. Do NOT invent information not present in the KB content

Output the reply as plain text, ready to send. No preamble.
```

---

### Prompt 4 — KB Entry Drafter

```
You are a knowledge base editor for Boldr Supply Co.

A customer asked a question that was not in our KB. A CS agent has now answered it manually.

**Original customer question:** {{customer_question}}
**CS agent's reply:** {{cs_reply}}

Draft a new KB entry in this exact format:

Category: [materials_safety / engraving / strap_compatibility / servicing / order_status / product_general / returns_warranty / gifting / knowledge_gap]
Question: [Rephrase the customer's question as a clear, generic FAQ question]
Answer: [Extract the answer from the CS reply. Write in second person ("You can...", "Yes, Boldr..."). Be concise but complete.]
Personas: [List applicable personas: health_conscious, gifter, enthusiast, transactional, owner_aftercare, prospect, niche_buyer]
Source: CS reply — ticket {{ticket_id}} — {{date}}

Output the entry only, no explanation.
```

---

## 5. Human Approval Gate Flow

No reply is ever sent automatically. Every AI-drafted reply goes through a mandatory human review step.

### Gate Design

```
AI drafts reply
       │
       ▼
Reply added to "Pending Approval" tab in Google Sheets
  - Columns: Ticket ID | Customer | Draft Reply | KB Sources Used | Confidence Score | Approve | Edit | Reject
       │
       ▼
CS agent receives Slack/email notification:
  "New draft ready for review — [Customer Name] asked about [summary]"
       │
       ├─── Agent clicks APPROVE → Gmail API sends reply → ticket marked resolved
       │
       ├─── Agent clicks EDIT → Opens draft in a simple form → edits text → clicks Send
       │
       └─── Agent clicks REJECT → Draft discarded → ticket routed to manual queue
                                                    → engine logs this as a KB improvement opportunity
```

### Why This Matters for the Competition

The brief explicitly warns against auto-sending. The gate is not just a safety feature — it is a trust-building mechanism. Over time, as the KB improves, the approval rate (approvals / total drafts) becomes a measurable KPI showing the system getting more accurate. This is the "self-improving" story for the judges.

### Gate KPIs to Track

| Metric | Target | What it shows |
|--------|--------|---------------|
| Draft approval rate | >80% after 30 days | KB quality improving |
| Time-to-approve | < 2 min per ticket | CS productivity gain |
| Tickets auto-triaged | >90% classified correctly | Classifier accuracy |
| Knowledge gap rate | Decreasing week-on-week | Self-improvement working |
| KB entries added per week | 3–5 initially, then declining | System reaching maturity |

---

## 6. Current Build Status

> For Ayush and any team members joining Phase 7 — here is what is live vs. pending as of May 16, 2026.

### Live in n8n (built and validated)

| Node | Status | Notes |
|------|--------|-------|
| Webhook trigger | ✅ Live | Receives POST, data at `body.message_body` |
| Step 1: Ingestion & Classification | ✅ Live | Qwen3-32B, outputs structured ticket JSON |
| Step 1b: Tag Persona | ✅ Live | Parallel branch from Step 1; 7 personas; validated on BPA ticket |
| Step 3: Draft Reply | ✅ Live | Qwen3-32B, brand voice prompt, TRUE branch |
| Step 4: Flag Knowledge Gap | ✅ Live | Edit Fields node, logs ticket_id / question / persona / channel / status |

### Pending / Not yet built

| Node | Status | Notes |
|------|--------|-------|
| Step 2: KB Search | 🟡 Partial | IF node routing done; vector search not yet wired (KB not indexed) |
| Step 5: Auto-draft KB Entry | 🔴 Not started | Needs Step 4 completion trigger + CS reply webhook |
| Step 6: Weekly Theme Clustering | 🔴 Not started | Scheduled trigger, pull gap log, cluster with Qwen3-32B |
| Step 7: Monthly Marketing Brief | 🔴 Not started | Ayush taking this — see tasks.md Phase 7 |

### Key technical notes for Phase 7 / presentation work

- **n8n instance**: `tejasdotchavan.app.n8n.cloud` — credentials shared separately
- **AI model**: Qwen3-32B via FPT AI Factory (`https://mkp-api.fptcloud.com/v1`), OpenAI-compatible API
- **Qwen3-32B quirk**: Model outputs `<think>...</think>` chain-of-thought tags before the final answer. Strip these before showing output in any demo or slide
- **Persona data**: `08_buyer_personas.csv` was not in the provided Boldr Data folder. All 7 personas were derived from the `buyer_persona` column in `01_customer_tickets.csv`
- **Missing source files**: `07_knowledge_gap_log.csv`, `08_buyer_personas.csv`, `09_xxx` — noted in `data_observations.md`
- **Human gate**: Nothing auto-sends. All drafted replies go to a Google Sheets approval queue first

---

*End of Architecture Document — last updated May 16, 2026*
