#!/usr/bin/env python3
"""
Monthly Marketing Intelligence Brief for Boldr
Surfaces unmet customer demand and product-page gaps with persona tags.
Run monthly to feed content strategy and product roadmap.
"""

import pandas as pd
import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter


def load_tickets(csv_path):
    """Load and clean ticket data."""
    df = pd.read_csv(csv_path)
    df['date_received'] = pd.to_datetime(df['date_received'])
    return df


def get_month_tickets(df, month_end=None):
    """Filter tickets for a specific month (30 days back from month_end)."""
    if month_end is None:
        month_end = datetime.now()
    else:
        month_end = pd.to_datetime(month_end)

    month_start = month_end - timedelta(days=30)
    month_df = df[(df['date_received'] >= month_start) & (df['date_received'] <= month_end)]
    return month_df.sort_values('date_received')


def identify_gaps(tickets_df):
    """
    Find unmet customer needs: tickets not answered by KB + escalations.
    Returns list of gap insights with context.
    """
    gaps = []

    # Filter: Knowledge gaps (answered_by_kb = no, usually escalated)
    gap_tickets = tickets_df[
        (tickets_df['answered_by_kb'] == 'no') |
        (tickets_df['answered_by_kb'].isna())
    ]

    for _, row in gap_tickets.iterrows():
        gaps.append({
            'ticket_id': row['ticket_id'],
            'date': row['date_received'].strftime('%Y-%m-%d'),
            'question': row['subject'],
            'message': row['message_body'][:150],  # First 150 chars
            'persona': row['buyer_persona'],
            'channel': row['channel'],
            'category': row['question_type'],
            'escalated': row['requires_escalation'] == 'yes',
        })

    return gaps


def identify_content_gaps(tickets_df):
    """
    Find product-page gaps: frequently asked questions that should be surfaced.
    Maps to: FAQ improvements, product page copy, knowledge base entries.
    """
    content_gaps = []

    # Group by subject pattern
    subjects = defaultdict(lambda: {'count': 0, 'personas': Counter(), 'samples': []})

    for _, row in tickets_df.iterrows():
        subject = row['subject']
        personas = row['buyer_persona']

        # Normalize subject to identify similar questions
        key = subject.lower()

        subjects[key]['count'] += 1
        subjects[key]['personas'][personas] += 1
        subjects[key]['samples'].append(row['ticket_id'])

    # Filter: Topics mentioned 2+ times (recurring) or escalated knowledge gaps
    for subject, data in subjects.items():
        if data['count'] >= 2:
            top_personas = data['personas'].most_common(2)
            content_gaps.append({
                'topic': subject,
                'frequency': data['count'],
                'top_personas': [p[0] for p in top_personas],
                'sample_tickets': data['samples'][:3],
                'type': 'FAQ',  # Default to FAQ; could be productpage, KB, or SOP
            })

    # Sort by frequency
    content_gaps.sort(key=lambda x: x['frequency'], reverse=True)

    return content_gaps


def persona_breakdown(tickets_df):
    """Analyze which personas are asking what."""
    breakdown = {}

    for persona in tickets_df['buyer_persona'].unique():
        persona_tickets = tickets_df[tickets_df['buyer_persona'] == persona]
        breakdown[persona] = {
            'count': len(persona_tickets),
            'top_questions': persona_tickets['question_type'].value_counts().to_dict(),
            'kb_coverage': f"{sum(persona_tickets['answered_by_kb'] == 'yes') / len(persona_tickets):.0%}",
            'escalation_rate': f"{sum(persona_tickets['requires_escalation'] == 'yes') / len(persona_tickets):.0%}",
            'top_subjects': persona_tickets['subject'].value_counts().head(3).to_dict(),
        }

    # Sort by ticket count
    return dict(sorted(breakdown.items(), key=lambda x: x[1]['count'], reverse=True))


def generate_marketing_recommendations(gaps, content_gaps, personas_breakdown):
    """
    Generate actionable content recommendations based on identified gaps.
    Output: Specific changes to product pages, FAQ, or campaigns.
    """
    recommendations = []

    # Recommendation 1: FAQ/Product page gaps
    for gap in content_gaps[:5]:  # Top 5
        topic = gap['topic']
        freq = gap['frequency']
        personas = ', '.join(gap['top_personas'])

        if freq >= 3:
            action = 'ADD to FAQ'
        elif freq == 2:
            action = 'EXPAND FAQ or Product Page'
        else:
            action = 'MONITOR'

        recommendations.append({
            'action': action,
            'topic': topic,
            'urgency': 'HIGH' if freq >= 4 else 'MEDIUM',
            'personas_affected': gap['top_personas'],
            'why': f"Asked {freq}× by {personas}. Current KB coverage appears low.",
            'suggested_placement': 'FAQ / Product Page / Pricing Page',
            'example_tickets': gap['sample_tickets'],
        })

    # Recommendation 2: Persona-specific campaigns
    for persona, data in list(personas_breakdown.items())[:3]:
        coverage = int(data['kb_coverage'].rstrip('%'))
        if coverage < 70:
            recommendations.append({
                'action': 'IMPROVE KB COVERAGE',
                'topic': f"{persona.replace('_', ' ').title()} segment",
                'urgency': 'HIGH' if coverage < 50 else 'MEDIUM',
                'personas_affected': [persona],
                'why': f"{persona.replace('_', ' ').title()} has {coverage}% KB coverage. High escalation rate suggests unmet needs.",
                'suggested_placement': 'Landing page, FAQ, targeted content',
                'example_tickets': [],
            })

    return recommendations


def generate_report(df, month_end_date=None):
    """Generate a monthly marketing intelligence brief."""

    if month_end_date is None:
        month_end_date = datetime.now()
    else:
        month_end_date = pd.to_datetime(month_end_date)

    month_start = month_end_date - timedelta(days=30)
    month_tickets = get_month_tickets(df, month_end=month_end_date)

    if len(month_tickets) == 0:
        return {"error": f"No tickets found in 30 days ending {month_end_date.date()}"}

    gaps = identify_gaps(month_tickets)
    content_gaps = identify_content_gaps(month_tickets)
    personas_breakdown = persona_breakdown(month_tickets)

    recommendations = generate_marketing_recommendations(gaps, content_gaps, personas_breakdown)

    report = {
        'month': {
            'start': month_start.strftime('%Y-%m-%d'),
            'end': month_end_date.strftime('%Y-%m-%d'),
            'generated': datetime.now().isoformat(),
        },
        'executive_summary': {
            'total_tickets': len(month_tickets),
            'unmet_demand_signals': len(gaps),
            'recurring_questions': len(content_gaps),
            'content_recommendations': len(recommendations),
            'kb_gap_rate': f"{len(gaps) / len(month_tickets):.0%}",
        },
        'unmet_demand': gaps[:10],  # Top 10 knowledge gaps
        'recurring_questions': content_gaps[:10],  # Top 10 recurring topics
        'persona_breakdown': personas_breakdown,
        'recommendations': recommendations,
    }

    return report


def save_report(report, output_path):
    """Save report as JSON and markdown."""
    # JSON
    with open(output_path.replace('.md', '.json'), 'w') as f:
        json.dump(report, f, indent=2, default=str)

    # Markdown
    md_lines = []
    md_lines.append(f"# Monthly Marketing Intelligence Brief")
    md_lines.append(f"**Period:** {report['month']['start']} → {report['month']['end']}")
    md_lines.append(f"*Generated: {report['month']['generated']}*\n")

    # Executive Summary
    md_lines.append("## Executive Summary")
    md_lines.append(f"- **Tickets Analyzed:** {report['executive_summary']['total_tickets']}")
    md_lines.append(f"- **Unmet Demand Signals:** {report['executive_summary']['unmet_demand_signals']}")
    md_lines.append(f"- **Recurring Questions:** {report['executive_summary']['recurring_questions']}")
    md_lines.append(f"- **KB Gap Rate:** {report['executive_summary']['kb_gap_rate']}")
    md_lines.append(f"- **Recommendations:** {report['executive_summary']['content_recommendations']}\n")

    # Unmet Demand
    md_lines.append("## Unmet Customer Demand (Knowledge Gaps)")
    md_lines.append("These questions are **not answered by the FAQ or product pages**. They represent growth opportunities.\n")
    for i, gap in enumerate(report['unmet_demand'][:5], 1):
        md_lines.append(f"### {i}. {gap['question']}")
        md_lines.append(f"- **Persona:** {gap['persona']} | **Channel:** {gap['channel']}")
        md_lines.append(f"- **Message:** {gap['message']}")
        md_lines.append(f"- **Ticket:** {gap['ticket_id']}\n")

    # Recurring Questions
    md_lines.append("## Recurring Questions (Product Page Gaps)")
    md_lines.append("These topics appear **2+ times** — they should be on your product pages or FAQ.\n")
    for i, rq in enumerate(report['recurring_questions'][:5], 1):
        md_lines.append(f"### {i}. {rq['topic'].title()}")
        md_lines.append(f"- **Frequency:** Asked {rq['frequency']}× | **Top Personas:** {', '.join(rq['top_personas'])}")
        md_lines.append(f"- **Sample Tickets:** {', '.join(rq['sample_tickets'])}\n")

    # Persona Breakdown
    md_lines.append("## Buyer Persona Breakdown")
    for persona, data in report['persona_breakdown'].items():
        md_lines.append(f"\n### {persona.replace('_', ' ').title()}")
        md_lines.append(f"- **Tickets:** {data['count']}")
        md_lines.append(f"- **KB Coverage:** {data['kb_coverage']}")
        md_lines.append(f"- **Escalation Rate:** {data['escalation_rate']}")
        md_lines.append(f"- **Top Question Types:** {', '.join(k for k in list(data['top_questions'].keys())[:3])}")

    # Recommendations
    md_lines.append("## Content Recommendations")
    md_lines.append("**Action Items for Product & Marketing Leads**\n")
    for i, rec in enumerate(report['recommendations'][:5], 1):
        md_lines.append(f"### {i}. [{rec['urgency']}] {rec['action']}")
        md_lines.append(f"**Topic:** {rec['topic']}")
        md_lines.append(f"**Why:** {rec['why']}")
        md_lines.append(f"**Suggested Placement:** {rec['suggested_placement']}")
        if rec['example_tickets']:
            md_lines.append(f"**Evidence:** {', '.join(rec['example_tickets'])}\n")
        else:
            md_lines.append("")

    md_lines.append(f"\n---\n*Intelligence Report | Generated {report['month']['generated']}*")

    with open(output_path, 'w') as f:
        f.write('\n'.join(md_lines))

    print(f"✓ Report saved:")
    print(f"  - {output_path}")
    print(f"  - {output_path.replace('.md', '.json')}")


if __name__ == '__main__':
    import sys

    csv_path = 'Boldr Data/01_customer_tickets.csv'
    month_end = sys.argv[1] if len(sys.argv) > 1 else None

    df = load_tickets(csv_path)
    report = generate_report(df, month_end_date=month_end)

    save_report(report, 'outputs/monthly_marketing_brief.md')
    print(f"\n📊 Marketing brief complete: {report['executive_summary']['content_recommendations']} recommendations")
