import json, re
from datetime import datetime
from collections import Counter, defaultdict
from typing import List, Dict, Any

def _safe_json_loads(line: str):
    try:
        return json.loads(line)
    except Exception:
        try:
            cleaned = line.encode('utf-8', 'ignore').decode('utf-8', 'ignore')
            return json.loads(cleaned)
        except Exception:
            return None

def load_jsonl_data(file_path: str) -> List[Dict[str, Any]]:
    """Load and parse JSONL files from Instagram/TikTok scrapers"""
    rows = []
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = _safe_json_loads(line)
            if obj is not None and isinstance(obj, dict):
                rows.append(obj)
    return rows

def analyze_hashtags(posts: List[Dict[str, Any]]):
    """Extract and analyze hashtag trends"""
    counter = Counter()
    for p in posts:
        tags = p.get('hashtags') or []
        if not tags:
            # Extract inline hashtags from caption/description
            text = (p.get('caption') or '') + ' ' + (p.get('description') or '')
            tags = re.findall(r"#(\w+)", text)
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split() if t.strip().startswith('#')]
        for t in tags:
            tag = t.lower().lstrip('#')
            if tag:
                counter[tag] += 1

    # Lightweight cultural categories
    categories = {
        'hip-hop': {'hiphop', 'rap', 'boom bap', 'trap', 'hip-hop', 'hiphopculture'},
        'streetwear': {'streetwear', 'ootd', 'sneakers', 'hypebeast', 'kicks'},
        'heritage': {'archive', 'y2k', 'throwback', 'retro', 'legacy', 'heritage'}
    }

    tagged = []
    for tag, count in counter.most_common():
        label = []
        for cat, keys in categories.items():
            if any(k in tag for k in keys):
                label.append(cat)
        tagged.append({'hashtag': tag, 'count': count, 'categories': label})

    return tagged

def calculate_engagement_metrics(posts: List[Dict[str, Any]]):
    """Calculate comprehensive engagement analytics"""
    total_likes = 0
    total_comments = 0
    total_shares = 0
    total_views = 0

    by_day = defaultdict(lambda: {'likes':0, 'comments':0, 'shares':0, 'views':0, 'count':0})
    for p in posts:
        total_likes += int(p.get('likesCount') or 0)
        total_comments += int(p.get('commentsCount') or 0)
        total_shares += int(p.get('shareCount') or 0)
        total_views += int(p.get('viewCount') or 0)

        ts = p.get('timestamp')
        if ts:
            try:
                day = datetime.fromisoformat(ts.replace('Z', '+00:00')).date().isoformat()
            except Exception:
                day = 'unknown'
        else:
            day = 'unknown'

        by_day[day]['likes'] += int(p.get('likesCount') or 0)
        by_day[day]['comments'] += int(p.get('commentsCount') or 0)
        by_day[day]['shares'] += int(p.get('shareCount') or 0)
        by_day[day]['views'] += int(p.get('viewCount') or 0)
        by_day[day]['count'] += 1

    count_posts = len(posts) if posts else 1
    avg_engagement = (total_likes + total_comments + total_shares) / count_posts

    trend = []
    for day, vals in sorted(by_day.items()):
        trend.append({
            'day': day,
            'avg_engagement': (vals['likes']+vals['comments']+vals['shares'])/max(1, vals['count']),
            'avg_views': vals['views']/max(1, vals['count']),
            'posts': vals['count']
        })

    engagement_rate = 0.0
    if total_views > 0:
        engagement_rate = round((total_likes + total_comments + total_shares) / total_views * 100.0, 2)

    return {
        'totals': {
            'likes': total_likes,
            'comments': total_comments,
            'shares': total_shares,
            'views': total_views,
            'posts': len(posts)
        },
        'averages': {
            'engagement_per_post': round(avg_engagement, 2)
        },
        'engagement_rate_percent': engagement_rate,
        'trend': trend
    }

def identify_cultural_moments(posts: List[Dict[str, Any]]):
    """Detect cultural events and trends from social data"""
    moments = []
    keywords = [
        ('Hispanic Heritage', ['hispanic', 'latino', 'latin', 'latinx', 'mexico']),
        ('Hip-Hop Anniversary', ['hiphop', 'hip-hop', 'rap', 'biggie', 'tupac', 'wu-tang']),
        ('Streetwear Heritage', ['archive', 'throwback', 'y2k', 'heritage']),
    ]
    for p in posts:
        text = (p.get('caption') or '') + ' ' + (p.get('description') or '')
        tl = text.lower()
        hit = []
        for label, keys in keywords:
            if any(k in tl for k in keys):
                hit.append(label)
        if hit:
            moments.append({
                'timestamp': p.get('timestamp'),
                'url': p.get('url'),
                'labels': list(set(hit)),
                'summary': text.strip()[:160]
            })
    return moments

def competitive_analysis(data: Dict[str, Any]):
    """Analyze competitive positioning"""
    posts = data.get('all_posts', [])
    brand_mentions = Counter()
    competitors = [
        'crooks & castles','crooks and castles','crooks',
        'supreme','bape','kith','palace','fear of god',
        'off-white','purple brand','stussy','billionaire boys club'
    ]

    for p in posts:
        text = (p.get('caption') or '') + ' ' + (p.get('description') or '')
        tl = text.lower()
        for c in competitors:
            if c in tl:
                brand_mentions[c] += 1

    total = sum(brand_mentions.values()) or 1
    comp = []
    for b, n in brand_mentions.most_common():
        comp.append({'brand': b.title(), 'mentions': n, 'share_pct': round(n * 100 / total, 2)})
    return {'brand_mentions': comp, 'notes': 'Mentions detected in captions/descriptions only.'}

def generate_intelligence_report(data: Dict[str, Any]):
    """Create formatted intelligence reports"""
    report = {
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'summary': {
            'posts': len(data.get('all_posts', [])),
            'engagement_rate_percent': data.get('engagement', {}).get('engagement_rate_percent', 0.0)
        },
        'top_hashtags': data.get('hashtags', [])[:20],
        'cultural_moments': data.get('cultural_moments', [])[:20],
        'competitive': data.get('competitive', {}),
        'recommendations': [
            'Double down on upcoming cultural moments in the next 7–14 days.',
            'Repurpose high-engagement formats across IG Reels and TikTok.',
            'Map assets to events and fill gaps 72h ahead of go-live.'
        ]
    }
    return report
