# Task List · Boldr Intelligence Engine
**Echelon 2026 · AI Workflow Competition**

> Status: 🔴 Not started · 🟡 In progress · 🟢 Done

---

## Phase 1 — Setup & Understanding

| Status | Task | Owner | Notes |
|--------|------|-------|-------|
| 🟢 | Read and understand the challenge brief | | |
| 🟢 | Create checklist from brief | | |
| 🟢 | Set up GitHub repo | | |
| 🟢 | Read all 6 sample data files thoroughly | | `Boldr Data/` folder |
| 🟢 | Map out data schema across files | | See `data_observations.md` |
| 🟢 | Identify any data gaps vs. brief's file list | | 3 files missing: 07, 08, 09 — noted in `data_observations.md` |

---

## Phase 2 — Workflow Architecture

| Status | Task | Owner | Notes |
|--------|------|-------|-------|
| 🟢 | Choose automation platform | | Make.com — see `workflow_architecture.md` |
| 🟢 | Design the 7-step intelligence loop (diagram) | | See `workflow_architecture.md` §2 |
| 🟢 | Define Knowledge Base structure | | See `workflow_architecture.md` §3 |
| 🟢 | Define prompt templates | | 4 prompts defined — see `workflow_architecture.md` §4 |
| 🟢 | Design human approval gate flow | | Google Sheets gate + KPIs — see `workflow_architecture.md` §5 |

---

## Phase 3 — Core Build

| Status | Task | Owner | Notes |
|--------|------|-------|-------|
| 🟢 | Step 1: Email ingestion node | | Webhook trigger + OpenAI GPT-4o classifier — built in n8n |
| 🟡 | Step 2: Knowledge Base search node | | IF node routing done; vector search to be wired once KB is indexed |
| 🟢 | Step 3: Draft reply (if answerable) | | OpenAI node with brand voice prompt on TRUE branch |
| 🟢 | Step 4: Flag knowledge gap (if not answerable) | | Edit Fields node on FALSE branch — logs ticket_id, question, buyer_persona, channel, status |
| 🔴 | Step 5: Auto-draft KB entry | | 1-click approval format |
| 🔴 | Step 6: Weekly theme clustering | | Group novel questions by theme |
| 🔴 | Step 7: Monthly marketing brief output | | With buyer persona tags |

---

## Phase 4 — Persona Tagging

| Status | Task | Owner | Notes |
|--------|------|-------|-------|
| 🟢 | Build persona classification logic | | `08_buyer_personas.csv` missing — derived 7 personas from `01_customer_tickets.csv` |
| 🟢 | Tag: health_conscious | | BPA-free, dye safety, nickel-free, titanium grade — built in Step 1b |
| 🟢 | Tag: gifter | | Engraving, gift wrap, occasions — built in Step 1b |
| 🟢 | Tag: enthusiast | | Watch specs, movement, strap compatibility, limited editions — built in Step 1b |
| 🟢 | Tag: niche_buyer | | Magnetic resistance, lume safety, ISO/depth ratings — built in Step 1b |
| 🟢 | Tag: owner_aftercare | | Servicing, repairs, warranty, older models — built in Step 1b |
| 🟢 | Tag: prospect | | Price matching, availability, stock — built in Step 1b |
| 🟢 | Tag: transactional | | Shipping, customs, express delivery — built in Step 1b |
| 🟢 | Test tagging against live ticket | | Vikram Allen BPA ticket → `health_conscious` (high confidence) ✓ — validated in n8n |

---

## Phase 5 — Outputs

| Status | Task | Owner | Notes |
|--------|------|-------|-------|
| 🔴 | Produce sample drafted replies | | Show 3–5 examples |
| 🔴 | Produce knowledge gap log | | Match format of `07_knowledge_gap_log.csv` |
| 🔴 | Produce weekly theme clustering report | | |
| 🔴 | Produce monthly marketing brief | | With persona tags + product page gaps |

---

## Phase 6 — Bonus: External Sentiment Benchmarking

| Status | Task | Owner | Notes |
|--------|------|-------|-------|
| 🔴 | Identify 2+ external sources | | Watch forums, Reddit, competitor reviews |
| 🔴 | Justify source selection | | Why each captures Boldr's buyer signals |
| 🔴 | Cross-validate on 3+ themes | | Internal tickets vs. external sentiment |
| 🔴 | Theme 1: BPA-free / health safety | | |
| 🔴 | Theme 2: Sustainability / vegan straps | | |
| 🔴 | Theme 3: Nickel allergy / titanium safety | | |
| 🔴 | Write actionable insight per theme | | Boldr-specific vs. market-wide? |

---

## Phase 7 — Presentation & Submission

| Status | Task | Owner | Notes |
|--------|------|-------|-------|
| 🔴 | Record workflow demo | | Walk through the self-improving loop end-to-end |
| 🔴 | Write up solution narrative | | Why this architecture, how it scales |
| 🔴 | Prepare slide deck / one-pager | | For judges |
| 🔴 | Final review against brief checklist | | Cross-check `checklist.md` |
| 🔴 | Submit | | |
