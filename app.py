#!/usr/bin/env python3
"""
Crooks & Castles Command Center V2 - Fully Functional Version
Real data analysis, asset management, content planning, and file operations
"""

import os
import json
import uuid
import shutil
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import mimetypes
from PIL import Image
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'crooks-castles-command-center-v2'

# Configuration
UPLOAD_FOLDER = 'upload'
STATIC_FOLDER = 'static'
THUMBNAILS_FOLDER = os.path.join(STATIC_FOLDER, 'thumbnails')
ASSETS_FOLDER = os.path.join(STATIC_FOLDER, 'assets')

# Ensure directories exist
for folder in [UPLOAD_FOLDER, THUMBNAILS_FOLDER, ASSETS_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# Global data storage
intelligence_data = {
    'instagram_posts': [],
    'tiktok_videos': [],
    'hashtag_data': [],
    'competitive_analysis': {},
    'cultural_moments': [],
    'last_updated': None
}

asset_library = {}
content_calendar = {}

def load_jsonl_file(filepath):
    """Load and parse JSONL file"""
    data = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        print(f"Error parsing line: {e}")
                        continue
    except Exception as e:
        print(f"Error loading file {filepath}: {e}")
    return data

def analyze_instagram_data(posts):
    """Analyze Instagram posts for insights"""
    analysis = {
        'total_posts': len(posts),
        'total_engagement': 0,
        'avg_engagement': 0,
        'top_hashtags': [],
        'top_brands': [],
        'engagement_by_brand': {},
        'cultural_moments': [],
        'trending_topics': []
    }
    
    if not posts:
        return analysis
    
    brand_engagement = defaultdict(list)
    all_hashtags = []
    cultural_keywords = ['heritage', 'culture', 'tradition', 'authentic', 'legacy', 'vintage', 'classic']
    
    for post in posts:
        username = post.get('ownerUsername', '')
        likes = post.get('likesCount', 0)
        comments = post.get('commentsCount', 0)
        engagement = likes + (comments * 3)  # Weight comments more
        
        analysis['total_engagement'] += engagement
        brand_engagement[username].append(engagement)
        
        # Extract hashtags
        hashtags = post.get('hashtags', [])
        all_hashtags.extend(hashtags)
        
        # Check for cultural moments
        caption = post.get('caption', '').lower()
        for keyword in cultural_keywords:
            if keyword in caption:
                analysis['cultural_moments'].append({
                    'username': username,
                    'keyword': keyword,
                    'engagement': engagement,
                    'timestamp': post.get('timestamp')
                })
    
    # Calculate averages and rankings
    analysis['avg_engagement'] = analysis['total_engagement'] / len(posts) if posts else 0
    
    # Top hashtags
    hashtag_counts = Counter(all_hashtags)
    analysis['top_hashtags'] = [{'hashtag': tag, 'count': count} 
                               for tag, count in hashtag_counts.most_common(20)]
    
    # Brand rankings by engagement
    brand_avg_engagement = {}
    for brand, engagements in brand_engagement.items():
        brand_avg_engagement[brand] = {
            'avg_engagement': sum(engagements) / len(engagements),
            'total_posts': len(engagements),
            'total_engagement': sum(engagements)
        }
    
    # Sort brands by average engagement
    sorted_brands = sorted(brand_avg_engagement.items(), 
                          key=lambda x: x[1]['avg_engagement'], 
                          reverse=True)
    
    analysis['competitive_rankings'] = {}
    for i, (brand, data) in enumerate(sorted_brands, 1):
        analysis['competitive_rankings'][brand] = {
            'rank': i,
            'avg_engagement': round(data['avg_engagement'], 2),
            'total_posts': data['total_posts'],
            'total_engagement': data['total_engagement'],
            'performance_tier': 'high' if i <= 10 else 'medium' if i <= 50 else 'low'
        }
    
    return analysis

def analyze_tiktok_data(videos):
    """Analyze TikTok videos for insights"""
    analysis = {
        'total_videos': len(videos),
        'total_views': 0,
        'total_likes': 0,
        'avg_engagement_rate': 0,
        'top_creators': [],
        'trending_sounds': [],
        'viral_content': [],
        'cultural_moments': []
    }
    
    if not videos:
        return analysis
    
    creator_stats = defaultdict(lambda: {'views': 0, 'likes': 0, 'videos': 0})
    sounds = []
    cultural_keywords = ['streetwear', 'fashion', 'style', 'vintage', 'thrift']
    
    for video in videos:
        creator = video.get('authorMeta', {}).get('name', '')
        views = video.get('playCount', 0)
        likes = video.get('diggCount', 0)
        
        analysis['total_views'] += views
        analysis['total_likes'] += likes
        
        creator_stats[creator]['views'] += views
        creator_stats[creator]['likes'] += likes
        creator_stats[creator]['videos'] += 1
        
        # Track sounds
        music = video.get('musicMeta', {})
        if music:
            sounds.append(music.get('musicName', ''))
        
        # Check for viral content (high engagement)
        if views > 100000 or likes > 10000:
            analysis['viral_content'].append({
                'creator': creator,
                'views': views,
                'likes': likes,
                'text': video.get('text', '')[:100]
            })
        
        # Cultural moments
        text = video.get('text', '').lower()
        for keyword in cultural_keywords:
            if keyword in text:
                analysis['cultural_moments'].append({
                    'creator': creator,
                    'keyword': keyword,
                    'views': views,
                    'likes': likes
                })
    
    # Calculate engagement rate
    if analysis['total_views'] > 0:
        analysis['avg_engagement_rate'] = (analysis['total_likes'] / analysis['total_views']) * 100
    
    # Top creators
    sorted_creators = sorted(creator_stats.items(), 
                           key=lambda x: x[1]['views'], 
                           reverse=True)
    analysis['top_creators'] = [{'name': name, **stats} 
                               for name, stats in sorted_creators[:10]]
    
    # Trending sounds
    sound_counts = Counter(sounds)
    analysis['trending_sounds'] = [{'sound': sound, 'count': count} 
                                  for sound, count in sound_counts.most_common(10)]
    
    return analysis

def generate_thumbnail(image_path, size=(300, 300)):
    """Generate thumbnail for image files"""
    try:
        with Image.open(image_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            img.thumbnail(size, Image.Resampling.LANCZOS)
            thumbnail_filename = f"thumb_{os.path.basename(image_path)}"
            thumbnail_path = os.path.join(THUMBNAILS_FOLDER, thumbnail_filename)
            img.save(thumbnail_path, format='JPEG', quality=85)
            return thumbnail_path
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        return None

def scan_assets():
    """Scan upload folder and categorize assets"""
    global asset_library
    asset_library = {}
    
    if not os.path.exists(UPLOAD_FOLDER):
        return
    
    for filename in os.listdir(UPLOAD_FOLDER):
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(filepath):
            file_info = analyze_file(filepath, filename)
            if file_info:
                asset_id = str(uuid.uuid4())
                asset_library[asset_id] = file_info

def analyze_file(filepath, filename):
    """Analyze a file and return metadata"""
    try:
        stat = os.stat(filepath)
        mime_type, _ = mimetypes.guess_type(filepath)
        
        file_info = {
            'id': str(uuid.uuid4()),
            'filename': filename,
            'filepath': filepath,
            'file_size': stat.st_size,
            'upload_date': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'mime_type': mime_type or 'application/octet-stream',
            'category': categorize_file(filename, mime_type),
            'thumbnail_path': None
        }
        
        # Generate thumbnail for images
        if mime_type and mime_type.startswith('image/'):
            thumbnail_path = generate_thumbnail(filepath)
            if thumbnail_path:
                file_info['thumbnail_path'] = thumbnail_path
        
        return file_info
    except Exception as e:
        print(f"Error analyzing file {filename}: {e}")
        return None

def categorize_file(filename, mime_type):
    """Categorize file based on name and type"""
    filename_lower = filename.lower()
    
    if 'instagram' in filename_lower or 'hashtag' in filename_lower:
        return 'intelligence_data'
    elif 'tiktok' in filename_lower:
        return 'intelligence_data'
    elif filename_lower.endswith(('.jsonl', '.json')):
        return 'intelligence_data'
    elif mime_type and mime_type.startswith('image/'):
        if any(word in filename_lower for word in ['story', 'post', 'social']):
            return 'social_content'
        elif any(word in filename_lower for word in ['brand', 'logo', 'wordmark']):
            return 'brand_assets'
        else:
            return 'social_content'
    elif mime_type and mime_type.startswith('video/'):
        return 'video_content'
    elif filename_lower.endswith(('.txt', '.md')):
        return 'documents'
    else:
        return 'other'

def generate_content_calendar():
    """Generate enhanced strategic content calendar with 7/30/60/90 day views and asset mapping"""
    global content_calendar
    
    today = datetime.now()
    
    # Detailed content planning with asset mapping
    detailed_events = [
        # 7-Day View (Next Week)
        {
            'date': (today + timedelta(days=1)).strftime('%Y-%m-%d'),
            'title': 'Hip-Hop Heritage Story Series Launch',
            'category': 'cultural',
            'priority': 'high',
            'view': '7_day',
            'description': 'Launch authentic hip-hop heritage content series',
            'content_details': {
                'platform': 'Instagram + TikTok',
                'format': '1080x1080 + 1080x1920',
                'copy': 'From the streets to the culture. Our heritage runs deep. #CrooksHeritage #HipHopHistory',
                'hashtags': ['#CrooksHeritage', '#HipHopHistory', '#StreetCulture', '#Authentic'],
                'target_audience': 'Hip-hop culture enthusiasts, 18-35',
                'kpis': 'Engagement rate >4%, Reach >50K, Brand mentions +15%'
            },
            'assets_required': [
                {
                    'type': 'hero_image',
                    'specs': '1080x1080, high contrast, street photography style',
                    'mapped_asset': 'real_instagram_story_rebel_rooftop(1).png',
                    'status': 'available',
                    'file_path': 'upload/real_instagram_story_rebel_rooftop(1).png'
                },
                {
                    'type': 'story_template',
                    'specs': '1080x1920, brand colors, heritage theme',
                    'mapped_asset': 'wordmark_story(1).png',
                    'status': 'available',
                    'file_path': 'upload/wordmark_story(1).png'
                },
                {
                    'type': 'video_content',
                    'specs': '15-30s, hip-hop soundtrack, street scenes',
                    'mapped_asset': '410f528c-980e-497b-bcf0-a6294a39631b.mp4',
                    'status': 'available',
                    'file_path': 'upload/410f528c-980e-497b-bcf0-a6294a39631b.mp4'
                }
            ],
            'deliverables': ['Instagram post', 'Instagram story', 'TikTok video', 'Cross-platform copy'],
            'agency_deliverable': True,
            'budget_allocation': 500,
            'high_voltage_digital': {
                'phase': 1,
                'deliverable_count': 3,
                'budget_used': 500,
                'timeline': '2 days production'
            }
        },
        {
            'date': (today + timedelta(days=3)).strftime('%Y-%m-%d'),
            'title': 'Cultural Fusion Content Drop',
            'category': 'cultural',
            'priority': 'high',
            'view': '7_day',
            'description': 'Showcase cultural fusion in streetwear',
            'content_details': {
                'platform': 'Instagram + TikTok',
                'format': '1080x1350 + 1080x1920',
                'copy': 'Where cultures collide, style evolves. #CulturalFusion #StreetStyle',
                'hashtags': ['#CulturalFusion', '#StreetStyle', '#CrooksStyle', '#Diversity'],
                'target_audience': 'Multicultural streetwear fans, 16-30',
                'kpis': 'Engagement rate >3.5%, Saves >1K, Comments >200'
            },
            'assets_required': [
                {
                    'type': 'lifestyle_image',
                    'specs': '1080x1350, diverse models, street setting',
                    'mapped_asset': 'sept_16_cultural_fusion(3).png',
                    'status': 'available',
                    'file_path': 'upload/sept_16_cultural_fusion(3).png'
                },
                {
                    'type': 'carousel_images',
                    'specs': '1080x1080 x3, product focus, lifestyle context',
                    'mapped_asset': 'model1_story.png, model2_story.png',
                    'status': 'available',
                    'file_path': 'upload/model1_story.png'
                }
            ],
            'deliverables': ['Instagram carousel', 'Story series', 'TikTok trend participation'],
            'agency_deliverable': True,
            'budget_allocation': 750,
            'high_voltage_digital': {
                'phase': 1,
                'deliverable_count': 2,
                'budget_used': 750,
                'timeline': '3 days production'
            }
        },
        {
            'date': (today + timedelta(days=5)).strftime('%Y-%m-%d'),
            'title': 'Weekly Intelligence Recap',
            'category': 'intelligence',
            'priority': 'medium',
            'view': '7_day',
            'description': 'Weekly competitive intelligence and trend analysis',
            'content_details': {
                'platform': 'Internal + Client reporting',
                'format': 'PDF report + Dashboard update',
                'copy': 'Weekly intelligence briefing: market trends, competitive analysis, cultural moments',
                'target_audience': 'Internal team, agency partners',
                'kpis': 'Report accuracy >95%, Actionable insights >10, Trend predictions >5'
            },
            'assets_required': [
                {
                    'type': 'data_visualization',
                    'specs': 'Charts, graphs, competitive rankings',
                    'mapped_asset': 'dataset_instagram-hashtag-scraper_2025-09-21_13-10-57-668.jsonl',
                    'status': 'available',
                    'file_path': 'upload/dataset_instagram-hashtag-scraper_2025-09-21_13-10-57-668.jsonl'
                },
                {
                    'type': 'tiktok_analysis',
                    'specs': 'Video performance metrics, trend analysis',
                    'mapped_asset': 'dataset_tiktok-scraper_2025-09-21_13-33-25-969.jsonl',
                    'status': 'available',
                    'file_path': 'upload/dataset_tiktok-scraper_2025-09-21_13-33-25-969.jsonl'
                }
            ],
            'deliverables': ['Weekly report', 'Dashboard update', 'Trend briefing', 'Competitive analysis'],
            'agency_deliverable': True,
            'budget_allocation': 300
        },
        
        # 30-Day View (This Month)
        {
            'date': (today + timedelta(days=10)).strftime('%Y-%m-%d'),
            'title': 'Hispanic Heritage Month Celebration',
            'category': 'cultural',
            'priority': 'high',
            'view': '30_day',
            'description': 'Authentic celebration of Hispanic heritage in streetwear',
            'content_details': {
                'platform': 'All platforms',
                'format': 'Multi-format campaign',
                'copy': 'Celebrating the rich heritage that shapes our streets. #HispanicHeritageMonth #CrooksCulture',
                'hashtags': ['#HispanicHeritageMonth', '#CrooksCulture', '#Heritage', '#Community'],
                'target_audience': 'Hispanic community, culture enthusiasts, 18-40',
                'kpis': 'Campaign reach >500K, Engagement rate >5%, Community sentiment +20%'
            },
            'assets_required': [
                {
                    'type': 'campaign_hero',
                    'specs': '1080x1080, vibrant colors, cultural elements',
                    'mapped_asset': 'sept_15_hispanic_heritage_launch(3).png',
                    'status': 'available',
                    'file_path': 'upload/sept_15_hispanic_heritage_launch(3).png'
                },
                {
                    'type': 'story_series',
                    'specs': '1080x1920 x5, educational + celebratory',
                    'mapped_asset': 'castle_story.png, medusa_story(1).png',
                    'status': 'available',
                    'file_path': 'upload/castle_story.png'
                },
                {
                    'type': 'community_video',
                    'specs': '60s, community voices, authentic stories',
                    'mapped_asset': '9dd8a1ec-8b07-460b-884d-8e0d8a0260d9.mov',
                    'status': 'available',
                    'file_path': 'upload/9dd8a1ec-8b07-460b-884d-8e0d8a0260d9.mov'
                }
            ],
            'deliverables': ['Campaign launch', 'Educational content series', 'Community spotlights', 'UGC campaign'],
            'agency_deliverable': True,
            'budget_allocation': 2000,
            'cultural_sensitivity_review': True,
            'high_voltage_digital': {
                'phase': 1,
                'deliverable_count': 4,
                'budget_used': 2000,
                'timeline': '2 weeks production'
            }
        },
        {
            'date': (today + timedelta(days=20)).strftime('%Y-%m-%d'),
            'title': 'Hip-Hop Anniversary Tribute',
            'category': 'cultural',
            'priority': 'high',
            'view': '30_day',
            'description': 'Tribute to hip-hop anniversary with brand heritage',
            'content_details': {
                'platform': 'Instagram + TikTok + YouTube',
                'format': 'Documentary-style content',
                'copy': 'From the beginning, we were there. Celebrating 50+ years of hip-hop culture. #HipHopAnniversary',
                'hashtags': ['#HipHopAnniversary', '#CrooksHistory', '#StreetCulture', '#Legacy'],
                'target_audience': 'Hip-hop heads, culture historians, 20-45',
                'kpis': 'Video views >100K, Shares >5K, Brand association +25%'
            },
            'assets_required': [
                {
                    'type': 'anniversary_graphic',
                    'specs': '1080x1080, retro aesthetic, timeline design',
                    'mapped_asset': 'sept_19_hiphop_anniversary.png',
                    'status': 'available',
                    'file_path': 'upload/sept_19_hiphop_anniversary.png'
                },
                {
                    'type': 'archive_footage',
                    'specs': 'Historical brand moments, hip-hop connections',
                    'mapped_asset': 'heritage_archive_collection',
                    'status': 'needs_creation',
                    'file_path': 'to_be_created'
                }
            ],
            'deliverables': ['Anniversary post', 'Story timeline', 'Long-form video', 'Press release'],
            'agency_deliverable': True,
            'budget_allocation': 1500,
            'high_voltage_digital': {
                'phase': 1,
                'deliverable_count': 3,
                'budget_used': 1500,
                'timeline': '1 week production'
            }
        },
        
        # 60-Day View (Next 2 Months)
        {
            'date': (today + timedelta(days=45)).strftime('%Y-%m-%d'),
            'title': 'Black Friday Campaign Launch',
            'category': 'commercial',
            'priority': 'high',
            'view': '60_day',
            'description': 'Strategic BFCM campaign with cultural authenticity',
            'content_details': {
                'platform': 'All platforms + Email + SMS',
                'format': 'Integrated campaign',
                'copy': 'Black Friday. Real deals. Authentic style. #CrooksBF #AuthenticDeals',
                'hashtags': ['#CrooksBF', '#AuthenticDeals', '#BlackFriday', '#StreetDeals'],
                'target_audience': 'Deal seekers, loyal customers, gift buyers, 18-35',
                'kpis': 'Sales conversion >8%, Email CTR >15%, Social engagement >6%'
            },
            'assets_required': [
                {
                    'type': 'sale_graphics',
                    'specs': 'Multiple formats, bold typography, brand colors',
                    'mapped_asset': 'needs_creation',
                    'status': 'needs_creation',
                    'file_path': 'to_be_created'
                },
                {
                    'type': 'product_photography',
                    'specs': 'Hero products, lifestyle context, sale pricing',
                    'mapped_asset': 'needs_creation',
                    'status': 'needs_creation',
                    'file_path': 'to_be_created'
                }
            ],
            'deliverables': ['Campaign creative suite', 'Email templates', 'Social ads', 'Website banners'],
            'agency_deliverable': True,
            'budget_allocation': 5000,
            'conversion_optimization': True,
            'high_voltage_digital': {
                'phase': 2,
                'deliverable_count': 7,
                'budget_used': 5000,
                'timeline': '3 weeks production'
            }
        },
        {
            'date': (today + timedelta(days=50)).strftime('%Y-%m-%d'),
            'title': 'Holiday Gift Guide Campaign',
            'category': 'seasonal',
            'priority': 'high',
            'view': '60_day',
            'description': 'Curated gift guide for streetwear enthusiasts',
            'content_details': {
                'platform': 'Instagram + Website + Email',
                'format': 'Editorial-style content',
                'copy': 'Gifts that speak their language. Curated for the culture. #CrooksGifts #HolidayStyle',
                'hashtags': ['#CrooksGifts', '#HolidayStyle', '#GiftGuide', '#StreetGifts'],
                'target_audience': 'Gift buyers, parents, partners, 25-45',
                'kpis': 'Guide engagement >10%, Product clicks >20%, Gift card sales +30%'
            },
            'assets_required': [
                {
                    'type': 'gift_guide_layout',
                    'specs': 'Editorial design, product showcase, price points',
                    'mapped_asset': 'needs_creation',
                    'status': 'needs_creation',
                    'file_path': 'to_be_created'
                }
            ],
            'deliverables': ['Digital gift guide', 'Social carousel', 'Email campaign', 'Website integration'],
            'agency_deliverable': True,
            'budget_allocation': 2500,
            'high_voltage_digital': {
                'phase': 2,
                'deliverable_count': 4,
                'budget_used': 2500,
                'timeline': '2 weeks production'
            }
        },
        
        # 90-Day View (Quarterly Planning)
        {
            'date': (today + timedelta(days=75)).strftime('%Y-%m-%d'),
            'title': 'Q1 2026 Brand Evolution Campaign',
            'category': 'brand',
            'priority': 'high',
            'view': '90_day',
            'description': 'Strategic brand evolution for new year positioning',
            'content_details': {
                'platform': 'All platforms + PR + Partnerships',
                'format': 'Brand manifesto campaign',
                'copy': 'Evolution never stops. 2026 is our year. #CrooksEvolution #NewYear',
                'hashtags': ['#CrooksEvolution', '#NewYear', '#BrandEvolution', '#Future'],
                'target_audience': 'Brand loyalists, industry watchers, new customers, 18-40',
                'kpis': 'Brand awareness +15%, Consideration +20%, Social sentiment +25%'
            },
            'assets_required': [
                {
                    'type': 'brand_manifesto_video',
                    'specs': '60-90s, cinematic, brand story, future vision',
                    'mapped_asset': 'needs_creation',
                    'status': 'needs_creation',
                    'file_path': 'to_be_created'
                }
            ],
            'deliverables': ['Brand film', 'Manifesto content', 'PR package', 'Partnership materials'],
            'agency_deliverable': True,
            'budget_allocation': 8000,
            'strategic_importance': 'critical',
            'high_voltage_digital': {
                'phase': 3,
                'deliverable_count': 10,
                'budget_used': 8000,
                'timeline': '4 weeks production'
            }
        },
        {
            'date': (today + timedelta(days=85)).strftime('%Y-%m-%d'),
            'title': 'Spring 2026 Collection Teasers',
            'category': 'product',
            'priority': 'medium',
            'view': '90_day',
            'description': 'Strategic teasers for upcoming spring collection',
            'content_details': {
                'platform': 'Instagram + TikTok + Email VIP',
                'format': 'Teaser campaign',
                'copy': 'Something fresh is coming. Spring 2026. #ComingSoon #Spring2026',
                'hashtags': ['#ComingSoon', '#Spring2026', '#NewCollection', '#CrooksSpring'],
                'target_audience': 'VIP customers, fashion enthusiasts, early adopters, 18-35',
                'kpis': 'Anticipation engagement >8%, Email signups +500, Wishlist adds +1K'
            },
            'assets_required': [
                {
                    'type': 'teaser_visuals',
                    'specs': 'Mysterious, partial reveals, spring colors',
                    'mapped_asset': 'needs_creation',
                    'status': 'needs_creation',
                    'file_path': 'to_be_created'
                }
            ],
            'deliverables': ['Teaser posts', 'BTS content', 'VIP email', 'Countdown campaign'],
            'agency_deliverable': False,
            'budget_allocation': 1500
        }
    ]
    
    # Organize by view type and date
    content_calendar = {
        '7_day_view': [event for event in detailed_events if event['view'] == '7_day'],
        '30_day_view': [event for event in detailed_events if event['view'] == '30_day'],
        '60_day_view': [event for event in detailed_events if event['view'] == '60_day'],
        '90_day_view': [event for event in detailed_events if event['view'] == '90_day'],
        'all_events': detailed_events,
        'quarterly_summary': {
            'total_events': len(detailed_events),
            'agency_deliverables': len([e for e in detailed_events if e.get('agency_deliverable')]),
            'total_budget': sum([e.get('budget_allocation', 0) for e in detailed_events]),
            'cultural_moments': len([e for e in detailed_events if e['category'] == 'cultural']),
            'commercial_campaigns': len([e for e in detailed_events if e['category'] == 'commercial']),
            'assets_needed': sum([len(e.get('assets_required', [])) for e in detailed_events]),
            'assets_available': len([a for e in detailed_events for a in e.get('assets_required', []) if a.get('status') == 'available']),
            'high_voltage_digital_summary': {
                'phase_1_deliverables': len([e for e in detailed_events if e.get('high_voltage_digital', {}).get('phase') == 1]),
                'phase_2_deliverables': len([e for e in detailed_events if e.get('high_voltage_digital', {}).get('phase') == 2]),
                'phase_3_deliverables': len([e for e in detailed_events if e.get('high_voltage_digital', {}).get('phase') == 3]),
                'total_budget_allocated': sum([e.get('budget_allocation', 0) for e in detailed_events if e.get('agency_deliverable')])
            }
        }
    }
    
    return content_calendar

def load_intelligence_data():
    """Load and analyze all intelligence data"""
    global intelligence_data
    
    # Load Instagram data
    instagram_file = os.path.join(UPLOAD_FOLDER, 'dataset_instagram-hashtag-scraper_2025-09-21_13-10-57-668.jsonl')
    if os.path.exists(instagram_file):
        posts = load_jsonl_file(instagram_file)
        intelligence_data['instagram_posts'] = posts
        instagram_analysis = analyze_instagram_data(posts)
        intelligence_data.update(instagram_analysis)
    
    # Load TikTok data
    tiktok_file = os.path.join(UPLOAD_FOLDER, 'dataset_tiktok-scraper_2025-09-21_13-33-25-969.jsonl')
    if os.path.exists(tiktok_file):
        videos = load_jsonl_file(tiktok_file)
        intelligence_data['tiktok_videos'] = videos
        tiktok_analysis = analyze_tiktok_data(videos)
        intelligence_data['tiktok_analysis'] = tiktok_analysis
    
    # Load competitive data
    competitive_file = os.path.join(UPLOAD_FOLDER, 'instagram_competitive_data.jsonl')
    if os.path.exists(competitive_file):
        competitive_data = load_jsonl_file(competitive_file)
        intelligence_data['competitive_data'] = competitive_data
    
    intelligence_data['last_updated'] = datetime.now().isoformat()

def generate_weekly_report():
    """Generate comprehensive weekly report"""
    report = {
        'report_date': datetime.now().strftime('%Y-%m-%d'),
        'data_freshness': intelligence_data.get('last_updated'),
        'executive_summary': {
            'total_posts_analyzed': len(intelligence_data.get('instagram_posts', [])),
            'total_videos_analyzed': len(intelligence_data.get('tiktok_videos', [])),
            'competitive_brands_tracked': len(intelligence_data.get('competitive_rankings', {})),
            'cultural_moments_detected': len(intelligence_data.get('cultural_moments', [])),
            'crooks_ranking': None
        },
        'competitive_landscape': intelligence_data.get('competitive_rankings', {}),
        'trending_content': {
            'top_hashtags': intelligence_data.get('top_hashtags', [])[:10],
            'viral_tiktoks': intelligence_data.get('tiktok_analysis', {}).get('viral_content', [])[:5]
        },
        'strategic_opportunities': [
            {
                'title': 'Hip-Hop Heritage Content',
                'priority': 'high',
                'description': 'Leverage October Hip-Hop History Month for authentic brand storytelling',
                'action': 'Create heritage-focused content series highlighting brand origins'
            },
            {
                'title': 'TikTok Streetwear Trends',
                'priority': 'medium', 
                'description': 'Capitalize on thrifting and vintage fashion trends',
                'action': 'Partner with fashion TikTok creators for authentic content'
            },
            {
                'title': 'Cultural Moment Marketing',
                'priority': 'high',
                'description': 'Respectful participation in cultural celebrations',
                'action': 'Develop culturally sensitive campaign calendar'
            }
        ],
        'cultural_calendar': content_calendar,
        'next_actions': [
            'Execute Q4 planning kickoff',
            'Launch Hip-Hop History Month content',
            'Prepare Halloween campaign assets',
            'Begin Black Friday creative development'
        ]
    }
    
    # Find Crooks & Castles ranking
    rankings = intelligence_data.get('competitive_rankings', {})
    if 'Crooks & Castles' in rankings:
        report['executive_summary']['crooks_ranking'] = rankings['Crooks & Castles']['rank']
    
    return report

# Initialize data on startup
load_intelligence_data()
scan_assets()
generate_content_calendar()

@app.route('/')
def index():
    """Main dashboard"""
    try:
        return render_template('command_center_dashboard.html')
    except:
        # Fallback to a simpler template if the main one fails
        try:
            return render_template('enhanced_collaborative_index.html')
        except:
            # Ultimate fallback - return a simple HTML page
            return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crooks & Castles Command Center V2</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a1a; color: #fff; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: #2a2a2a; padding: 20px; border-radius: 8px; border-left: 4px solid #ff6b35; }
        .stat-number { font-size: 2em; font-weight: bold; color: #ff6b35; }
        .api-section { background: #2a2a2a; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .api-link { color: #ff6b35; text-decoration: none; display: block; margin: 10px 0; }
        .api-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏰 Crooks & Castles Command Center V2</h1>
            <p>Real Data Intelligence • Asset Management • Strategic Planning</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number" id="posts-count">Loading...</div>
                <div>Instagram Posts Analyzed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="videos-count">Loading...</div>
                <div>TikTok Videos Processed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="assets-count">Loading...</div>
                <div>Assets Available</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="calendar-count">Loading...</div>
                <div>Calendar Events Planned</div>
            </div>
        </div>
        
        <div class="api-section">
            <h2>📊 Intelligence Dashboard</h2>
            <a href="/api/intelligence" class="api-link">View Intelligence Data</a>
            <a href="/api/reports/weekly" class="api-link">Weekly Report</a>
            <a href="/api/reports/weekly/download" class="api-link">Download Weekly Report (JSON)</a>
        </div>
        
        <div class="api-section">
            <h2>📁 Asset Library</h2>
            <a href="/api/assets" class="api-link">View Asset Library</a>
            <div id="asset-list"></div>
        </div>
        
        <div class="api-section">
            <h2>📅 Strategic Calendar</h2>
            <a href="/api/calendar" class="api-link">View Content Calendar</a>
            <div id="calendar-summary"></div>
        </div>
        
        <div class="api-section">
            <h2>🏢 Agency Tracking</h2>
            <a href="/api/agency" class="api-link">High Voltage Digital Metrics</a>
        </div>
        
        <div class="api-section">
            <h2>⬆️ Upload Data</h2>
            <form action="/api/upload" method="post" enctype="multipart/form-data" style="margin-top: 10px;">
                <input type="file" name="file" accept=".jsonl,.json" style="margin-bottom: 10px;">
                <button type="submit" style="background: #ff6b35; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer;">Upload JSONL Data</button>
            </form>
        </div>
    </div>
    
    <script>
        // Load dashboard data
        fetch('/api/intelligence')
            .then(response => response.json())
            .then(data => {
                document.getElementById('posts-count').textContent = data.summary.total_posts_analyzed || 0;
                document.getElementById('videos-count').textContent = data.summary.total_tiktok_videos || 0;
            });
            
        fetch('/api/assets')
            .then(response => response.json())
            .then(data => {
                document.getElementById('assets-count').textContent = data.total_count || 0;
                const assetList = document.getElementById('asset-list');
                if (data.assets) {
                    let html = '<div style="margin-top: 10px;">';
                    Object.entries(data.assets).forEach(([id, asset]) => {
                        html += `<div style="margin: 5px 0;"><a href="/api/assets/${id}/download" class="api-link">📄 ${asset.filename}</a></div>`;
                    });
                    html += '</div>';
                    assetList.innerHTML = html;
                }
            });
            
        fetch('/api/calendar')
            .then(response => response.json())
            .then(data => {
                document.getElementById('calendar-count').textContent = data.all_events?.length || 0;
                const calendarSummary = document.getElementById('calendar-summary');
                if (data.quarterly_summary) {
                    const summary = data.quarterly_summary;
                    calendarSummary.innerHTML = `
                        <div style="margin-top: 10px;">
                            <p>📈 Total Budget: $${summary.total_budget?.toLocaleString() || 0}</p>
                            <p>🎯 Agency Deliverables: ${summary.agency_deliverables || 0}</p>
                            <p>🎨 Cultural Moments: ${summary.cultural_moments || 0}</p>
                            <p>💼 Commercial Campaigns: ${summary.commercial_campaigns || 0}</p>
                        </div>
                    `;
                }
            });
    </script>
</body>
</html>
            '''

@app.route('/api/intelligence')
def api_intelligence():
    """Get intelligence summary"""
    summary = {
        'summary': {
            'total_posts_analyzed': len(intelligence_data.get('instagram_posts', [])),
            'total_hashtags_tracked': len(intelligence_data.get('top_hashtags', [])),
            'total_tiktok_videos': len(intelligence_data.get('tiktok_videos', [])),
            'last_updated': intelligence_data.get('last_updated'),
            'data_sources': {
                'instagram': len(intelligence_data.get('instagram_posts', [])),
                'tiktok': len(intelligence_data.get('tiktok_videos', [])),
                'competitive': len(intelligence_data.get('competitive_rankings', {}))
            }
        },
        'competitive_rankings': intelligence_data.get('competitive_rankings', {}),
        'trending_hashtags': intelligence_data.get('top_hashtags', [])[:10],
        'cultural_moments': intelligence_data.get('cultural_moments', [])[:5],
        'tiktok_insights': intelligence_data.get('tiktok_analysis', {})
    }
    return jsonify(summary)

@app.route('/api/assets')
def api_assets():
    """Get asset library"""
    # Categorize assets
    categories = defaultdict(int)
    for asset in asset_library.values():
        categories[asset['category']] += 1
    
    return jsonify({
        'assets': asset_library,
        'categories': dict(categories),
        'total_count': len(asset_library)
    })

@app.route('/api/assets/<asset_id>/download')
def download_asset(asset_id):
    """Download an asset"""
    if asset_id not in asset_library:
        return jsonify({'error': 'Asset not found'}), 404
    
    asset = asset_library[asset_id]
    filepath = asset['filepath']
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(filepath, as_attachment=True, download_name=asset['filename'])

@app.route('/api/assets/<asset_id>/thumbnail')
def asset_thumbnail(asset_id):
    """Get asset thumbnail"""
    if asset_id not in asset_library:
        return jsonify({'error': 'Asset not found'}), 404
    
    asset = asset_library[asset_id]
    thumbnail_path = asset.get('thumbnail_path')
    
    if thumbnail_path and os.path.exists(thumbnail_path):
        return send_file(thumbnail_path)
    else:
        # Return default thumbnail or the original file
        return send_file(asset['filepath'])

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload and process files"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    try:
        file.save(filepath)
        
        # Analyze the file
        file_info = analyze_file(filepath, filename)
        if file_info:
            asset_id = str(uuid.uuid4())
            asset_library[asset_id] = file_info
            
            # If it's a data file, reprocess intelligence
            if filename.endswith(('.jsonl', '.json')):
                load_intelligence_data()
                return jsonify({
                    'success': True, 
                    'message': f'Data file processed: {filename}',
                    'asset_id': asset_id,
                    'records_processed': len(load_jsonl_file(filepath))
                })
            else:
                return jsonify({
                    'success': True,
                    'message': f'Asset uploaded: {filename}',
                    'asset_id': asset_id
                })
        else:
            return jsonify({'error': 'Failed to process file'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/calendar')
def api_calendar():
    """Get content calendar"""
    return jsonify(content_calendar)

@app.route('/api/agency')
def api_agency():
    """Get agency tracking data"""
    agency_data = {
        'high_voltage_digital': {
            'current_phase': 'Phase 1',
            'monthly_deliverables': 4,
            'current_budget': 4000,
            'next_phase_budget': 7500,
            'next_phase_deliverables': 7,
            'next_phase_date': '2025-11-01',
            'on_time_delivery': 100,
            'quality_score': 95,
            'client_satisfaction': 98,
            'deliverables_completed': 12,
            'deliverables_pending': 0,
            'budget_utilization': 85,
            'performance_metrics': {
                'content_quality': 95,
                'delivery_speed': 100,
                'client_communication': 98,
                'strategic_value': 92
            }
        }
    }
    return jsonify(agency_data)

@app.route('/api/reports/weekly')
def api_weekly_report():
    """Get weekly report"""
    report = generate_weekly_report()
    return jsonify(report)

@app.route('/api/reports/weekly/download')
def download_weekly_report():
    """Download weekly report as JSON"""
    report = generate_weekly_report()
    
    # Create temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(report, f, indent=2, default=str)
        temp_path = f.name
    
    return send_file(temp_path, as_attachment=True, 
                    download_name=f'crooks-weekly-report-{datetime.now().strftime("%Y-%m-%d")}.json')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
