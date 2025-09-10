# KyndVibes Command Center

A sophisticated brand management and content planning platform for KyndVibes High Frequency Apparel.

## Features

### 🎨 Brand Asset Management
- **Thumbnail Generation** - Automatic thumbnails for all file types
- **Brand Compliance Checking** - Validates assets against KyndVibes peacock color palette
- **Campaign Tagging** - Organize assets by campaigns and collections
- **Upload & Processing** - Drag & drop file uploads with metadata extraction

### 📅 Dynamic Calendar Planning
- **Rolling Calendar** - Dynamic timeline for ongoing planning
- **Campaign Templates** - Pre-built templates for product launches, Frequency Collective, seasonal drops
- **Milestone Tracking** - Automatic milestone creation and progress tracking
- **Deadline Management** - Upcoming deadline alerts and urgency indicators

### 🎯 Content Planning
- **Gap Analysis** - Identify missing assets for campaigns
- **Asset Requirements** - Template-based asset requirement mapping
- **Production Timelines** - Recommended timelines based on campaign type
- **Progress Tracking** - Real-time campaign and asset completion tracking

### 🎨 KyndVibes Branding
- **Peacock Color Palette** - Deep Teal, Vibrant Turquoise, Bright Pink, Rich Purple, Lime Green
- **Sophisticated Typography** - Playfair Display, Dancing Script, Inter fonts
- **BOHO Aesthetic** - Elegant, refined design matching Shopify BOHO theme
- **Brand Elements** - "Kynd Vibes" script logo, energy rays, talisman symbolism

## Deployment to Render

### Prerequisites
- Render account
- Git repository with this code

### Quick Deploy
1. **Connect Repository** to Render
2. **Service Type**: Web Service
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `gunicorn --config gunicorn.conf.py app:app`

### Environment Variables
```
FLASK_ENV=production
FLASK_DEBUG=false
PYTHON_VERSION=3.11.0
```

### File Structure
```
kyndvibes-command-center/
├── app.py                 # Main Flask application
├── asset_manager.py       # Asset management system
├── calendar_manager.py    # Dynamic calendar system
├── requirements.txt       # Python dependencies
├── render.yaml           # Render deployment config
├── gunicorn.conf.py      # Production server config
├── Procfile              # Process definition
├── templates/
│   └── index.html        # Main interface
├── static/
│   ├── css/style.css     # KyndVibes styling
│   ├── js/script.js      # Frontend functionality
│   └── thumbnails/       # Generated thumbnails
├── uploads/              # File uploads (persistent disk)
├── data/                 # Calendar and event data
└── README.md            # This file
```

### Persistent Storage
- **Disk Mount**: `/opt/render/project/src/uploads` (1GB)
- **Purpose**: Store uploaded assets, thumbnails, and metadata
- **Backup**: Automatic Render disk snapshots

## API Endpoints

### Calendar Management
- `GET /api/calendar` - Get calendar events
- `POST /api/calendar/events` - Create new event
- `PUT /api/calendar/events/<id>` - Update event
- `DELETE /api/calendar/events/<id>` - Delete event
- `POST /api/calendar/campaigns` - Create campaign from template
- `GET /api/calendar/deadlines` - Get upcoming deadlines
- `GET /api/calendar/progress/<id>` - Get campaign progress

### Asset Management
- `GET /api/assets` - Get all assets
- `POST /api/upload` - Upload new asset
- `GET /uploads/<filename>` - Access uploaded files

### Content Planning
- `GET /api/content-planning/campaign-requirements/<type>` - Get campaign requirements
- `GET /api/content-planning/gap-analysis` - Analyze content gaps
- `GET /api/content-planning/checklist/<type>` - Get asset checklist

### System
- `GET /healthz` - Health check
- `GET /api/deliverables` - Get project deliverables

## Campaign Templates

### Product Launch
- **Duration**: 30 days
- **Milestones**: Concept → Asset Creation → Review → Final Assets → Launch
- **Required Assets**: Hero image, product shots, lifestyle photos, social media posts, email header, website banner

### Frequency Collective
- **Duration**: 21 days  
- **Milestones**: Recruitment → Content Creation → UGC Collection → Launch
- **Required Assets**: Ambassador photos, UGC templates, recruitment graphics, social media kit, campus materials

### Seasonal Drop
- **Duration**: 45 days
- **Milestones**: Planning → Photoshoot Prep → Execution → Processing → Marketing → Launch
- **Required Assets**: Collection hero, individual products, styling shots, countdown graphics, email campaign, website assets

## Brand Compliance

### Color Palette Validation
- Automatically detects brand colors in uploaded images
- Provides compliance score and recommendations
- Suggests improvements for brand consistency

### Format Optimization
- Validates file formats for web use
- Checks image dimensions for social media
- Provides format conversion recommendations

### Asset Requirements
- Maps assets to campaign requirements
- Tracks completion status
- Identifies missing assets

## Usage

### Creating a Campaign
1. Navigate to Calendar section
2. Click "Create Campaign"
3. Select template (Product Launch, Frequency Collective, Seasonal Drop)
4. Set launch date and campaign title
5. System automatically creates milestone timeline

### Uploading Assets
1. Go to Brand Assets section
2. Drag & drop files or click to browse
3. Add campaign tags and asset type
4. System processes file and generates thumbnail
5. Brand compliance report generated automatically

### Planning Content
1. Use Gap Analysis to identify missing assets
2. Review Asset Checklist for campaign requirements
3. Track progress in Calendar view
4. Monitor deadlines in Upcoming Deadlines section

## Support

For technical issues or feature requests, contact the development team or submit issues through the repository.

## License

Proprietary - KyndVibes High Frequency Apparel

