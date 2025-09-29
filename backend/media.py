from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional

router = APIRouter()

@router.get("/")
async def media_root():
    """Media root endpoint"""
    return {
        "success": True,
        "message": "Media API operational",
        "endpoints": ["/library", "/analytics", "/upload"]
    }

@router.get("/library")
async def media_library():
    """Get media library data"""
    return {
        "success": True,
        "media": {
            "total_assets": 245,
            "categories": {
                "product_photos": 120,
                "lifestyle": 75,
                "campaign": 35,
                "video": 15
            },
            "recent_uploads": [
                {
                    "id": "med1",
                    "name": "Fall_Collection_Hero_01.jpg",
                    "type": "image/jpeg",
                    "size": 2450000,
                    "dimensions": "2000x1500",
                    "uploaded": "2023-09-25T14:30:00",
                    "category": "campaign",
                    "tags": ["fall", "hero", "collection"],
                    "url": "/media/Fall_Collection_Hero_01.jpg",
                    "thumbnail": "/media/thumbnails/Fall_Collection_Hero_01.jpg"
                },
                {
                    "id": "med2",
                    "name": "Product_Hoodie_Black_Front.jpg",
                    "type": "image/jpeg",
                    "size": 1850000,
                    "dimensions": "1800x2400",
                    "uploaded": "2023-09-24T10:15:00",
                    "category": "product_photos",
                    "tags": ["product", "hoodie", "black"],
                    "url": "/media/Product_Hoodie_Black_Front.jpg",
                    "thumbnail": "/media/thumbnails/Product_Hoodie_Black_Front.jpg"
                },
                {
                    "id": "med3",
                    "name": "Lifestyle_Urban_Streetwear_05.jpg",
                    "type": "image/jpeg",
                    "size": 3250000,
                    "dimensions": "2200x1600",
                    "uploaded": "2023-09-23T16:45:00",
                    "category": "lifestyle",
                    "tags": ["lifestyle", "urban", "streetwear"],
                    "url": "/media/Lifestyle_Urban_Streetwear_05.jpg",
                    "thumbnail": "/media/thumbnails/Lifestyle_Urban_Streetwear_05.jpg"
                },
                {
                    "id": "med4",
                    "name": "Fall_Collection_Promo.mp4",
                    "type": "video/mp4",
                    "size": 24500000,
                    "dimensions": "1920x1080",
                    "duration": "00:01:25",
                    "uploaded": "2023-09-22T11:30:00",
                    "category": "video",
                    "tags": ["promo", "fall", "collection", "video"],
                    "url": "/media/Fall_Collection_Promo.mp4",
                    "thumbnail": "/media/thumbnails/Fall_Collection_Promo.jpg"
                },
                {
                    "id": "med5",
                    "name": "Product_Tshirt_White_Front.jpg",
                    "type": "image/jpeg",
                    "size": 1650000,
                    "dimensions": "1800x2400",
                    "uploaded": "2023-09-21T09:20:00",
                    "category": "product_photos",
                    "tags": ["product", "tshirt", "white"],
                    "url": "/media/Product_Tshirt_White_Front.jpg",
                    "thumbnail": "/media/thumbnails/Product_Tshirt_White_Front.jpg"
                }
            ],
            "collections": [
                {
                    "name": "Fall Collection 2023",
                    "asset_count": 45,
                    "created": "2023-08-15T10:00:00",
                    "thumbnail": "/media/thumbnails/Fall_Collection_Hero_01.jpg"
                },
                {
                    "name": "Product Catalog",
                    "asset_count": 120,
                    "created": "2023-07-01T09:00:00",
                    "thumbnail": "/media/thumbnails/Product_Hoodie_Black_Front.jpg"
                },
                {
                    "name": "Lifestyle Imagery",
                    "asset_count": 75,
                    "created": "2023-06-15T14:30:00",
                    "thumbnail": "/media/thumbnails/Lifestyle_Urban_Streetwear_05.jpg"
                }
            ]
        }
    }

@router.get("/analytics")
async def media_analytics():
    """Get media analytics data"""
    return {
        "success": True,
        "analytics": {
            "usage_metrics": {
                "total_views": 24500,
                "total_downloads": 1250,
                "total_shares": 850,
                "average_views_per_asset": 100
            },
            "top_performing_assets": [
                {
                    "id": "med1",
                    "name": "Fall_Collection_Hero_01.jpg",
                    "views": 2450,
                    "downloads": 120,
                    "shares": 85,
                    "engagement_rate": "10.2%"
                },
                {
                    "id": "med4",
                    "name": "Fall_Collection_Promo.mp4",
                    "views": 1850,
                    "downloads": 95,
                    "shares": 120,
                    "engagement_rate": "11.6%"
                },
                {
                    "id": "med3",
                    "name": "Lifestyle_Urban_Streetwear_05.jpg",
                    "views": 1650,
                    "downloads": 75,
                    "shares": 65,
                    "engagement_rate": "8.5%"
                }
            ],
            "usage_by_channel": {
                "website": {
                    "views": 12500,
                    "downloads": 450,
                    "shares": 250
                },
                "social_media": {
                    "views": 8500,
                    "downloads": 350,
                    "shares": 450
                },
                "email_campaigns": {
                    "views": 3500,
                    "downloads": 150,
                    "shares": 150
                }
            },
            "storage_metrics": {
                "total_storage": "45.2 GB",
                "available_storage": "154.8 GB",
                "storage_used_percentage": "22.6%",
                "monthly_growth": "+2.5 GB"
            }
        }
    }

@router.post("/upload")
async def media_upload(file: UploadFile = File(...), 
                      name: Optional[str] = Form(None),
                      category: str = Form(...),
                      tags: str = Form(...)):
    """Upload media file"""
    return {
        "success": True,
        "message": "File uploaded successfully",
        "file_info": {
            "id": "new_med_id",
            "original_name": file.filename,
            "name": name if name else file.filename,
            "type": file.content_type,
            "size": 1024000,  # Mock size
            "category": category,
            "tags": tags.split(","),
            "uploaded": "2023-09-29T10:00:00",
            "url": f"/media/{file.filename}",
            "thumbnail": f"/media/thumbnails/{file.filename}"
        }
    }
