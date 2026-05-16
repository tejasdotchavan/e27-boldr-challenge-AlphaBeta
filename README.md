# Boldr · Self-Improving Customer Intelligence Engine
**Echelon 2026 · AI Workflow Competition**

> Turn every customer question into product & marketing intelligence.

---

## The Challenge

Build an AI workflow that transforms Boldr's reactive customer support into a self-improving intelligence engine — one that answers questions, identifies knowledge gaps, updates its own knowledge base, and generates marketing signals automatically.

---

## Folder Structure

```
.
├── Boldr Data/          # Sample data provided by organisers
│   ├── 01_customer_tickets.csv
│   ├── 03a_rate_card_engraving.csv
│   ├── 03b_rate_card_servicing.csv
│   ├── 04_faq_document.pdf
│   ├── 05a_SOP.docx
│   └── 05b_product_reference.docx
├── workflow/            # n8n / Make.com workflow exports + configs
├── outputs/             # Generated outputs (KB entries, marketing briefs, persona tags)
├── docs/                # Notes, research, planning
├── Challenge Brief_BOLDR.pdf
├── checklist.md
└── README.md
```

---

## The Intelligence Loop

1. **Ingest enquiry** — receive email, extract intent and context
2. **Search Knowledge Base** — query FAQ, product specs, rate cards
3. **Draft reply** (if answerable) — brand voice, queued for human approval
4. **Flag gap** (if not answerable) — route to CS staff, no hallucination
5. **Auto-draft KB entry** — 1-click approval format once gap is resolved
6. **Theme clustering** — weekly grouping of novel questions by theme
7. **Marketing brief** — monthly output of unaddressed customer signals with persona tags

---

## Buyer Personas

| Persona | Trigger Signals | Marketing Action |
|---|---|---|
| Health-Conscious Buyer | BPA-free, nickel-free, hypoallergenic | "BPA-Free Straps" product badge |
| Gifter | Engraving, gift wrap, anniversary | Seasonal campaigns |
| Enthusiast / Collector | Grade 5 titanium, Miyota, limited editions | Collector content |
| Active / Outdoor Buyer | Water resistance, shock, FKM strap | Adventure lifestyle content |
| Sustainability Advocate | Vegan straps, carbon offset, eco packaging | Develop vegan strap angle |

---

## Bonus: External Sentiment Benchmarking

Cross-validate internal ticket themes against external watch forum and Reddit sentiment across 3+ themes to determine whether signals are Boldr-specific or market-wide.

---

## Team

- Tejas Chavan
- *(add teammate)*
