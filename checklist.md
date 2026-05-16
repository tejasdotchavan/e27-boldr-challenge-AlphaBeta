# BOLDR Challenge Checklist
**Echelon 2026 · AI Workflow Competition**

---

## 1. Understand the Brief

- [ ] Read the full challenge brief (`Challenge Brief_BOLDR.pdf`)
- [ ] Review all 9 sample data files in `Boldr Data/`
- [ ] Understand the self-improving intelligence loop diagram (Page 3)

---

## 2. Review Sample Data Files

- [ ] `01_customer_tickets.csv` — primary input; understand schema (subject, body, theme, persona tag, answerable flag)
- [ ] `02_product_specs.json` — product catalogue (SKUs, materials, lug widths, water resistance, strap compatibility)
- [ ] `03a_rate_card_engraving.csv` — engraving pricing, character limits, font options, turnaround
- [ ] `03b_rate_card_servicing.csv` — servicing tiers, pricing, turnaround per model
- [ ] `04_faq_document.pdf` — 28 existing FAQ entries (primary Knowledge Base)
- [ ] `05_decision_tree.json` — 16 routing rules (trigger conditions, YES/NO branches, escalation flags)
- [ ] `06_shipping_reconciliation.csv` — reference only (bonus context)
- [ ] `07_knowledge_gap_log.csv` — target OUTPUT format for gap detection
- [ ] `08_buyer_personas.csv` — 5 personas with trigger keywords and marketing opportunities
- [ ] `09_external_sentiment_data.csv` — 4 external forum/review sources (bonus input)

---

## 3. Core Intelligence Loop (7 Steps)

- [ ] **Step 1 — Ingest enquiry:** Receive customer email, extract question intent and context
- [ ] **Step 2 — Search Knowledge Base:** Query FAQ, product specs, rate cards for a relevant answer
- [ ] **Step 3 — Draft reply (if answerable):** Write reply in Boldr's brand voice; queue for human approval before sending (do NOT auto-send)
- [ ] **Step 4 — Flag gap (if not answerable):** Flag as knowledge gap, route to CS staff with context; do NOT hallucinate an answer
- [ ] **Step 5 — Auto-draft Knowledge Base entry:** Once a human resolves the gap, auto-draft a new KB entry in Boldr's format for 1-click approval
- [ ] **Step 6 — Theme clustering:** Weekly grouping of novel questions by theme (materials, sustainability, sizing, gifting, etc.)
- [ ] **Step 7 — Marketing brief:** Monthly output — "What customers are asking that is not on your product pages" with buyer persona tags

---

## 4. Buyer Persona Tagging

Tag every enquiry against one of the five personas:

- [ ] **Health-Conscious Buyer** — BPA-free, nickel-free, hypoallergenic, EU REACH, safe for kids → marketing action: "BPA-Free Straps" product badge
- [ ] **Gifter** — engraving, gift wrap, birthday, anniversary, turnaround time → marketing action: seasonal campaigns (Valentine's, Father's Day)
- [ ] **Enthusiast / Collector** — Grade 5 titanium, Miyota movement, limited editions → marketing action: collector content, specs & craftsmanship
- [ ] **Active / Outdoor Buyer** — water resistance, shock, trail running, FKM rubber strap → marketing action: adventure lifestyle content
- [ ] **Sustainability Advocate** — vegan straps, carbon offset shipping, eco packaging → marketing action: develop vegan strap angle

---

## 5. Outputs to Produce

- [ ] Drafted email replies (queued for human approval, not auto-sent)
- [ ] Knowledge gap flags with context for CS staff
- [ ] Auto-drafted Knowledge Base entries (1-click approval format)
- [ ] Weekly theme clustering report
- [ ] Monthly marketing intelligence brief (with persona tags, product page gaps)

---

## 6. Bonus Challenge — External Sentiment Benchmarking

- [ ] Identify **2+ external sources** relevant to Boldr's customer base (e.g. watch forums, Reddit communities, competitor reviews); justify why each source captures the right buyer signals
- [ ] **Compare on 3+ themes** — show how internal ticket signals align or diverge from external market sentiment (cross-validate using `09_external_sentiment_data.csv`)
- [ ] Suggested themes to validate: BPA-free straps, titanium safety/nickel allergy, sustainability/vegan straps, corporate gifting, water resistance
- [ ] **Actionable insight per theme:** Answer "Is this a Boldr-specific gap or a market-wide concern? What should Boldr do about it?"

---

## 7. Workflow Architecture

- [ ] Choose an automation platform (n8n, Make.com, or similar open-source/low-code tool preferred)
- [ ] Ensure the workflow is **well-architected, explainable, and ownable** by Boldr's 3-person CS team
- [ ] Document the workflow clearly so judges can follow the logic
- [ ] Ensure no hallucinated answers are ever sent to customers
- [ ] Human approval gates are in place before any reply is sent and before any KB entry is published

---

## 8. Final Checks Before Submission

- [ ] All 7 steps of the intelligence loop are functional (or clearly demonstrated)
- [ ] All 5 buyer personas are being tagged correctly against ticket data
- [ ] Knowledge Base is being queried and updated in the loop
- [ ] Gap detection is producing entries in the format of `07_knowledge_gap_log.csv`
- [ ] Persona tagging output matches the format of `08_buyer_personas.csv`
- [ ] Marketing brief output is generated (monthly cadence)
- [ ] Bonus: External benchmarking covers 3+ themes with actionable insights
- [ ] Presentation/demo is clear and judges can understand the self-improving loop end-to-end
