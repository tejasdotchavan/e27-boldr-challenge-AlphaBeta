# External Sentiment Benchmarking Guide

This guide explains how to validate Boldr's internal customer themes against external market sentiment using the **bonus challenge** approach.

---

## Overview

**Goal:** Determine if a customer signal is:
- 🔴 **Boldr-Specific Opportunity** — Market is silent, Boldr customers ask → **Differentiate**
- 🟡 **Boldr-Specific Concern** — Boldr customers care more than the market → **Fix it**
- 🟡 **Balanced Signal** — Market and Boldr are aligned → **Standard priority**
- 🟢 **Market-Wide Baseline** — Every brand addresses it → **Match competitors**

---

## Current Script vs. Real Data

### Current: Mock Data
The included `external_sentiment_benchmark.py` uses **hardcoded sample data** from:
- 2 Reddit subreddits (r/Watches, r/AskWomenOver30)
- 2 Forums (WatchUSeek, Hacker News)
- 2 Review platforms (Trustpilot, YouTube)

**Use case:** Quick demo, proof of concept, testing logic

### Production: Real APIs & Scraping
To validate on real data, integrate:
- **Reddit API** (PRAW library) — posts, comments, sentiment
- **Forum scraping** (BeautifulSoup) — thread counts, engagement
- **Review sites** (custom scraping or APIs) — mention counts
- **News/blog indexing** — emerging trends

---

## Setup: Real External Data Sources

### Option 1: Reddit API (Recommended)

Install PRAW:
```bash
pip install praw
```

Register your app:
1. Go to https://www.reddit.com/prefs/apps
2. Create "script" app
3. Get: `client_id`, `client_secret`, `user_agent`

Script template:
```python
import praw

reddit = praw.Reddit(
    client_id='YOUR_ID',
    client_secret='YOUR_SECRET',
    user_agent='Boldr theme validator by /u/YourUsername'
)

# Search subreddit for keyword
subreddit = reddit.subreddit('watches')
for post in subreddit.search('titanium safety', time_filter='year'):
    print(f"{post.title}: {post.num_comments} comments")
```

**Relevant subreddits for Boldr:**
- `r/Watches` — general watch enthusiasts
- `r/AskWomenOver30` — gifting, lifestyle
- `r/sustainability` — eco-conscious buyers
- `r/microbusiness` — indie brand enthusiasts

---

### Option 2: Forum Scraping (BeautifulSoup)

Install:
```bash
pip install beautifulsoup4 requests
```

Script template:
```python
import requests
from bs4 import BeautifulSoup

# Scrape WatchUSeek for titanium threads
url = 'https://forums.watchuseek.com/f22/'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

for thread in soup.find_all('a', class_='thread-title'):
    if 'titanium' in thread.text.lower():
        print(thread.text)
```

**Forums to monitor:**
- **WatchUSeek** (forums.watchuseek.com) — enthusiast/collector focus
- **Watchuseek buying guide** — trending gear
- **Hacker News** (news.ycombinator.com) — sustainability angle
- **Product Hunt** — new watch launches

---

### Option 3: Review Site Aggregation

**Trustpilot API:**
```bash
pip install trustpilot
```

**YouTube Comments (via Google API):**
```bash
pip install google-api-python-client
```

**Amazon/Etsy reviews:**
- Use Keepa or CamelCamelCamel for price/review history

---

## Integration Steps

### Step 1: Modify `external_sentiment_benchmark.py`

Replace mock data with real API calls:

```python
# OLD: Mock data
REDDIT_DATA = {'r/Watches': {'posts': [...]}}

# NEW: Real API call
def fetch_reddit_data():
    import praw
    reddit = praw.Reddit(...)
    subreddits = ['watches', 'AskWomenOver30', 'sustainability']
    
    results = {}
    for subreddit_name in subreddits:
        posts = []
        subreddit = reddit.subreddit(subreddit_name)
        for post in subreddit.search('titanium OR vegan OR sustainability', time_filter='year'):
            posts.append({
                'title': post.title,
                'comments': post.num_comments,
                'sentiment': get_sentiment(post.selftext)
            })
        results[f'r/{subreddit_name}'] = {'posts': posts}
    
    return results
```

### Step 2: Add Sentiment Analysis

Use a sentiment API or library:

```bash
pip install textblob  # Simple
# OR
pip install transformers huggingface-hub  # Advanced (Hugging Face)
```

Example with TextBlob:
```python
from textblob import TextBlob

def get_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return 'positive'
    elif polarity < -0.1:
        return 'negative'
    else:
        return 'neutral'
```

### Step 3: Cache Results (to avoid rate limits)

```python
import json
from datetime import datetime, timedelta

def load_cached_data(cache_file='external_cache.json'):
    try:
        with open(cache_file, 'r') as f:
            data = json.load(f)
            # Only use cache if < 7 days old
            if (datetime.now() - datetime.fromisoformat(data['timestamp'])).days < 7:
                return data['sources']
    except FileNotFoundError:
        pass
    
    # Fetch fresh data
    sources = fetch_all_sources()
    
    # Cache it
    with open(cache_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'sources': sources
        }, f)
    
    return sources
```

---

## Themes to Validate (Benchmark)

Focus on these 3-5 core themes against external sources:

| Theme | Keywords | External Sources | Signal Type |
|-------|----------|------------------|-------------|
| **BPA-free / Materials Safety** | BPA, hypoallergenic, dye safety, non-toxic | r/Watches, Trustpilot, YouTube reviews | ? |
| **Titanium Grade & Safety** | titanium, nickel allergy, Grade 5, Grade 2 | r/Watches, WatchUSeek, Hacker News | ? |
| **Sustainability & Vegan Straps** | vegan, carbon-neutral, eco, strap recycling | r/sustainability, Hacker News, YouTube | ? |
| **Engraving (Multi-Script & Gifting)** | engrav, arabic, mandarin, multi-script | r/AskWomenOver30, Product Hunt, Trustpilot | ? |
| **Strap Compatibility & Customization** | nato strap, lug width, quick-release | r/Watches, WatchUSeek forums | ? |

---

## Running the Analysis

### Quick Demo (Mock Data)
```bash
python3 external_sentiment_benchmark.py
```

### With Real Data (After Setup)
```bash
# Set environment variables for API keys
export REDDIT_CLIENT_ID="..."
export REDDIT_CLIENT_SECRET="..."
export REDDIT_USER_AGENT="..."

python3 external_sentiment_benchmark.py --use-real-data
```

---

## Expected Outputs

### Signal Types You'll See

#### 🔴 Boldr-Specific Opportunity (No external buzz)
- **Example:** "Engraving in Arabic"
- **Internal:** 2 tickets | **External:** 0 mentions
- **Action:** Lead with this as a differentiator. "Only Boldr supports multi-script engraving."

#### 🟡 Boldr-Specific Concern (Higher than market)
- **Example:** "BPA-free straps"
- **Internal:** 11 tickets | **External:** 24 mentions
- **Action:** Boldr customers care 2x more than market. Invest in KB and messaging.

#### 🟢 Market-Wide Baseline (Table stakes)
- **Example:** "Titanium durability"
- **Internal:** 4 tickets | **External:** 130 mentions
- **Action:** Match competitors. Non-differentiating, but essential.

---

## Cost & Rate Limits

| Source | Cost | Rate Limit | Update Frequency |
|--------|------|-----------|------------------|
| Reddit PRAW API | Free | 60 requests/min | Real-time |
| WatchUSeek (scrape) | Free | ~10 req/min | Weekly |
| Trustpilot API | Free | 10 req/sec | Daily |
| YouTube Data API | Free (quota) | 10k units/day | Real-time |
| Hacker News | Free | Unlimited | Real-time |

**Recommendation:** Run benchmarking monthly (not weekly) to stay within free tier limits.

---

## Production Checklist

- [ ] Set up Reddit API credentials (get from https://reddit.com/prefs/apps)
- [ ] Install PRAW (`pip install praw`)
- [ ] Add sentiment analysis (TextBlob or Transformers)
- [ ] Implement caching to avoid rate limits
- [ ] Test with 1-2 themes first before full rollout
- [ ] Set monthly schedule (not weekly) to preserve free tier
- [ ] Add error handling for API downtime
- [ ] Store results in Google Sheets for historical tracking
- [ ] Create Slack notification for actionable insights

---

## Example: Full Real Data Workflow

```bash
# 1. Monthly benchmark run (1st of month)
0 9 1 * * cd /path/to/boldr && \
  python3 external_sentiment_benchmark.py --use-real-data && \
  python3 -c "import json; print(json.load(open('outputs/external_sentiment_benchmark.json'))['summary'])" | \
  curl -X POST -d "@-" https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# 2. Archive results for trend analysis
0 10 1 * * cp outputs/external_sentiment_benchmark.json \
  archives/benchmarks_$(date +%Y-%m-%d).json
```

---

## Troubleshooting

**Q: Reddit API returns 403 Unauthorized**  
A: Check `client_id`, `client_secret`, and `user_agent` are correct. Ensure app is registered at https://reddit.com/prefs/apps

**Q: Rate limit errors**  
A: Implement caching (cache file if < 7 days old). Run monthly, not weekly.

**Q: Forum scraping blocked (403 Forbidden)**  
A: Add delay between requests: `time.sleep(2)` between requests. Some forums require User-Agent header.

**Q: Sentiment analysis inaccurate**  
A: TextBlob is simple. Use Hugging Face transformers for better accuracy, or manually label sample posts.

---

## Files

| File | Purpose |
|------|---------|
| `external_sentiment_benchmark.py` | Main benchmarking script (currently with mock data) |
| `outputs/external_sentiment_benchmark.md` | Human-readable report |
| `outputs/external_sentiment_benchmark.json` | Machine-readable results |

---

## Next Steps

1. ✅ Run demo with mock data (done)
2. **Set up Reddit API** (15 min)
3. **Add PRAW integration** (30 min)
4. **Test with 1-2 themes** (1 hour)
5. **Schedule monthly runs** (cron or n8n)
6. **Archive results for trend tracking** (Google Sheets)

---

**See Also:** [SETUP_THEME_AND_BRIEF.md](SETUP_THEME_AND_BRIEF.md) for integrating with theme clustering & marketing brief.
