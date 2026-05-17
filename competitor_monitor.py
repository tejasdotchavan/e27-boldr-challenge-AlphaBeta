#!/usr/bin/env python3
"""
Competitor Feature Monitor for Boldr
Tracks when competing watch brands launch features relevant to Boldr customer signals.
Update the COMPETITOR_DB below whenever you spot a new launch.
Run weekly to generate a delta report showing what changed.
"""

import json
import os
from datetime import datetime

DB_PATH = 'outputs/competitor_db.json'

# ============================================================================
# COMPETITOR DATABASE — update this when you spot new launches
# ============================================================================

COMPETITOR_DB = {
    "last_updated": "2026-05-17",
    "competitors": {
        "Nordgreen": {
            "url": "https://nordgreen.com",
            "watch_type": "Danish minimalist",
            "features": {
                "vegan_strap": {
                    "status": "launched",
                    "date": "2023-Q1",
                    "marketing_prominence": "high",
                    "source": "https://nordgreen.com/blogs/news/vegan-strap-launch",
                    "social_response": {
                        "instagram_likes": 4200,
                        "twitter_retweets": 312,
                        "sentiment": "positive"
                    },
                    "notes": "Heavy homepage feature, full campaign"
                },
                "carbon_neutral_shipping": {
                    "status": "launched",
                    "date": "2023-Q3",
                    "marketing_prominence": "medium",
                    "source": "https://nordgreen.com/pages/sustainability",
                    "social_response": {
                        "instagram_likes": 2100,
                        "twitter_retweets": 178,
                        "sentiment": "positive"
                    },
                    "notes": "Offset via DHL GoGreen, badge on checkout"
                },
                "bpa_free_certification": {
                    "status": "launched",
                    "date": "2022-Q4",
                    "marketing_prominence": "medium",
                    "source": "https://nordgreen.com/pages/materials",
                    "social_response": None,
                    "notes": "On materials page, not prominently marketed"
                },
                "multi_script_engraving": {
                    "status": "not_launched",
                    "date": None,
                    "marketing_prominence": None,
                    "source": None,
                    "social_response": None,
                    "notes": "Latin characters only as of May 2026"
                },
                "titanium_grade5": {
                    "status": "launched",
                    "date": "2020",
                    "marketing_prominence": "high",
                    "source": "https://nordgreen.com/pages/materials",
                    "social_response": None,
                    "notes": "Standard across all models"
                }
            }
        },
        "Solios": {
            "url": "https://solioswatches.com",
            "watch_type": "Solar-powered microbrands",
            "features": {
                "vegan_strap": {
                    "status": "launched",
                    "date": "2023-Q2",
                    "marketing_prominence": "high",
                    "source": "https://solioswatches.com/collections/vegan-straps",
                    "social_response": {
                        "instagram_likes": 3800,
                        "twitter_retweets": 290,
                        "sentiment": "positive"
                    },
                    "notes": "Dedicated vegan strap collection, top menu item"
                },
                "carbon_neutral_shipping": {
                    "status": "launched",
                    "date": "2024-Q1",
                    "marketing_prominence": "medium",
                    "source": "https://solioswatches.com/pages/planet",
                    "social_response": {
                        "instagram_likes": 1200,
                        "twitter_retweets": 89,
                        "sentiment": "positive"
                    },
                    "notes": "Carbon offset through Pachama forestry"
                },
                "multi_script_engraving": {
                    "status": "launched",
                    "date": "2025-Q1",
                    "marketing_prominence": "low",
                    "source": "https://solioswatches.com/pages/personalization",
                    "social_response": {
                        "instagram_likes": 450,
                        "twitter_retweets": 34,
                        "sentiment": "positive"
                    },
                    "notes": "Arabic, Chinese, Latin. Quiet launch, no campaign"
                },
                "bpa_free_certification": {
                    "status": "launched",
                    "date": "2023",
                    "marketing_prominence": "low",
                    "source": "https://solioswatches.com/pages/materials",
                    "social_response": None,
                    "notes": "Listed in FAQ, not prominently marketed"
                },
                "titanium_grade5": {
                    "status": "not_launched",
                    "date": None,
                    "marketing_prominence": None,
                    "source": None,
                    "social_response": None,
                    "notes": "Uses stainless steel; titanium not in lineup"
                }
            }
        },
        "Minase": {
            "url": "https://minase-watches.com",
            "watch_type": "Japanese artisan, titanium-focused",
            "features": {
                "titanium_grade5": {
                    "status": "launched",
                    "date": "2019",
                    "marketing_prominence": "high",
                    "source": "https://minase-watches.com/technology",
                    "social_response": None,
                    "notes": "Core brand identity, Grade 5 is central to all models"
                },
                "vegan_strap": {
                    "status": "not_launched",
                    "date": None,
                    "marketing_prominence": None,
                    "source": None,
                    "social_response": None,
                    "notes": "Premium leather only, sustainability not a focus"
                },
                "carbon_neutral_shipping": {
                    "status": "not_launched",
                    "date": None,
                    "marketing_prominence": None,
                    "source": None,
                    "social_response": None,
                    "notes": None
                },
                "multi_script_engraving": {
                    "status": "launched",
                    "date": "2018",
                    "marketing_prominence": "medium",
                    "source": "https://minase-watches.com/personalization",
                    "social_response": None,
                    "notes": "Kanji + Latin engraving, artisan positioning"
                },
                "bpa_free_certification": {
                    "status": "not_launched",
                    "date": None,
                    "marketing_prominence": None,
                    "source": None,
                    "social_response": None,
                    "notes": None
                }
            }
        },
        "Boldr": {
            "url": "https://boldrwatch.com",
            "watch_type": "Singapore titanium microbrands",
            "features": {
                "vegan_strap": {
                    "status": "not_launched",
                    "date": None,
                    "marketing_prominence": None,
                    "source": None,
                    "social_response": None,
                    "notes": "No vegan options as of May 2026"
                },
                "carbon_neutral_shipping": {
                    "status": "not_launched",
                    "date": None,
                    "marketing_prominence": None,
                    "source": None,
                    "social_response": None,
                    "notes": "No sustainability commitments public as of May 2026"
                },
                "multi_script_engraving": {
                    "status": "partial",
                    "date": "unknown",
                    "marketing_prominence": "low",
                    "source": None,
                    "social_response": None,
                    "notes": "Chinese supported per FAQ; Arabic unconfirmed — TKT-1070 was a gap"
                },
                "bpa_free_certification": {
                    "status": "partial",
                    "date": "unknown",
                    "marketing_prominence": "low",
                    "source": None,
                    "social_response": None,
                    "notes": "36% KB coverage — confirmed for some straps, not all"
                },
                "titanium_grade5": {
                    "status": "launched",
                    "date": "2023",
                    "marketing_prominence": "medium",
                    "source": "https://boldrwatch.com/pages/materials",
                    "social_response": None,
                    "notes": "Grade 5 on Expedition model; not always surfaced clearly"
                }
            }
        }
    }
}


FEATURES_TRACKED = {
    "vegan_strap": "Vegan/Sustainable Straps",
    "carbon_neutral_shipping": "Carbon Neutral Shipping",
    "multi_script_engraving": "Multi-Script Engraving",
    "bpa_free_certification": "BPA-Free Certification",
    "titanium_grade5": "Titanium Grade 5 Spec"
}


def load_db():
    if os.path.exists(DB_PATH):
        with open(DB_PATH) as f:
            return json.load(f)
    return COMPETITOR_DB


def save_db(db):
    os.makedirs('outputs', exist_ok=True)
    with open(DB_PATH, 'w') as f:
        json.dump(db, f, indent=2)


def generate_feature_matrix(db):
    """Build a feature × competitor matrix showing launch status."""
    competitors = db['competitors']
    features = list(FEATURES_TRACKED.keys())
    brands = list(competitors.keys())

    matrix = {}
    for feature in features:
        matrix[feature] = {}
        for brand in brands:
            feat_data = competitors[brand]['features'].get(feature, {})
            status = feat_data.get('status', 'unknown')
            date = feat_data.get('date', '')
            matrix[feature][brand] = {'status': status, 'date': date}

    return matrix


def gap_analysis(db):
    """Identify where Boldr is behind competitors."""
    boldr = db['competitors']['Boldr']['features']
    gaps = []

    for feature_key, feature_name in FEATURES_TRACKED.items():
        boldr_status = boldr.get(feature_key, {}).get('status', 'not_launched')
        launched_by = []

        for brand, brand_data in db['competitors'].items():
            if brand == 'Boldr':
                continue
            feat = brand_data['features'].get(feature_key, {})
            if feat.get('status') == 'launched':
                launched_by.append({
                    'brand': brand,
                    'date': feat.get('date'),
                    'prominence': feat.get('marketing_prominence'),
                    'source': feat.get('source'),
                    'social': feat.get('social_response')
                })

        if launched_by and boldr_status in ('not_launched', 'partial'):
            earliest = min([b['date'] for b in launched_by if b['date']], default='?')
            high_engagement = [b for b in launched_by
                               if b['social'] and b['social'].get('instagram_likes', 0) > 1000]

            gaps.append({
                'feature': feature_name,
                'boldr_status': boldr_status,
                'launched_by': launched_by,
                'earliest_competitor': earliest,
                'high_engagement_launches': high_engagement,
                'urgency': 'CRITICAL' if len(launched_by) >= 2 else 'MEDIUM'
            })

    gaps.sort(key=lambda x: 0 if x['urgency'] == 'CRITICAL' else 1)
    return gaps


def generate_delta_report(db):
    """Compare current DB to what Boldr has — what changed recently."""
    gaps = gap_analysis(db)
    matrix = generate_feature_matrix(db)

    report_lines = []
    report_lines.append("# Competitor Feature Monitor")
    report_lines.append(f"*Last updated: {db['last_updated']}*\n")

    # Feature matrix table
    report_lines.append("## Feature Matrix\n")
    brands = list(db['competitors'].keys())
    header = "| Feature | " + " | ".join(brands) + " |"
    separator = "|---|" + "---|" * len(brands)
    report_lines.append(header)
    report_lines.append(separator)

    STATUS_ICON = {
        'launched': '✅',
        'partial': '🟡',
        'not_launched': '❌',
        'unknown': '?'
    }

    for feature_key, feature_name in FEATURES_TRACKED.items():
        row = f"| {feature_name} |"
        for brand in brands:
            cell = matrix[feature_key].get(brand, {})
            icon = STATUS_ICON.get(cell.get('status', 'unknown'), '?')
            date = cell.get('date', '') or ''
            row += f" {icon} {date} |"
        report_lines.append(row)

    report_lines.append("")

    # Gap analysis
    report_lines.append("## Gap Analysis — Where Boldr Is Behind\n")

    for gap in gaps:
        urgency_icon = "🚨" if gap['urgency'] == 'CRITICAL' else "⚠️"
        report_lines.append(f"### {urgency_icon} {gap['feature']} [{gap['urgency']}]")
        report_lines.append(f"**Boldr Status:** {gap['boldr_status']}")
        report_lines.append(f"**First competitor launched:** {gap['earliest_competitor']}\n")

        for competitor in gap['launched_by']:
            social = competitor.get('social') or {}
            likes = social.get('instagram_likes', 0)
            rts = social.get('twitter_retweets', 0)
            source = competitor.get('source') or 'no source'
            report_lines.append(
                f"- **{competitor['brand']}** (launched {competitor['date']}, "
                f"prominence: {competitor['prominence']}) "
                f"— 🤍 {likes:,} IG likes, 🔁 {rts} RT"
            )
            report_lines.append(f"  Source: [{source}]({source})")

        if gap['high_engagement_launches']:
            report_lines.append(
                f"\n**Public response was real:** "
                f"{len(gap['high_engagement_launches'])} launch(es) got 1,000+ IG likes — demand validated."
            )

        report_lines.append("")

    # What to track next
    report_lines.append("## What to Watch Next\n")
    report_lines.append("Check these sources monthly for new competitor moves:\n")
    for brand, data in db['competitors'].items():
        if brand == 'Boldr':
            continue
        report_lines.append(f"- [{brand}]({data['url']}) — {data['watch_type']}")

    report_lines.append("\n**Signal sources:**")
    report_lines.append("- Product Hunt: https://producthunt.com (filter: watches)")
    report_lines.append("- Instagram: search brand hashtags after product launches")
    report_lines.append("- Press: Google Alerts for `\"vegan watch\" OR \"sustainable watch\" OR \"carbon watch\"`")

    return '\n'.join(report_lines)


if __name__ == '__main__':
    db = COMPETITOR_DB
    save_db(db)

    report = generate_delta_report(db)
    out_path = 'outputs/competitor_monitor.md'
    with open(out_path, 'w') as f:
        f.write(report)

    print(f"✓ Competitor monitor saved: {out_path}")
    print(f"✓ DB saved: {DB_PATH}\n")

    gaps = gap_analysis(db)
    print("🚨 GAPS FOUND:")
    for g in gaps:
        print(f"  [{g['urgency']}] {g['feature']} — "
              f"{len(g['launched_by'])} competitor(s) launched, Boldr: {g['boldr_status']}")
