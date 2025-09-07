# Crooks & Castles Content Machine - GitHub Starter Pack

## 🎯 **Overview**
This is the exact front-end experience extracted from the working Crooks & Castles Command Center, optimized for deployment on Render with Flask + Gunicorn.

## 🚀 **How to Run on Render**

### **Prerequisites**
- GitHub repository with this code
- Render account

### **Deployment Steps**
1. **Connect Repository**: Link your GitHub repo to Render
2. **Build Command**: `pip install -r requirements.txt`
3. **Start Command**: `gunicorn app:app`
4. **Environment**: Python 3.11

### **Required Folders**
```
├── src/static/
│   ├── index_enhanced_planning.html
│   └── assets/
│       └── _assets_manifest.json
├── data/
│   └── tactical_calendar.json
├── agency_reports/
│   └── report_sample.csv
├── app.py (your Flask application)
├── requirements.txt
└── README.md
```

## 🔌 **API Endpoints**

The UI calls these endpoints that your Flask app should implement:

### **GET /api/calendar**
Returns calendar data for different timeframes.
```json
{
  "calendar_data": [
    {
      "date": "2025-09-07",
      "day_name": "Sunday", 
      "formatted_date": "Sep 07",
      "posts": []
    }
  ],
  "success": true,
  "view_type": "7day"
}
```

### **GET /api/assets**
Returns asset library data.
```json
[
  {
    "id": "asset_id",
    "original_name": "Asset Name",
    "category": "Social Media",
    "badge_score": 95,
    "cultural_relevance": "Description",
    "created_date": "2025-09-07"
  }
]
```

### **GET /api/reports/agency**
Returns agency tracking metrics.
```json
{
  "overall_progress": 55.6,
  "phase": 1,
  "monthly_budget": 4000,
  "deliverables": {
    "social_posts": {"target": 12, "delivered": 6, "percentage": 50.0},
    "ad_creatives": {"target": 4, "delivered": 8, "percentage": 200.0},
    "email_campaigns": {"target": 2, "delivered": 0, "percentage": 0.0}
  }
}
```

### **POST /api/upload**
Handles file uploads.
```json
{
  "success": true,
  "asset": {
    "id": "new_asset_id",
    "name": "uploaded_file.png"
  }
}
```

### **GET /api/download/<id>**
Returns download URL for assets.
```json
{
  "url": "/static/assets/asset_file.png"
}
```

## 📊 **Data Files**

### **data/tactical_calendar.json**
Contains the 7-day tactical calendar covering 2025-09-07 to 2025-09-13 in America/Chicago timezone.

### **agency_reports/report_sample.csv**
Sample performance data with headers: date,channel,spend,impressions,clicks,conversions,revenue

## 🎨 **Assets**
All asset references in the HTML point to `/static/assets/<filename>`. The `_assets_manifest.json` tracks all referenced files.

## 🔧 **Technical Notes**
- HTML is cleaned of external Manus URLs
- All paths are relative to the application root
- CSS and JavaScript are embedded in the HTML
- No external dependencies for the frontend
- Responsive design for mobile and desktop

## 📈 **Features**
- **Calendar Planning**: 7/30/60/90-day strategic views
- **Asset Library**: Badge Test scoring system
- **Agency Tracking**: Real-time progress monitoring
- **Cultural Alignment**: Hispanic Heritage Month, Hip Hop History
- **Dynamic Content**: Monday Night Football, NFL Season

## 🎯 **Acceptance Criteria**
✅ HTML loads without external Manus URLs  
✅ All asset paths resolve to `/static/assets/`  
✅ Calendar covers 2025-09-07 → 2025-09-13  
✅ CSV parses with correct headers and realistic metrics  

---

**This starter pack reproduces the exact working experience from the live Crooks & Castles Command Center.**

