# Data Observations · Boldr Intelligence Engine
**Echelon 2026 · AI Workflow Competition**
> Analysed by: Claude | Date: May 16, 2026

---

## Files Reviewed

| File | Type | Description |
|------|------|-------------|
| `01_customer_tickets.csv` | CSV | 70 real customer support tickets |
| `03a_rate_card_engraving.csv` | CSV | Engraving pricing tiers |
| `03b_rate_card_servicing.csv` | CSV | Watch servicing pricing tiers |
| `04_faq_document.pdf` | PDF | 4-page public-facing FAQ |
| `05a_SOP.docx` | DOCX | Internal CS handling procedures |
| `05b_product_reference.docx` | DOCX | CS product quick-reference sheet |

**Missing files** (brief mentions 9 files, only 6 present): files `02_x`, `06_x`, `07_knowledge_gap_log.csv`, `08_buyer_personas.csv`, and `09_x` are absent. This is a notable gap — the buyer personas CSV is referenced heavily in the task list for Phase 4 but does not exist in the data folder.

---

## 01 — Customer Tickets (`01_customer_tickets.csv`)

### Overview
- **70 tickets** spanning Nov 15, 2025 to May 12, 2026 (~6 months)
- **Ticket IDs**: TKT-1001 to TKT-1070 (not sequential by date — numbered in random order relative to date)
- **Channels**: email, chat, whatsapp, instagram_dm (no phone support)

### Question Type Breakdown
| Question Type | Count | Notes |
|--------------|-------|-------|
| `order_status` | 13 | High escalation rate — needs Shopify access |
| `engraving` | 12 | Most are answerable from rate card |
| `strap_compatibility` | 11 | Mostly answerable via FAQ |
| `materials_safety` | 11 | Health-conscious persona dominant here |
| `product_general` | 10 | Mix of prospect and gifter queries |
| `servicing` | 9 | Mostly answerable via rate card |
| `knowledge_gap` | 10 | Labelled as unanswerable from existing KB |

### Buyer Persona Breakdown
| Persona | Description | Dominant Question Type |
|---------|-------------|----------------------|
| `health_conscious` | BPA, nickel, hypoallergenic, EU certs | materials_safety |
| `enthusiast` | Strap specs, lug widths, interchangeability | strap_compatibility |
| `gifter` | Engraving, font, turnaround, correction | engraving |
| `transactional` | Order status, tracking, refunds, cancellations | order_status |
| `owner_aftercare` | Servicing, regulation, polishing | servicing |
| `prospect` | Product differences, warranty, return policy | product_general |
| `niche_buyer` | MRI safety, altitude, resale value, vegan straps | knowledge_gap |

### Ticket Status Summary
| Status | Count |
|--------|-------|
| `resolved` | ~34 |
| `pending_reply` | ~17 |
| `open` | ~13 |
| `escalated` | ~6 |

### KB Coverage Analysis
- `answered_by_kb = yes` means existing FAQ/rate cards can answer the query
- `answered_by_kb = no` combined with `requires_escalation = yes` = true knowledge gaps that need human handling
- There are tickets where `answered_by_kb = yes` but status is still `open` or `pending_reply` — these are prime candidates for auto-drafted replies in the intelligence engine

### Knowledge Gap Tickets (answered_by_kb = no)
These 19 tickets represent genuine gaps in the KB — questions the current FAQ/docs cannot answer:

| Ticket | Topic | Persona |
|--------|-------|---------|
| TKT-1046 | MRI / magnetic field resistance | niche_buyer |
| TKT-1002 | Express shipping cost | transactional |
| TKT-1005 | Customs duties (UK) | transactional |
| TKT-1007 | Discount code not working | transactional |
| TKT-1009 | Order not received | transactional |
| TKT-1021 | Luminous material safety (Super-LumiNova) | niche_buyer |
| TKT-1029 | Wrong item received | transactional |
| TKT-1040 | Order stuck in customs | transactional |
| TKT-1043 | Refund status | transactional |
| TKT-1045 | Extreme sports / shock resistance rating | niche_buyer |
| TKT-1052 | Resale value of titanium watches | niche_buyer |
| TKT-1056 | Tracking number not updating | transactional |
| TKT-1057 | Change delivery address | transactional |
| TKT-1065 | Altitude performance at 5,000m | niche_buyer |
| TKT-1013 | Carbon-neutral shipping | niche_buyer |
| TKT-1028 | Strap recycling programme | niche_buyer |
| TKT-1036 | Vegan-friendly materials (synthetic leather) | niche_buyer |
| TKT-1055 | Cancel order before shipping | transactional |
| TKT-1070 | Engraving in Arabic script | niche_buyer |
| TKT-1014 | Collab with independent watchmakers | niche_buyer |
| TKT-1066 | Safety certifications for children | health_conscious |

**Pattern**: Most knowledge gaps fall into two buckets — (1) operational/order queries that need live Shopify data, and (2) niche product questions not covered in the current FAQ.

### Data Quality Issues — Order ID Mismatches
Several tickets have a different order ID in the `order_id` field vs. what the customer quotes in their message body. This is likely a data entry error (agent logged wrong order ID). These need to be flagged:

| Ticket | order_id field | Mentioned in message |
|--------|---------------|----------------------|
| TKT-1009 | BLD-76540 | BLD-93810 |
| TKT-1029 | BLD-36772 | BLD-46048 |
| TKT-1040 | BLD-13248 | BLD-42098 |
| TKT-1043 | BLD-56025 | BLD-23434 |
| TKT-1055 | BLD-65724 | BLD-39256 |
| TKT-1057 | BLD-68446 | BLD-28289 |

---

## 03a — Engraving Rate Card

### Pricing Summary
| Service | Price (SGD) | Notes |
|---------|-------------|-------|
| Caseback — up to 20 chars | 25 | Latin/Roman script only |
| Caseback — 21 to 40 chars | 40 | Latin/Roman script only |
| Caseback — per char beyond 40 | 1.50 | Max 60 chars total |
| CJK characters (per char) | 3.00 | Up to 15 chars |
| Arabic script (per char) | 3.00 | Up to 15 chars |
| Strap buckle — up to 10 chars | 15 | Metal buckle only, not rubber/NATO |
| Logo/symbol (custom vector) | 60 | Must supply .ai or .svg; approval required |
| Multi-line (2 lines) | 35 | Up to 30 chars total across both lines |
| Rush (same-day processing) | 20 surcharge | Before 12pm SGT; subject to availability |
| Engraving correction (within 1hr) | Free | After 1hr: SGD 15 |

### Observations
- Arabic engraving is supported (SGD 3/char, up to 15 chars) — directly relevant to TKT-1070
- Logo engraving at SGD 60 requires a vector file, meaning the CS agent cannot confirm it without a team review step
- The correction window (1 hour, free) is very short — this creates urgency for customers like TKT-1020

---

## 03b — Servicing Rate Card

### Pricing Summary
| Service | Price (SGD) | Turnaround |
|---------|-------------|-----------|
| Battery Replacement | 35 | 3–5 days |
| Regulation Service | 85 | 7–10 days |
| Full Service — Standard | 160 | 14–21 days |
| Full Service — Premium | 220 | 14–21 days |
| Crystal Replacement | 65 | 5–7 days |
| Case & Bracelet Polish | 45 | 3–5 days |
| Strap/Bracelet Replacement (fitting) | 10 | 1 day |
| Water Resistance Re-test | 20 | 1–2 days |
| International Service (surcharge) | 25 | +7–14 days |
| Service Warranty Extension (12 months) | 30 | N/A |

### Observations
- Premium Full Service at SGD 220 includes a 12-month warranty — this is an upsell opportunity
- International service adds both cost (SGD 25) and significant time (+7–14 days) — relevant for TKT-1059 (Australian customer)
- Regulation service (SGD 85) specifically targets the "losing X seconds/day" complaint type (e.g. TKT-1062)
- No explicit pricing for older/discontinued model servicing — SOP says to check with team first

---

## 04 — FAQ Document (4 pages)

### Topics Covered
- **Materials & Safety**: BPA-free straps, Grade 5 Ti (Expedition) vs Grade 2 Ti (Journey), EU REACH + RoHS compliance, Super-LumiNova lume, nickel content
- **Engraving**: Character limits, pricing overview, correction policy, logo engraving, strap buckle engraving, turnaround
- **Strap Compatibility**: 20mm lug width (universal across models), quick-release mechanism, NATO compatibility, cross-model interchangeability, leather care
- **Watch Servicing**: Pricing, what's included in Full Service, regulation for timekeeping drift, service frequency recommendation, international shipping process, warranty
- **Orders & Shipping**: Delivery timelines, international shipping, customs disclaimer, return policy
- **General**: 2-year warranty scope, gift wrapping (SGD 8), Expedition vs Journey differences, bulk/corporate pricing

### Key Facts Extracted
- Expedition: 40mm, Grade 5 Ti, 100m water resistance, SGD 485
- Journey: 38mm, Grade 2 Ti, 50m water resistance, SGD 395
- Both models use automatic movements
- Returns: 14 days, unworn, original packaging; engraved items non-returnable
- Warranty: 2 years on movement, does NOT cover physical/water damage or strap wear
- Corporate pricing: available for 10+ units at corporate@boldr.co
- Gift wrapping: SGD 8, premium box with ribbon and personalised card

### Gaps in the FAQ (not covered)
- MRI / magnetic field resistance
- Altitude / barometric performance
- Shock resistance ratings for extreme sports
- Carbon-neutral shipping options
- Strap recycling programme
- Vegan certification details for synthetic leather
- Resale value comparison
- Collaboration with independent watchmakers
- Specific font options for engraving
- Express shipping cost (mentioned but not priced)

---

## 05a — Customer Service SOP

### Key Process Insights
- **3 CS staff** sharing one Gmail inbox — entirely manual, no automation or triage
- Reference workflow: read email → check reference docs → draft reply → send → mark resolved
- New questions go into a **New Questions Log** (Google Sheets, Google Drive) — this is the predecessor to the KB entry step in the intelligence engine
- Escalation triggers: angry customers, chargebacks, significant warranty claims, refund outstanding >10 days, corporate orders >5 units, media enquiries

### Brand Voice Guidelines
- Friendly but not overly casual
- Direct — answer clearly, no filler
- Never promise what you cannot guarantee
- Suggested opener: "Hi [Name], thanks for reaching out! Happy to help with that."
- Avoid: "Great question!", "Dear Sir/Madam", unverified timeline promises

### Critical Discrepancy Found
The SOP (Section 4.2) states engraving for 21–40 characters costs **SGD 35**. The rate card (`03a_rate_card_engraving.csv`) states the same tier costs **SGD 40**. This is a direct pricing conflict. CS agents following the SOP would quote the wrong price. The rate card should be treated as the authoritative source — the SOP needs updating.

---

## 05b — Product Quick Reference

### Current Models
| Model | Price (SGD) | SKU | Notes |
|-------|-------------|-----|-------|
| Expedition Titanium | 485 | BLD-EXP-TI-40 | Active use, 100m WR |
| Journey Titanium | 395 | BLD-JRN-TI-38 | Dress-casual, 50m WR |
| Expedition Ember (Limited Edition) | 595 | BLD-EXP-TI-40-LE | **SOLD OUT** — waitlist only |

### Material Notes
- FKM rubber + Nylon NATO straps: BPA-free and nickel-free
- Leather straps: BPA-free, but **NOT hypoallergenic** — sensitive skin customers may react
- Mesh bracelet: 316L stainless steel — trace nickel present (relevant for nickel allergy queries)

---

## Cross-File Observations & Design Implications

### What the Intelligence Engine Needs to Know

1. **Two-tier ticket handling**: Tickets where `answered_by_kb = yes` can be auto-drafted from the KB. Tickets where `answered_by_kb = no` must be routed to a human — no hallucination. This maps directly to Steps 3 and 4 of the 7-step loop.

2. **Order-status tickets always need Shopify**: Any `order_status` query requires live data. The engine should detect order numbers (pattern: `BLD-XXXXX`) and flag them for human handling or Shopify API lookup — do not attempt to answer from KB.

3. **Persona tagging is already in the data**: The `buyer_persona` column exists in the tickets CSV. This is ground-truth labelling we can use to train or validate the classifier — a strong starting point.

4. **The New Questions Log already exists manually**: The SOP describes CS agents logging unanswerable questions to a Google Sheet. The intelligence engine should replace this with an automated KB entry draft (Step 5 of the loop), following the same structure the CS team already uses.

5. **Pricing consistency is critical**: The SOP/rate card discrepancy (SGD 35 vs SGD 40 for 21–40 char engraving) is the kind of error the intelligence engine could perpetuate at scale if it uses the SOP as the KB source. The rate card should take precedence for pricing.

6. **Multi-language engraving is supported but nuanced**: CJK and Arabic are explicitly priced in the rate card. Arabic engraving (TKT-1070) was flagged as `answered_by_kb = no` — this is incorrect, the answer exists in the rate card. Suggests the current CS team doesn't realise Arabic is covered.

7. **Health-conscious persona has the most "partially answered" queries**: Materials & safety questions are largely covered in the FAQ (BPA, nickel, lume, EU certs) but customers still phrase them in ways that confuse agents (e.g. "is this safe for my 10-year-old?" vs. "is the lume safe?"). The KB entry should include these phrasings as synonyms/variants.

8. **Escalation ≠ knowledge gap**: Some escalated tickets (`requires_escalation = yes`) are about order operations (wrong item, address change) rather than missing knowledge. These should route to a human operational queue, not a KB-drafting flow.

---

## Suggested KB Structure (based on data)

Based on question type distribution, the KB should be structured around these primary intents:

1. **Materials & Safety** — BPA, nickel, hypoallergenic, lume, EU certs, titanium grade
2. **Engraving** — pricing tiers, character limits, CJK/Arabic, logos, corrections, turnaround
3. **Strap Compatibility** — lug width, quick-release, model interchangeability, swimming recommendations, leather care
4. **Watch Servicing** — pricing tiers, turnaround, what's included, international process, warranty
5. **Orders & Shipping** — tracking, international duties, express options, delivery timelines
6. **Returns & Warranty** — policy, exceptions (engraved items), warranty scope
7. **Product Comparison** — Expedition vs Journey, model specs, pricing, limited editions
8. **Gifting** — gift wrapping, personalisation options, corporate/bulk orders
9. **Knowledge Gaps (unresolved)** — MRI safety, altitude, shock ratings, vegan certs, strap recycling, carbon shipping

---

*End of observations — last updated May 16, 2026*
