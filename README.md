# 🏰 Crooks & Castles Command Center V2

**Advanced Brand Intelligence & Cultural Radar System**

A comprehensive competitive intelligence platform that transforms social media data into actionable strategic insights for Crooks & Castles streetwear brand positioning.

## 🚀 Features

### 📊 **Brand Intelligence Dashboard**
- **Real-time competitive rankings** across 12 streetwear brands
- **Engagement metrics analysis** with performance benchmarking
- **Brand positioning insights** with strategic gap identification
- **Performance tracking** with trend analysis

### 🔍 **Cultural Radar System**
- **Hashtag velocity tracking** for emerging trend detection
- **TikTok cultural intelligence** for Gen Z insights
- **Viral content identification** and pattern analysis
- **Cross-platform trend validation**

### 🎯 **Competitive Intelligence**
- **Multi-platform monitoring** (Instagram, TikTok, hashtag trends)
- **Automated data processing** from Apify scrapers
- **Strategic insights generation** with priority levels
- **Actionable recommendations** for brand positioning

### 📈 **Data Integration**
- **JSONL file processing** from Apify Instagram Scraper
- **Hashtag trend analysis** from social media monitoring
- **TikTok cultural moment detection** for youth market insights
- **Real-time dashboard updates** with animated visualizations

## 🛠 Technology Stack

- **Backend**: Flask (Python 3.11)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Data Processing**: Pandas, JSON processing
- **Styling**: Custom CSS with Command Center design system
- **Deployment**: Render.com
- **Data Sources**: Apify scrapers (Instagram, TikTok, Hashtags)

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+ (for development tools)
- Apify account with active scrapers
- Modern web browser

## ⚡ Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/Jillian-ignited/Crooks-Command-Center-V2.git
cd Crooks-Command-Center-V2
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Application
```bash
python app.py
```

### 4. Access Dashboard
Open `http://localhost:5000` in your browser

## 🔧 Configuration

### Environment Variables
```bash
FLASK_ENV=production
FLASK_DEBUG=false
PORT=5000
```

### Apify Integration
1. **Instagram Scraper**: Monitor 12 competitor brands
2. **Hashtag Scraper**: Track 15 strategic hashtags
3. **TikTok Scraper**: Analyze cultural moments and trends

## 📊 Data Sources

### **Monitored Brands (12 Total)**
- **Crooks & Castles** (baseline)
- **Supreme** (hype generation leader)
- **Stussy** (heritage revival expert)
- **Fear of God Essentials** (premium positioning)
- **Hellstar** (emerging competitor)
- **Diamond Supply Co.** (established competitor)
- **LRG** (legacy streetwear)
- **Ed Hardy** (Y2K revival)
- **Von Dutch** (heritage brand)
- **Reason Clothing** (direct competitor)
- **Godspeed** (emerging brand)
- **Smoke Rise** (contemporary competitor)

### **Strategic Hashtags (15 Total)**
- `#streetwear` - Core category monitoring
- `#crooksandcastles` - Brand-specific tracking
- `#y2kfashion` - Trend analysis
- `#vintagestreetwear` - Heritage market
- `#streetweararchive` - Collector culture
- `#streetweardrop` - Release culture
- `#heritagebrand` - Brand positioning
- `#supremedrop` - Competitor analysis
- `#hellstar` - Emerging competitor tracking
- `#fearofgod` - Premium segment
- `#diamondsupply` - Established competitor
- `#edhardy` - Y2K revival tracking
- `#vondutch` - Heritage competitor
- `#streetwearculture` - Cultural insights
- `#hypebeast` - Influencer culture

### **TikTok Search Terms (10 Total)**
- `"crooks and castles"` - Direct brand mentions
- `"streetwear haul"` - Shopping behavior
- `"streetwear drop"` - Release reactions
- `"y2k fashion"` - Trend participation
- `"vintage streetwear"` - Heritage interest
- `"thrift streetwear"` - Resale culture
- `"streetwear archive"` - Collector content
- `"supreme unboxing"` - Competitor analysis
- `"hellstar outfit"` - Styling insights
- `"fear of god essentials"` - Premium segment

## 📅 Automated Scheduling

### **Data Collection Schedule**
- **Instagram Brands**: Daily at 7:00 AM CST
- **Hashtag Monitoring**: Monday/Wednesday/Friday at 9:00 AM CST
- **TikTok Cultural Intelligence**: Sunday/Wednesday at 10:00 AM CST

### **Reporting Timeline**
- **Monday Morning**: Fresh weekend data ready for strategic planning
- **Wednesday**: Mid-week trend validation and momentum analysis
- **Weekly Reports**: Comprehensive intelligence delivered Monday AM

## 💰 Cost Structure

### **Apify Monthly Budget: $49**
- **Instagram Monitoring**: $37.50 (25k results)
- **Hashtag Tracking**: $7.20 (1.2k results, 3x weekly)
- **TikTok Intelligence**: $10.00 (2k results, 2x weekly)
- **Total**: $54.70 (slightly over budget but comprehensive coverage)

## 📈 Usage Guide

### **1. Upload Intelligence Data**
1. Download JSONL files from Apify scrapers
2. Navigate to Brand Intelligence tab
3. Drag & drop JSONL files into upload zone
4. Watch automated analysis and insights generation

### **2. Monitor Cultural Trends**
1. Switch to Cultural Radar tab
2. Review trending hashtags with velocity indicators
3. Analyze TikTok cultural moments
4. Identify emerging opportunities

### **3. Competitive Analysis**
1. Access Competitive Analysis tab
2. Review strategic insights with priority levels
3. Monitor competitor activity levels
4. Generate actionable recommendations

### **4. Strategic Planning**
1. Export insights for team meetings
2. Use competitive rankings for positioning decisions
3. Leverage cultural trends for content strategy
4. Implement recommended actions

## 🎯 Key Metrics

### **Competitive Intelligence**
- **Brand Rankings**: Position among 12 competitors
- **Engagement Gaps**: Performance vs. top performers
- **Content Frequency**: Posting activity comparison
- **Cultural Relevance**: Trend participation analysis

### **Cultural Radar**
- **Hashtag Velocity**: Trend acceleration rates
- **Viral Content**: High-engagement post identification
- **TikTok Moments**: Gen Z cultural insights
- **Cross-Platform Validation**: Trend consistency

### **Strategic Insights**
- **Priority Levels**: High/Medium/Low action items
- **Opportunity Identification**: Market gaps and trends
- **Competitive Advantages**: Unique positioning opportunities
- **Risk Assessment**: Brand reputation and market threats

## 🚀 Deployment

### **Render.com Deployment**
1. Connect GitHub repository
2. Configure build settings:
   ```yaml
   buildCommand: pip install -r requirements.txt
   startCommand: gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 30 app:app
   ```
3. Set environment variables
4. Deploy and monitor

### **Production Considerations**
- **SSL Certificate**: Automatic via Render
- **Custom Domain**: Configure DNS settings
- **Monitoring**: Built-in Render monitoring
- **Scaling**: Automatic based on traffic

## 📊 Sample Insights

### **Competitive Intelligence Example**
> "Crooks & Castles ranks #9/12 with 1.2k average engagement. Supreme leads with 12.5k (10x gap). Strategic priority: Increase posting frequency from 0 to 3-5 posts/week to match competitor activity levels."

### **Cultural Radar Example**
> "Y2K fashion hashtag showing +340% velocity this week. Archive Medusa pieces trending on resale platforms. Opportunity: Launch 'Archive Remastered' micro-drop targeting nostalgic millennials."

### **TikTok Intelligence Example**
> "'Streetwear drop' content up 2.3x this week with 340 videos. Gen Z engagement patterns show authentic reactions vs. manufactured hype. Insight: Focus on genuine cultural moments over forced viral attempts."

## 🔄 Data Flow

```
Apify Scrapers → JSONL Files → Command Center Upload → 
Data Processing → Competitive Analysis → Strategic Insights → 
Dashboard Visualization → Actionable Recommendations
```

## 🛡 Security

- **Data Privacy**: No personal data collection
- **Secure Processing**: Local file processing only
- **API Security**: Environment variable protection
- **Access Control**: Single-user dashboard design

## 📞 Support

### **Technical Issues**
- Check browser console for JavaScript errors
- Verify JSONL file format compliance
- Ensure stable internet connection for uploads

### **Data Questions**
- Validate Apify scraper configurations
- Confirm scheduled run completions
- Review data export formats

### **Strategic Insights**
- Interpret competitive rankings in market context
- Validate cultural trends with additional sources
- Cross-reference TikTok insights with Instagram data

## 🔮 Future Enhancements

### **Phase 2 Features**
- **Real-time API integration** with Apify
- **Automated report generation** and email delivery
- **Advanced analytics** with predictive modeling
- **Multi-brand comparison** tools

### **Phase 3 Capabilities**
- **AI-powered insights** generation
- **Sentiment analysis** integration
- **Influencer identification** and tracking
- **ROI measurement** for strategic actions

## 📝 License

Private repository for Crooks & Castles internal use only.

## 🏆 Success Metrics

### **Intelligence Quality**
- **Data Accuracy**: 95%+ competitive ranking precision
- **Trend Prediction**: 48-72 hour cultural moment detection
- **Strategic Value**: Actionable insights per weekly report

### **Operational Efficiency**
- **Processing Speed**: <30 seconds for JSONL analysis
- **Update Frequency**: Real-time dashboard refresh
- **Cost Effectiveness**: <$55/month for comprehensive intelligence

---

**Built with ❤️ for Crooks & Castles strategic dominance in streetwear culture**

*Last Updated: September 2025*
