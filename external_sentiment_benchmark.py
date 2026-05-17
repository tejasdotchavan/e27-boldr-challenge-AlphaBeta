#!/usr/bin/env python3
"""
External Sentiment Benchmarking for Boldr Customer Themes

Validates internal theme signals against external sources (Reddit, forums, reviews)
to determine whether signals are Boldr-specific gaps or market-wide concerns.

Bonus challenge: Cross-validate on 3+ themes across 2+ external sources.
"""

import json
from datetime import datetime
from collections import Counter


# ============================================================================
# EXTERNAL SOURCE DATA (Mock Data - Replace with Real API Calls)
# ============================================================================

REDDIT_DATA = {
    'r/Watches': {
        'url': 'https://reddit.com/r/watches',
        'description': 'Core watch enthusiasts, microbrands & specs focus',
        'posts': [
            {'title': 'BPA-free strap recommendations for sensitive skin', 'comments': 24, 'sentiment': 'positive'},
            {'title': 'Titanium watches: nickel allergy safe?', 'comments': 18, 'sentiment': 'positive'},
            {'title': 'Best titanium microbrands 2026 under $500', 'comments': 45, 'sentiment': 'positive'},
            {'title': 'Strap compatibility across brands (NATO, quick-release)', 'comments': 22, 'sentiment': 'neutral'},
            {'title': 'Grade 5 titanium vs Grade 2: durability comparison', 'comments': 31, 'sentiment': 'positive'},
        ]
    }
}

FORUM_DATA = {
    'WatchUSeek': {
        'url': 'https://forums.watchuseek.com/f496/',
        'description': 'Microbrand enthusiast community (core audience)',
        'threads': [
            {'title': 'Titanium Grade 5 vs Grade 2 - health, durability, value', 'replies': 67, 'sentiment': 'positive'},
            {'title': 'Best affordable titanium watches 2026', 'replies': 52, 'sentiment': 'positive'},
            {'title': 'Strap compatibility: NATO, quick-release, lug width specs', 'replies': 38, 'sentiment': 'neutral'},
            {'title': 'Engraving options across microbrand watches', 'replies': 24, 'sentiment': 'positive'},
            {'title': 'Microbrand warranty & servicing comparison', 'replies': 21, 'sentiment': 'mixed'},
        ]
    },
    'r/watchexchange': {
        'url': 'https://reddit.com/r/watchexchange',
        'description': 'Secondary market, collector sentiment on value/durability',
        'posts': [
            {'title': 'Titanium microbrands holding resale value - which ones?', 'comments': 58, 'sentiment': 'positive'},
            {'title': 'Strap quality issues: which brands fail after 6 months?', 'comments': 31, 'sentiment': 'negative'},
            {'title': 'Best value microbrands for the money', 'comments': 45, 'sentiment': 'positive'},
            {'title': 'Materials durability: titanium vs steel long-term', 'comments': 29, 'sentiment': 'positive'},
        ]
    }
}

REVIEW_SITES = {
    'YouTube Watch Reviews (Microbrands)': {
        'url': 'https://youtube.com/results?search_query=microbrand+watch+review',
        'description': 'Dedicated watch review channels (JustOneMoreWatch, Hodinkee, etc.)',
        'mentions': {
            'titanium durability': 34,
            'strap quality': 41,
            'water resistance': 52,
            'build quality': 48,
            'value for money': 43,
            'sustainability practices': 12,
        }
    },
    'Trustpilot (Watch Brands)': {
        'url': 'https://trustpilot.com/search?query=watch+brands',
        'description': 'Verified customer reviews on watch micro-brands',
        'mentions': {
            'titanium safety': 18,
            'engraving quality': 23,
            'strap durability': 14,
            'customer service speed': 19,
            'material certifications': 8,
            'shipping quality': 21,
        }
    }
}


# ============================================================================
# INTERNAL THEME BASELINE (from Boldr tickets)
# ============================================================================

INTERNAL_THEMES = {
    'BPA-free / Materials Safety': {
        'internal_freq': 11,  # tickets
        'personas': ['health_conscious'],
        'kb_coverage': '36%',
        'escalation_rate': '36%',
        'description': 'Customers ask if straps contain BPA, dye safety, hypoallergenic materials'
    },
    'Titanium Grade & Safety': {
        'internal_freq': 4,  # tickets
        'personas': ['health_conscious'],
        'kb_coverage': '50%',
        'escalation_rate': '25%',
        'description': 'Grade 2 vs Grade 5 titanium, nickel allergy concerns, durability'
    },
    'Sustainability & Vegan Straps': {
        'internal_freq': 3,  # tickets
        'personas': ['niche_buyer'],
        'kb_coverage': '0%',
        'escalation_rate': '100%',
        'description': 'Carbon-neutral shipping, vegan materials, strap recycling, eco-packaging'
    },
    'Engraving (Multi-Script & Gifting)': {
        'internal_freq': 10,  # tickets
        'personas': ['gifter', 'niche_buyer'],
        'kb_coverage': '60%',
        'escalation_rate': '30%',
        'description': 'Font options, Arabic/Chinese characters, engraving depth, turnaround'
    },
    'Strap Compatibility & Customization': {
        'internal_freq': 8,  # tickets
        'personas': ['enthusiast'],
        'kb_coverage': '75%',
        'escalation_rate': '25%',
        'description': 'Quick-release, lug width, NATO compatibility, third-party straps'
    }
}


# ============================================================================
# BENCHMARKING LOGIC
# ============================================================================

def count_external_mentions(keyword_themes):
    """
    Aggregate mentions across external sources by theme keyword.
    Returns dict of theme: external_count
    """
    theme_counts = {}

    # Map keywords to themes
    keyword_map = {
        'BPA-free / Materials Safety': ['bpa', 'hypoallergenic', 'dye safety', 'non-toxic'],
        'Titanium Grade & Safety': ['titanium', 'nickel allergy', 'grade 5', 'grade 2', 'safety'],
        'Sustainability & Vegan Straps': ['vegan', 'carbon', 'eco', 'sustainable', 'recycl'],
        'Engraving (Multi-Script & Gifting)': ['engrav', 'gift', 'mandarin', 'arabic', 'script'],
        'Strap Compatibility & Customization': ['strap', 'nato', 'lug width', 'strap compatibility']
    }

    for theme, keywords in keyword_map.items():
        count = 0

        # Count Reddit mentions
        for subreddit, data in REDDIT_DATA.items():
            for post in data['posts']:
                title_lower = post['title'].lower()
                for keyword in keywords:
                    if keyword in title_lower:
                        count += post['comments']  # Weight by engagement
                        break

        # Count Forum mentions
        for forum, data in FORUM_DATA.items():
            for thread in data.get('threads', []):
                title_lower = thread['title'].lower()
                for keyword in keywords:
                    if keyword in title_lower:
                        count += thread.get('replies', thread.get('points', 0))
                        break

        # Count Review site mentions
        for site, data in REVIEW_SITES.items():
            for kw in keywords:
                if kw in data.get('mentions', {}):
                    count += data['mentions'][kw] * 2  # Weight reviews higher

        theme_counts[theme] = count

    return theme_counts


def analyze_theme_externally(theme_name, internal_data, external_count):
    """
    Compare internal signals to external sentiment.
    Determine if Boldr-specific or market-wide concern.
    """
    internal_freq = internal_data['internal_freq']

    # Calculate market saturation
    # High external count relative to internal = market-wide concern
    # Low external count = Boldr-specific gap

    if external_count == 0:
        signal_type = '🔴 BOLDR-SPECIFIC OPPORTUNITY'
        insight = 'Customers ask frequently, but market is silent. This is a Boldr differentiation angle.'
    elif external_count < internal_freq * 2:
        signal_type = '🟡 BOLDR-SPECIFIC CONCERN (EMERGING)'
        insight = 'Customers ask about this more often than market-wide. Boldr should address it.'
    elif external_count > internal_freq * 10:
        signal_type = '🟢 MARKET-WIDE BASELINE EXPECTATION'
        insight = 'This is table stakes — every brand is addressing it. Boldr needs to be competitive, not differentiated.'
    else:
        signal_type = '🟡 BALANCED SIGNAL'
        insight = 'Market cares, and so do Boldr customers. Priority: standard implementation.'

    return {
        'theme': theme_name,
        'signal_type': signal_type,
        'internal_freq': internal_freq,
        'external_signal_strength': external_count,
        'ratio': f"{external_count / max(internal_freq, 1):.1f}x market",
        'insight': insight,
        'kb_coverage': internal_data['kb_coverage'],
        'escalation_rate': internal_data['escalation_rate'],
    }


def generate_benchmarking_report(month_end_date=None):
    """Generate external sentiment benchmarking report."""

    if month_end_date is None:
        month_end_date = datetime.now()
    else:
        month_end_date = datetime.fromisoformat(month_end_date) if isinstance(month_end_date, str) else month_end_date

    # Count external mentions per theme
    external_counts = count_external_mentions(INTERNAL_THEMES.keys())

    # Analyze each theme
    analyses = []
    for theme_name, internal_data in INTERNAL_THEMES.items():
        external_count = external_counts.get(theme_name, 0)
        analysis = analyze_theme_externally(theme_name, internal_data, external_count)
        analyses.append(analysis)

    # Sort by signal type priority
    priority_order = {'🔴 BOLDR-SPECIFIC OPPORTUNITY': 0, '🟡 BOLDR-SPECIFIC CONCERN (EMERGING)': 1,
                      '🟡 BALANCED SIGNAL': 2, '🟢 MARKET-WIDE BASELINE EXPECTATION': 3}
    analyses.sort(key=lambda x: priority_order.get(x['signal_type'], 999))

    report = {
        'benchmarking_period': {
            'month_end': month_end_date.strftime('%Y-%m-%d'),
            'generated': datetime.now().isoformat(),
            'sources_analyzed': {
                'reddit': 1,
                'forums': 2,
                'review_sites': 2,
                'total': 5,
            }
        },
        'summary': {
            'boldr_specific_opportunities': len([a for a in analyses if '🔴' in a['signal_type']]),
            'boldr_specific_concerns': len([a for a in analyses if '🟡 BOLDR-SPECIFIC' in a['signal_type']]),
            'market_wide_baselines': len([a for a in analyses if '🟢' in a['signal_type']]),
        },
        'analyses': analyses,
    }

    return report


def save_benchmarking_report(report, output_path):
    """Save benchmarking report as JSON and markdown."""

    # JSON
    json_path = output_path.replace('.md', '.json')
    with open(json_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    # Markdown
    md_lines = []
    md_lines.append("# External Sentiment Benchmarking Report")
    md_lines.append("**Bonus Challenge:** Validating internal themes against external sources")
    md_lines.append(f"\n**Analysis Period:** {report['benchmarking_period']['month_end']}")
    md_lines.append(f"**Sources Analyzed:** {report['benchmarking_period']['sources_analyzed']['total']}")
    md_lines.append(f"- Reddit: 1 subreddit (r/Watches)")
    md_lines.append(f"- Forums: 2 communities (WatchUSeek, r/watchexchange)")
    md_lines.append(f"- Review sites: 2 platforms (YouTube, Trustpilot)\n")

    md_lines.append("## Summary")
    md_lines.append(f"- **Boldr-Specific Opportunities:** {report['summary']['boldr_specific_opportunities']} themes")
    md_lines.append(f"- **Boldr-Specific Concerns:** {report['summary']['boldr_specific_concerns']} themes")
    md_lines.append(f"- **Market-Wide Baselines:** {report['summary']['market_wide_baselines']} themes\n")

    md_lines.append("## Theme-by-Theme Analysis\n")

    for i, analysis in enumerate(report['analyses'], 1):
        md_lines.append(f"### {i}. {analysis['theme']}")
        md_lines.append(f"**Signal Type:** {analysis['signal_type']}")
        md_lines.append(f"**Internal Frequency:** {analysis['internal_freq']} tickets")
        md_lines.append(f"**External Signal Strength:** {analysis['external_signal_strength']} mentions")
        md_lines.append(f"**Ratio:** {analysis['ratio']}\n")
        md_lines.append(f"**Insight:** {analysis['insight']}\n")
        md_lines.append(f"**Current State:**")
        md_lines.append(f"- KB Coverage: {analysis['kb_coverage']}")
        md_lines.append(f"- Escalation Rate: {analysis['escalation_rate']}\n")

        # Recommendations based on signal type
        if '🔴' in analysis['signal_type']:
            md_lines.append("**Action:** Lead with this as a differentiator. Market is NOT addressing it yet.")
            md_lines.append("- Add to product marketing: \"Boldr's unique commitment to [feature]\"")
            md_lines.append("- Create dedicated landing page or FAQ section")
        elif 'BOLDR-SPECIFIC CONCERN' in analysis['signal_type']:
            md_lines.append("**Action:** Boldr customers care more than market average. Build it to compete.")
            md_lines.append("- High-priority FAQ entry")
            md_lines.append("- Include in product specifications")
        elif 'BALANCED' in analysis['signal_type']:
            md_lines.append("**Action:** Standard implementation. Match market expectations.")
            md_lines.append("- Ensure KB covers this")
            md_lines.append("- Include in FAQ")
        else:  # Market-wide baseline
            md_lines.append("**Action:** Table stakes. Implement to match competitors.")
            md_lines.append("- Best practice from top brands")
            md_lines.append("- Non-differentiating; focus on execution quality")

        md_lines.append("\n---\n")

    md_lines.append("## External Source Details\n")

    md_lines.append("### Reddit\n")
    for subreddit, data in REDDIT_DATA.items():
        md_lines.append(f"**{subreddit}** ({data['description']})")
        md_lines.append(f"- URL: {data['url']}")
        md_lines.append(f"- Posts analyzed: {len(data['posts'])}\n")

    md_lines.append("### Forums\n")
    for forum, data in FORUM_DATA.items():
        md_lines.append(f"**{forum}** ({data['description']})")
        md_lines.append(f"- URL: {data['url']}")
        md_lines.append(f"- Threads analyzed: {len(data.get('threads', []))}\n")

    md_lines.append("### Review Sites\n")
    for site, data in REVIEW_SITES.items():
        md_lines.append(f"**{site}** ({data['description']})")
        md_lines.append(f"- URL: {data['url']}")
        md_lines.append(f"- Keywords tracked: {len(data.get('mentions', {}))}\n")

    md_lines.append("---\n")
    md_lines.append("## How to Read This Report\n")
    md_lines.append("- **🔴 Boldr-Specific Opportunity:** Market is silent, but Boldr customers ask. DIFFERENTIATE HERE.")
    md_lines.append("- **🟡 Boldr-Specific Concern:** Boldr customers care more than the market average. FIX IT.")
    md_lines.append("- **🟡 Balanced Signal:** Market and Boldr are aligned. Standard priority.")
    md_lines.append("- **🟢 Market-Wide Baseline:** Everyone's doing it. Match competitors, don't innovate.")

    with open(output_path, 'w') as f:
        f.write('\n'.join(md_lines))

    print(f"✓ Benchmarking report saved:")
    print(f"  - {output_path}")
    print(f"  - {json_path}")


if __name__ == '__main__':
    import sys

    month_end = sys.argv[1] if len(sys.argv) > 1 else None

    report = generate_benchmarking_report(month_end_date=month_end)
    save_benchmarking_report(report, 'outputs/external_sentiment_benchmark.md')

    print(f"\n🌍 Benchmarking complete:")
    print(f"  - Boldr-Specific Opportunities: {report['summary']['boldr_specific_opportunities']}")
    print(f"  - Market-Wide Baselines: {report['summary']['market_wide_baselines']}")
