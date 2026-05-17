# Theme Clustering & Marketing Brief Setup

This guide explains how to run the **weekly theme clustering** and **monthly marketing intelligence brief** as part of the Boldr self-improving intelligence engine.

---

## Quick Start

### Prerequisites
```bash
pip install pandas
```

### Generate Reports
```bash
# Weekly theme clustering (for a specific week)
python3 theme_clustering.py "2026-05-12"

# Monthly marketing brief (for a specific month)
python3 marketing_brief.py "2026-05-12"

# Or use today's date (default)
python3 theme_clustering.py
python3 marketing_brief.py
```

Outputs are saved to `outputs/`:
- `weekly_theme_clustering.md` + `.json`
- `monthly_marketing_brief.md` + `.json`

---

## What Each Script Does

### 1. `theme_clustering.py` — Weekly Intelligence

**Purpose:** Group customer questions by theme, identify escalation patterns, and flag emerging trends.

**Output:**
- Breakdown of 10+ themes (e.g., "Gifting & Engraving", "Strap Compatibility", "Sustainability & Ethics")
- Per-theme metrics: KB coverage, escalation rate, top personas
- Trend flags: high escalation, low KB coverage, cross-persona appeal, emerging themes
- Sample tickets for each theme

**When to Run:** Weekly (e.g., Monday morning to review last week's questions)

**Who Uses It:** 
- **CS Team:** Identify which knowledge gaps are becoming patterns
- **Product:** See which features customers are asking about
- **Marketing:** Spot emerging customer segments and interests

**Example Output:**
```markdown
### Sustainability & Ethics
- Tickets: 1 | KB-answerable: 0 | Escalations: 1
- Trend Flags:
  - ⚠ High escalation rate (100%)
  - 📚 Low KB coverage (0%)
  - 📈 Emerging theme (1/1 recent)
```

---

### 2. `marketing_brief.py` — Monthly Intelligence

**Purpose:** Surface unmet customer demand and product-page gaps for marketing & product strategy.

**Output:**
- **Unmet Demand:** Top 10 knowledge gaps (customer questions NOT in FAQ/product pages)
- **Recurring Questions:** Topics asked 2+ times (= product page gap)
- **Persona Breakdown:** How each buyer segment is asking, KB coverage per persona
- **Content Recommendations:** Specific actions (ADD to FAQ, EXPAND product page, IMPROVE KB)

**When to Run:** Monthly (e.g., first Friday of the month for last 30 days)

**Who Uses It:**
- **Marketing Lead:** Content calendar, landing page copy, seasonal campaigns
- **Product Manager:** Feature requests, product page gaps, roadmap signals
- **CS Manager:** Identify high-frequency gaps to address in Q&A sessions

**Example Output:**
```markdown
### Unmet Customer Demand (Knowledge Gaps)
1. Engraving in Arabic script
   - Persona: niche_buyer | Channel: email
   - Ticket: TKT-1070

### Content Recommendations
[HIGH] ADD to FAQ: Multi-script engraving options
- Asked by 2+ personas
- Top priority for international gifting segment
```

---

## Integration Points

### With n8n Workflow
1. **Step 6 — Weekly Clustering:** Add an n8n node that runs `theme_clustering.py` every Monday
2. **Step 7 — Monthly Brief:** Add an n8n node that runs `marketing_brief.py` on the 1st of each month
3. Route outputs to Slack channels:
   - `#cs-theme-report` (weekly)
   - `#marketing-intelligence` (monthly)

### With Google Sheets
1. Create a Google Sheet: "Theme Clustering History"
2. Export `weekly_theme_clustering.json` and append to the sheet weekly
3. Create another sheet: "Marketing Briefs"
4. Archive monthly briefs for trend analysis

### Manual Workflow (Current)
1. Run scripts on schedule (cron job or reminder)
2. Review outputs in `outputs/` folder
3. Paste key findings into Slack or team docs
4. Update product roadmap / FAQ based on recommendations

---

## Customization

### Add Custom Themes
Edit `cluster_by_theme()` in `theme_clustering.py`:
```python
elif qtype == 'my_new_type':
    themes['My Custom Theme'].append(row)
    # Or sub-cluster based on keywords:
    if any(x in msg for x in ['keyword1', 'keyword2']):
        themes['Sub-Theme A'].append(row)
```

### Change Trend Flag Thresholds
Edit the thresholds in `trend_flag()`:
```python
if esc_rate > 0.3:  # Change to > 0.5 for stricter alerts
    flags.append(f"⚠ High escalation rate ({esc_rate:.0%})")
```

### Adjust Recurring Question Frequency
Edit `identify_content_gaps()` in `marketing_brief.py`:
```python
if data['count'] >= 2:  # Change to >= 3 for stricter filtering
    content_gaps.append({...})
```

---

## Data Format

### Input: `01_customer_tickets.csv`
Required columns:
- `ticket_id`: Unique ID (TKT-1001, etc.)
- `date_received`: ISO datetime
- `question_type`: One of: engraving, strap_compatibility, materials_safety, servicing, knowledge_gap, order_status, product_general
- `subject`: Short question title
- `message_body`: Full customer message
- `answered_by_kb`: "yes" or "no"
- `requires_escalation`: "yes" or "no"
- `buyer_persona`: One of: health_conscious, gifter, enthusiast, niche_buyer, owner_aftercare, prospect, transactional

### Output: JSON + Markdown
Both formats are generated for easy viewing and programmatic access.

---

## Automation Recipe

### Option A: Cron Job (Linux/Mac)
```bash
# Add to crontab -e

# Every Monday 9am: run theme clustering
0 9 * * 1 cd /path/to/boldr && python3 theme_clustering.py >> logs/weekly.log 2>&1

# 1st of month 9am: run marketing brief
0 9 1 * * cd /path/to/boldr && python3 marketing_brief.py >> logs/monthly.log 2>&1
```

### Option B: n8n Workflow
1. Create a new workflow node with HTTP request to execute Python script
2. Set schedule: Weekly (Monday 9am) and Monthly (1st, 9am)
3. Send outputs to Slack webhook
4. Archive JSON to Google Drive for historical tracking

### Option C: GitHub Actions
Create `.github/workflows/theme-clustering.yml`:
```yaml
name: Weekly Theme Clustering
on:
  schedule:
    - cron: '0 9 * * 1'
jobs:
  cluster:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: pip install pandas
      - run: python3 theme_clustering.py
      - uses: actions/upload-artifact@v2
        with:
          name: theme-report
          path: outputs/
```

---

## Troubleshooting

**Q: "No tickets found in week"**  
A: Check date format. Use ISO format: "2026-05-12"

**Q: Low recurring question count**  
A: This is normal for a small dataset. Add more tickets or lower the threshold in the script.

**Q: Personas don't show up in recommendations**  
A: Ensure `buyer_persona` column matches expected values. Run report with sample data first.

---

## Next Steps

1. ✅ Run both scripts with sample data (done)
2. **Wire into n8n:** Add Python execution nodes after Step 5 (KB entry approval)
3. **Set automation:** Schedule weekly/monthly runs via cron or n8n
4. **Create dashboards:** Use JSON outputs to build Slack briefings or Google Sheets reports
5. **Iterate on themes:** After 2-3 weeks of data, refine theme definitions based on CS feedback

---

## Files Reference

| File | Purpose |
|------|---------|
| `theme_clustering.py` | Weekly theme grouping & trend detection |
| `marketing_brief.py` | Monthly unmet demand & content gaps |
| `outputs/weekly_theme_clustering.md` | Human-readable weekly report |
| `outputs/weekly_theme_clustering.json` | Machine-readable for automation |
| `outputs/monthly_marketing_brief.md` | Human-readable monthly brief |
| `outputs/monthly_marketing_brief.json` | Machine-readable for automation |

---

**Questions? Check the main [README.md](README.md) or the intelligence loop diagram in the submission deck.**
