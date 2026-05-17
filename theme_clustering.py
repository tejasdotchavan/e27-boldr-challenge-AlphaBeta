#!/usr/bin/env python3
"""
Weekly Theme Clustering for Boldr Support Tickets
Groups novel and recurring questions by theme with trend analysis.
Run weekly to identify support patterns and escalation flags.
"""

import pandas as pd
import json
from datetime import datetime, timedelta
from collections import defaultdict
import re


def load_tickets(csv_path):
    """Load and clean ticket data."""
    df = pd.read_csv(csv_path)
    df['date_received'] = pd.to_datetime(df['date_received'])
    return df


def get_week_tickets(df, end_date=None, days_back=7):
    """Filter tickets for a specific week (7 days back from end_date)."""
    if end_date is None:
        end_date = datetime.now()
    else:
        end_date = pd.to_datetime(end_date)

    start_date = end_date - timedelta(days=days_back)
    week_df = df[(df['date_received'] >= start_date) & (df['date_received'] <= end_date)]
    return week_df.sort_values('date_received')


def cluster_by_theme(tickets_df):
    """
    Group tickets into themes based on question_type and content patterns.
    Returns dict with theme: DataFrame of tickets
    """
    themes = defaultdict(lambda: [])

    for _, row in tickets_df.iterrows():
        qtype = row['question_type']
        subject = str(row['subject']).lower()
        msg = str(row['message_body']).lower()

        # Primary grouping by question type
        if qtype == 'engraving':
            themes['Gifting & Engraving'].append(row)
        elif qtype == 'strap_compatibility':
            themes['Strap Compatibility & Customization'].append(row)
        elif qtype == 'materials_safety':
            themes['Materials Safety & Health'].append(row)
        elif qtype == 'servicing':
            themes['Servicing & Maintenance'].append(row)
        elif qtype == 'knowledge_gap':
            # Sub-cluster knowledge gaps
            if any(x in msg for x in ['vegan', 'sustain', 'carbon', 'eco', 'recycl']):
                themes['Sustainability & Ethics'].append(row)
            elif any(x in msg for x in ['arabic', 'chinese', 'mandarin', 'multi-script']):
                themes['Multi-Script Engraving'].append(row)
            elif any(x in msg for x in ['resale', 'collector', 'collaboration', 'extreme', 'altitude', 'magnetic']):
                themes['Enthusiast & Niche'].append(row)
            else:
                themes['Other Knowledge Gaps'].append(row)
        elif qtype == 'order_status':
            themes['Order & Shipping'].append(row)
        elif qtype == 'product_general':
            # Sub-cluster product inquiries
            if any(x in subject for x in ['gift', 'wrap', 'personaliz']):
                themes['Gifting Options'].append(row)
            elif any(x in subject for x in ['sustainability', 'environmental']):
                themes['Sustainability & Ethics'].append(row)
            elif any(x in subject for x in ['size', 'fit', 'wrist']):
                themes['Sizing & Fit'].append(row)
            else:
                themes['Product Information'].append(row)
        else:
            themes['Other'].append(row)

    # Convert lists to DataFrames
    result = {}
    for theme_name, rows in themes.items():
        if rows:
            result[theme_name] = pd.DataFrame(rows)

    return result


def analyze_theme(theme_name, tickets):
    """Analyze a theme for patterns and insights."""
    analysis = {
        'name': theme_name,
        'count': len(tickets),
        'kb_answerable': sum(tickets['answered_by_kb'] == 'yes'),
        'knowledge_gaps': sum(tickets['answered_by_kb'] == 'no'),
        'escalations': sum(tickets['requires_escalation'] == 'yes'),
        'personas': tickets['buyer_persona'].value_counts().to_dict(),
        'channels': tickets['channel'].value_counts().to_dict(),
        'statuses': tickets['status'].value_counts().to_dict(),
        'samples': [
            {
                'ticket_id': row['ticket_id'],
                'subject': row['subject'],
                'persona': row['buyer_persona'],
                'answered_by_kb': row['answered_by_kb'],
                'escalation': row['requires_escalation'],
            }
            for _, row in tickets.head(3).iterrows()
        ]
    }
    return analysis


def trend_flag(tickets_df, theme_name, theme_tickets):
    """Determine if theme shows escalation trends."""
    flags = []

    # Flag: High escalation rate
    esc_rate = theme_tickets['requires_escalation'].value_counts().get('yes', 0) / len(theme_tickets)
    if esc_rate > 0.3:
        flags.append(f"⚠ High escalation rate ({esc_rate:.0%})")

    # Flag: Low KB coverage
    kb_rate = theme_tickets['answered_by_kb'].value_counts().get('yes', 0) / len(theme_tickets)
    if kb_rate < 0.4:
        flags.append(f"📚 Low KB coverage ({kb_rate:.0%})")

    # Flag: Multiple personas (indicates broad appeal)
    unique_personas = theme_tickets['buyer_persona'].nunique()
    if unique_personas >= 4:
        flags.append(f"👥 Cross-persona appeal ({unique_personas} personas)")

    # Flag: Recent surge (last 2 weeks)
    recent_cutoff = datetime.now() - timedelta(days=14)
    recent_count = len(theme_tickets[theme_tickets['date_received'] >= recent_cutoff])
    total_count = len(theme_tickets)
    if recent_count > total_count * 0.5:
        flags.append(f"📈 Emerging theme ({recent_count}/{total_count} recent)")

    return flags


def generate_report(df, week_end_date=None):
    """Generate a weekly theme clustering report."""

    if week_end_date is None:
        week_end_date = datetime.now()
    else:
        week_end_date = pd.to_datetime(week_end_date)

    week_start = week_end_date - timedelta(days=7)
    week_tickets = get_week_tickets(df, end_date=week_end_date, days_back=7)

    if len(week_tickets) == 0:
        return {"error": f"No tickets found in week of {week_start.date()} to {week_end_date.date()}"}

    themes = cluster_by_theme(week_tickets)

    # Sort themes by ticket count (descending)
    sorted_themes = sorted(themes.items(), key=lambda x: len(x[1]), reverse=True)

    report = {
        'week': {
            'start': week_start.strftime('%Y-%m-%d'),
            'end': week_end_date.strftime('%Y-%m-%d'),
            'generated': datetime.now().isoformat(),
        },
        'summary': {
            'total_tickets': len(week_tickets),
            'unique_themes': len(themes),
            'kb_coverage': f"{sum(week_tickets['answered_by_kb'] == 'yes') / len(week_tickets):.0%}",
            'escalation_rate': f"{sum(week_tickets['requires_escalation'] == 'yes') / len(week_tickets):.0%}",
        },
        'themes': []
    }

    for theme_name, theme_tickets in sorted_themes:
        analysis = analyze_theme(theme_name, theme_tickets)
        flags = trend_flag(df, theme_name, theme_tickets)
        analysis['trend_flags'] = flags
        report['themes'].append(analysis)

    return report


def save_report(report, output_path):
    """Save report as JSON and markdown."""
    # JSON
    with open(output_path.replace('.md', '.json'), 'w') as f:
        json.dump(report, f, indent=2, default=str)

    # Markdown
    md_lines = []
    md_lines.append(f"# Weekly Theme Clustering Report")
    md_lines.append(f"**Week:** {report['week']['start']} → {report['week']['end']}")
    md_lines.append(f"*Generated: {report['week']['generated']}*\n")

    md_lines.append("## Summary")
    md_lines.append(f"- **Total Tickets:** {report['summary']['total_tickets']}")
    md_lines.append(f"- **Unique Themes:** {report['summary']['unique_themes']}")
    md_lines.append(f"- **KB Coverage:** {report['summary']['kb_coverage']}")
    md_lines.append(f"- **Escalation Rate:** {report['summary']['escalation_rate']}\n")

    md_lines.append("## Themes Breakdown")
    for i, theme in enumerate(report['themes'], 1):
        md_lines.append(f"\n### {i}. {theme['name']}")
        md_lines.append(f"**Tickets:** {theme['count']} | **KB-answerable:** {theme['kb_answerable']} | **Gaps:** {theme['knowledge_gaps']} | **Escalations:** {theme['escalations']}")

        if theme['trend_flags']:
            md_lines.append(f"\n**Trend Flags:**")
            for flag in theme['trend_flags']:
                md_lines.append(f"- {flag}")

        personas_str = ', '.join(f"{p} ({c})" for p, c in list(theme['personas'].items())[:3])
        md_lines.append(f"\n**Top Personas:** {personas_str}")
        md_lines.append(f"\n**Sample Tickets:**")
        for sample in theme['samples']:
            kb_status = "✓ KB" if sample['answered_by_kb'] == 'yes' else "✗ Gap"
            esc_status = " [ESCALATED]" if sample['escalation'] == 'yes' else ""
            md_lines.append(f"- **{sample['ticket_id']}:** {sample['subject']} ({sample['persona']}) {kb_status}{esc_status}")

    md_lines.append(f"\n---\n*Report generated {report['week']['generated']}*")

    with open(output_path, 'w') as f:
        f.write('\n'.join(md_lines))

    print(f"✓ Report saved:")
    print(f"  - {output_path}")
    print(f"  - {output_path.replace('.md', '.json')}")


if __name__ == '__main__':
    import sys

    csv_path = 'Boldr Data/01_customer_tickets.csv'
    week_end = sys.argv[1] if len(sys.argv) > 1 else None

    df = load_tickets(csv_path)
    report = generate_report(df, week_end_date=week_end)

    save_report(report, 'outputs/weekly_theme_clustering.md')
    print(f"\n📊 Clustering complete: {report['summary']['unique_themes']} themes identified")
