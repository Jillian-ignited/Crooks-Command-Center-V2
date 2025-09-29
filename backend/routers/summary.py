from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def summary_root():
    """Summary root endpoint"""
    return {
        "success": True,
        "message": "Summary API operational",
        "endpoints": ["/dashboard", "/performance", "/insights"]
    }

@router.get("/dashboard")
async def summary_dashboard():
    """Get summary dashboard data"""
    return {
        "success": True,
        "summary": {
            "business_overview": {
                "revenue": {
                    "value": "$325,750",
                    "trend": "+12.5%",
                    "status": "Above Target"
                },
                "orders": {
                    "value": "2,450",
                    "trend": "+8.2%",
                    "status": "On Target"
                },
                "customers": {
                    "value": "2,450",
                    "new": "875",
                    "returning": "1,575",
                    "trend": "+15.3%"
                },
                "conversion_rate": {
                    "value": "3.2%",
                    "trend": "+0.5%",
                    "status": "Below Target"
                }
            },
            "marketing_highlights": {
                "social_engagement": {
                    "value": "4.2%",
                    "trend": "+0.8%",
                    "status": "Above Target"
                },
                "email_performance": {
                    "open_rate": "28%",
                    "click_rate": "3.5%",
                    "trend": "+2.1%"
                },
                "top_campaign": "Fall Collection Launch",
                "campaign_performance": "4.5x ROAS"
            },
            "product_highlights": {
                "top_seller": "Signature Hoodie - Black",
                "new_releases": 12,
                "inventory_health": "92%",
                "product_performance": {
                    "above_target": 45,
                    "on_target": 32,
                    "below_target": 10
                }
            },
            "content_highlights": {
                "top_performing": "Behind the Scenes: Fall Collection",
                "content_published": 72,
                "content_scheduled": 15,
                "avg_engagement": "4.8%"
            },
            "key_alerts": [
                {
                    "type": "positive",
                    "message": "Social media engagement up 15% this month"
                },
                {
                    "type": "warning",
                    "message": "Inventory low for 12 products"
                },
                {
                    "type": "negative",
                    "message": "Website conversion rate below target"
                },
                {
                    "type": "positive",
                    "message": "Email open rates exceeding industry average by 10%"
                }
            ]
        }
    }

@router.get("/performance")
async def summary_performance():
    """Get summary performance data"""
    return {
        "success": True,
        "performance": {
            "kpi_summary": [
                {
                    "category": "Financial",
                    "kpis": [
                        {"name": "Revenue", "value": "$325,750", "target": "$300,000", "status": "Above Target"},
                        {"name": "Profit Margin", "value": "32%", "target": "30%", "status": "Above Target"},
                        {"name": "Average Order Value", "value": "$101.00", "target": "$110.00", "status": "Below Target"},
                        {"name": "Customer Acquisition Cost", "value": "$24.50", "target": "$25.00", "status": "On Target"}
                    ]
                },
                {
                    "category": "Marketing",
                    "kpis": [
                        {"name": "Social Engagement", "value": "4.2%", "target": "3.5%", "status": "Above Target"},
                        {"name": "Email Open Rate", "value": "28%", "target": "25%", "status": "Above Target"},
                        {"name": "Conversion Rate", "value": "3.2%", "target": "3.5%", "status": "Below Target"},
                        {"name": "ROAS", "value": "4.5x", "target": "4.0x", "status": "Above Target"}
                    ]
                },
                {
                    "category": "Operations",
                    "kpis": [
                        {"name": "Fulfillment Rate", "value": "98.5%", "target": "97%", "status": "Above Target"},
                        {"name": "On-Time Delivery", "value": "95.2%", "target": "95%", "status": "On Target"},
                        {"name": "Return Rate", "value": "4.2%", "target": "5.0%", "status": "Above Target"},
                        {"name": "Customer Satisfaction", "value": "4.8/5", "target": "4.5/5", "status": "Above Target"}
                    ]
                }
            ],
            "trend_analysis": {
                "revenue_trend": [
                    {"month": "April", "value": 250000},
                    {"month": "May", "value": 265000},
                    {"month": "June", "value": 280000},
                    {"month": "July", "value": 290000},
                    {"month": "August", "value": 310000},
                    {"month": "September", "value": 325750}
                ],
                "engagement_trend": [
                    {"month": "April", "value": 3.2},
                    {"month": "May", "value": 3.5},
                    {"month": "June", "value": 3.7},
                    {"month": "July", "value": 3.9},
                    {"month": "August", "value": 4.0},
                    {"month": "September", "value": 4.2}
                ],
                "customer_growth": [
                    {"month": "April", "value": 1850},
                    {"month": "May", "value": 1950},
                    {"month": "June", "value": 2050},
                    {"month": "July", "value": 2150},
                    {"month": "August", "value": 2300},
                    {"month": "September", "value": 2450}
                ]
            }
        }
    }

@router.get("/insights")
async def summary_insights():
    """Get summary insights data"""
    return {
        "success": True,
        "insights": {
            "key_insights": [
                {
                    "title": "Social Media Strategy Success",
                    "description": "Video content is driving 40% higher engagement than static images across all platforms.",
                    "recommendation": "Increase video content production by 25% for Q4 campaigns."
                },
                {
                    "title": "Product Category Performance",
                    "description": "Hoodie and outerwear categories showing 35% higher conversion rates than other categories.",
                    "recommendation": "Feature hoodies and outerwear prominently in Q4 marketing campaigns."
                },
                {
                    "title": "Customer Retention Opportunity",
                    "description": "Customers who make a second purchase within 30 days have 65% higher lifetime value.",
                    "recommendation": "Implement 30-day post-purchase email sequence with personalized recommendations."
                },
                {
                    "title": "Geographic Expansion Potential",
                    "description": "Orders from Midwest region increased 28% with minimal marketing investment.",
                    "recommendation": "Allocate 15% of Q4 marketing budget to targeted campaigns in Midwest cities."
                }
            ],
            "market_trends": [
                {
                    "trend": "Sustainable Materials",
                    "relevance": 9.2,
                    "opportunity": "High",
                    "description": "Growing consumer demand for sustainable and eco-friendly materials in streetwear."
                },
                {
                    "trend": "Limited Edition Drops",
                    "relevance": 8.8,
                    "opportunity": "High",
                    "description": "Continued strong performance of limited availability products creating urgency."
                },
                {
                    "trend": "Streetwear Collaborations",
                    "relevance": 8.5,
                    "opportunity": "Medium",
                    "description": "Cross-brand collaborations driving high engagement and new customer acquisition."
                },
                {
                    "trend": "Digital Experiences",
                    "relevance": 8.2,
                    "opportunity": "High",
                    "description": "AR/VR product experiences increasing conversion rates by up to 40%."
                }
            ],
            "competitive_position": {
                "market_share": "8.5%",
                "position": "Growth Challenger",
                "strengths": ["Brand Loyalty", "Social Engagement", "Product Quality"],
                "opportunities": ["International Expansion", "Product Line Extension", "Digital Experience"],
                "key_competitors": [
                    {"name": "Supreme", "market_share": "12%", "threat_level": "High"},
                    {"name": "Off-White", "market_share": "8%", "threat_level": "Medium"},
                    {"name": "Fear of God", "market_share": "6%", "threat_level": "Medium"}
                ]
            }
        }
    }
