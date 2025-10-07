from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from datetime import datetime, timedelta, timezone
from typing import Optional
import json

from ..database import get_db
from ..models import CompetitiveData

router = APIRouter()


def classify_threat_level(competitor: str) -> str:
    """Classify competitor threat level based on brand"""
    
    competitor_lower = competitor.lower()
    
    # High threat - direct streetwear competitors
    high_threat = [
        'supreme', 'bape', 'stussy', 'the hundreds', 'diamond supply',
        'huf', 'obey', 'mishka', 'been trill', 'pyrex', 'hood by air',
        'off-white', 'vlone', 'antisocialsocialclub', 'ftp', 'palace'
    ]
    
    # Medium threat - lifestyle/fashion brands
    medium_threat = [
        'nike', 'adidas', 'vans', 'converse', 'puma', 'reebok',
        'champion', 'carhartt', 'dickies', 'levis', 'guess',
        'tommy hilfiger', 'ralph lauren', 'lacoste'
    ]
    
    # Low threat - casual/mass market
    low_threat = [
        'hm', 'zara', 'uniqlo', 'gap', 'forever21', 'urban outfitters',
        'pacsun', 'tillys', 'zumiez', 'shein', 'fashion nova'
    ]
    
    for brand in high_threat:
        if brand in competitor_lower:
            return "high"
    
    for brand in medium_threat:
        if brand in competitor_lower:
            return "medium"
    
    for brand in low_threat:
        if brand in competitor_lower:
            return "low"
    
    # Default to medium if unknown
    return "medium"


@router.post("/import-json")
async def import_competitive_json(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import competitive intelligence from JSON or JSONL file (Apify export)"""
    
    if not (file.filename.endswith('.json') or file.filename.endswith('.jsonl')):
        raise HTTPException(400, "File must be JSON or JSONL")
    
    try:
        contents = await file.read()
        text_content = contents.decode('utf-8')
        
        # Parse based on file type
        if file.filename.endswith('.jsonl'):
            # JSONL: Each line is a separate JSON object
            data_items = []
            for line in text_content.split('\n'):
                line = line.strip()
                if line:
                    try:
                        data_items.append(json.loads(line))
                    except:
                        continue
        else:
            # JSON: Single object or array
            parsed = json.loads(text_content)
            if isinstance(parsed, list):
                data_items = parsed
            else:
                data_items = [parsed]
        
        imported = 0
        
        for item in data_items:
            try:
                # Determine platform and extract data
                platform = "unknown"
                competitor = None
                engagement = 0
                content_type = None
                post_url = None
                caption = None
                hashtags = []
                post_date = None
                
                # Instagram detection
                if 'ownerUsername' in item or 'username' in item:
                    platform = "instagram"
                    competitor = item.get('ownerUsername') or item.get('username')
                    engagement = (item.get('likesCount', 0) or 0) + (item.get('commentsCount', 0) or 0)
                    content_type = item.get('type', 'post')
                    post_url = item.get('url')
                    caption = item.get('caption')
                    hashtags = item.get('hashtags', [])
                    
                    # Parse date
                    timestamp = item.get('timestamp')
                    if timestamp:
                        try:
                            post_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        except:
                            pass
                
                # TikTok detection
                elif 'authorMeta' in item or 'author' in item:
                    platform = "tiktok"
                    author = item.get('authorMeta') or item.get('author', {})
                    competitor = author.get('name') if isinstance(author, dict) else str(author)
                    engagement = (item.get('diggCount', 0) or 0) + (item.get('commentCount', 0) or 0) + (item.get('shareCount', 0) or 0)
                    content_type = "video"
                    post_url = item.get('webVideoUrl') or item.get('videoUrl')
                    caption = item.get('text')
                    hashtags = [h.get('name') for h in item.get('hashtags', []) if isinstance(h, dict) and h.get('name')]
                    
                    # Parse date
                    create_time = item.get('createTime')
                    if create_time:
                        try:
                            post_date = datetime.fromtimestamp(int(create_time), tz=timezone.utc)
                        except:
                            pass
                
                # Generic social media detection
                elif 'likes' in item or 'comments' in item or 'shares' in item:
                    platform = item.get('platform', 'social_media')
                    competitor = item.get('account') or item.get('user') or item.get('brand')
                    engagement = (item.get('likes', 0) or 0) + (item.get('comments', 0) or 0) + (item.get('shares', 0) or 0)
                    content_type = item.get('type', 'post')
                    post_url = item.get('url') or item.get('link')
                    caption = item.get('text') or item.get('caption') or item.get('description')
                    hashtags = item.get('hashtags', [])
                
                if not competitor:
                    continue
                
                # Classify threat level
                threat_level = classify_threat_level(competitor)
                
                # Create competitive data record
                comp_data = CompetitiveData(
                    competitor=competitor,
                    platform=platform,
                    content_type=content_type,
                    engagement_count=engagement,
                    post_url=post_url,
                    caption=caption[:500] if caption else None,
                    hashtags=hashtags[:20] if hashtags else None,
                    post_date=post_date,
                    threat_level=threat_level,
                    raw_data=item
                )
                
                db.add(comp_data)
                imported += 1
                
            except Exception as e:
                continue
        
        db.commit()
        
        return {
            "success": True,
            "imported": imported,
            "message": f"Imported {imported} competitive data points"
        }
        
    except json.JSONDecodeError as e:
        raise HTTPException(400, f"Invalid JSON/JSONL format: {str(e)}")
    except Exception as e:
        raise HTTPException(400, f"Error importing file: {str(e)}")


@router.get("/dashboard")
def get_competitive_dashboard(
    days: int = 30,
    threat_level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get competitive intelligence dashboard"""
    
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days)
    
    query = db.query(CompetitiveData).filter(
        CompetitiveData.scraped_at >= start_date
    )
    
    if threat_level:
        query = query.filter(CompetitiveData.threat_level == threat_level)
    
    data = query.all()
    
    # Aggregate by competitor
    competitor_stats = {}
    for item in data:
        if item.competitor not in competitor_stats:
            competitor_stats[item.competitor] = {
                "competitor": item.competitor,
                "threat_level": item.threat_level,
                "total_posts": 0,
                "total_engagement": 0,
                "avg_engagement": 0,
                "platforms": set()
            }
        
        competitor_stats[item.competitor]["total_posts"] += 1
        competitor_stats[item.competitor]["total_engagement"] += item.engagement_count or 0
        competitor_stats[item.competitor]["platforms"].add(item.platform)
    
    # Calculate averages
    competitors = []
    for comp_name, stats in competitor_stats.items():
        stats["avg_engagement"] = int(stats["total_engagement"] / stats["total_posts"]) if stats["total_posts"] > 0 else 0
        stats["platforms"] = list(stats["platforms"])
        competitors.append(stats)
    
    # Sort by total engagement
    competitors.sort(key=lambda x: x["total_engagement"], reverse=True)
    
    return {
        "period_days": days,
        "total_data_points": len(data),
        "competitors_tracked": len(competitors),
        "competitors": competitors
    }


@router.get("/data")
def get_competitive_data(
    limit: int = 50,
    offset: int = 0,
    competitor: Optional[str] = None,
    platform: Optional[str] = None,
    threat_level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get competitive data with filters"""
    
    query = db.query(CompetitiveData)
    
    if competitor:
        query = query.filter(CompetitiveData.competitor == competitor)
    
    if platform:
        query = query.filter(CompetitiveData.platform == platform)
    
    if threat_level:
        query = query.filter(CompetitiveData.threat_level == threat_level)
    
    total = query.count()
    
    data = query.order_by(desc(CompetitiveData.scraped_at)).limit(limit).offset(offset).all()
    
    return {
        "data": [
            {
                "id": d.id,
                "competitor": d.competitor,
                "platform": d.platform,
                "content_type": d.content_type,
                "engagement_count": d.engagement_count,
                "post_url": d.post_url,
                "caption": d.caption,
                "hashtags": d.hashtags,
                "post_date": d.post_date.isoformat() if d.post_date else None,
                "threat_level": d.threat_level,
                "scraped_at": d.scraped_at.isoformat() if d.scraped_at else None
            }
            for d in data
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/brands")
def get_competitor_brands(db: Session = Depends(get_db)):
    """Get list of all competitor brands with threat levels"""
    
    competitors = db.query(
        CompetitiveData.competitor,
        CompetitiveData.threat_level,
        func.count(CompetitiveData.id).label('data_points')
    ).group_by(
        CompetitiveData.competitor,
        CompetitiveData.threat_level
    ).all()
    
    # Organize by threat level
    brands_by_threat = {
        "high_threat": [],
        "medium_threat": [],
        "low_threat": [],
        "unknown": []
    }
    
    threat_counts = {
        "high": 0,
        "medium": 0,
        "low": 0,
        "unknown": 0
    }
    
    for comp, threat, count in competitors:
        if threat == "high":
            brands_by_threat["high_threat"].append(comp)
            threat_counts["high"] += 1
        elif threat == "medium":
            brands_by_threat["medium_threat"].append(comp)
            threat_counts["medium"] += 1
        elif threat == "low":
            brands_by_threat["low_threat"].append(comp)
            threat_counts["low"] += 1
        else:
            brands_by_threat["unknown"].append(comp)
            threat_counts["unknown"] += 1
    
    return {
        "total": len(competitors),
        "threat_levels": threat_counts,
        "brands": brands_by_threat
    }


@router.get("/platforms")
def get_platforms(db: Session = Depends(get_db)):
    """Get list of platforms being tracked"""
    
    platforms = db.query(
        CompetitiveData.platform,
        func.count(CompetitiveData.id).label('count')
    ).group_by(CompetitiveData.platform).all()
    
    return {
        "platforms": [
            {
                "name": platform,
                "count": count
            }
            for platform, count in platforms
        ]
    }


@router.delete("/data/{data_id}")
def delete_competitive_data(data_id: int, db: Session = Depends(get_db)):
    """Delete a competitive data point"""
    
    data = db.query(CompetitiveData).filter(CompetitiveData.id == data_id).first()
    
    if not data:
        raise HTTPException(404, "Data not found")
    
    db.delete(data)
    db.commit()
    
    return {"success": True}
