from fastapi import APIRouter, Query

router = APIRouter()

@router.get("/")
async def executive_root():
    """Executive root endpoint"""
    return {
        "success": True,
        "message": "Executive API operational",
        "endpoints": ["/overview", "/kpis", "/reports"]
    }

@router.get("/overview")
async def executive_overview(days: int = Query(30, description="Days to include in overview")):
    """Get executive overview data"""
    return {
        "success": True,
        "time_period": f"Last {days} days",
        "overview": {
            "financial": {
                "revenue": 325750.45,
                "growth": "+12.5%",
                "profit_margin": "32%",
                "cac": "$24.50",
                "ltv": "$320.75",
                "roas": "4.5x"
            },
            "marketing": {
                "total_reach": 1245000,
                "engagement_rate": "4.2%",
                "conversion_rate": "3.2%",
                "active_campaigns": 8,
                "campaign_performance": "Above Target"
            },
            "product": {
                "total_products": 87,
                "new_releases": 12,
                "best_seller": "Signature Hoodie",
                "inventory_health": "92%"
            },
            "operations": {
                "fulfillment_rate": "98.5%",
                "average_shipping_time": "2.3 days",
                "return_rate": "4.2%",
                "customer_satisfaction": "4.8/5"
            },
            "strategic_initiatives": [
                {
                    "name": "International Expansion",
                    "status": "On Track",
                    "progress": 65,
                    "notes": "EU launch scheduled for Q4"
                },
                {
                    "name": "Sustainability Program",
                    "status": "On Track",
                    "progress": 40,
                    "notes": "Eco-friendly packaging rollout in progress"
                },
                {
                    "name": "Loyalty Program Revamp",
                    "status": "At Risk",
                    "progress": 25,
                    "notes": "Technical integration delays"
                }
            ]
        }
    }

@router.get("/kpis")
async def executive_kpis():
    """Get executive KPIs"""
    return {
        "success": True,
        "kpis": {
            "financial_kpis": [
                {"name": "Monthly Revenue", "value": "$325,750", "target": "$300,000", "status": "Above Target"},
                {"name": "Profit Margin", "value": "32%", "target": "30%", "status": "Above Target"},
                {"name": "Customer Acquisition Cost", "value": "$24.50", "target": "$25.00", "status": "On Target"},
                {"name": "Average Order Value", "value": "$101.00", "target": "$110.00", "status": "Below Target"},
                {"name": "Return on Ad Spend", "value": "4.5x", "target": "4.0x", "status": "Above Target"}
            ],
            "marketing_kpis": [
                {"name": "Social Media Engagement", "value": "4.2%", "target": "3.5%", "status": "Above Target"},
                {"name": "Email Open Rate", "value": "28%", "target": "25%", "status": "Above Target"},
                {"name": "Conversion Rate", "value": "3.2%", "target": "3.5%", "status": "Below Target"},
                {"name": "Brand Awareness", "value": "42%", "target": "45%", "status": "Below Target"},
                {"name": "Customer Retention", "value": "68%", "target": "65%", "status": "Above Target"}
            ],
            "operational_kpis": [
                {"name": "Inventory Turnover", "value": "5.2x", "target": "5.0x", "status": "Above Target"},
                {"name": "On-Time Delivery", "value": "98.5%", "target": "97%", "status": "Above Target"},
                {"name": "Return Rate", "value": "4.2%", "target": "5.0%", "status": "Above Target"},
                {"name": "Customer Satisfaction", "value": "4.8/5", "target": "4.5/5", "status": "Above Target"},
                {"name": "Website Uptime", "value": "99.95%", "target": "99.9%", "status": "On Target"}
            ]
        }
    }

@router.get("/reports")
async def executive_reports():
    """Get executive reports"""
    return {
        "success": True,
        "reports": [
            {
                "id": "rep1",
                "title": "Monthly Performance Report",
                "date": "2023-09-01",
                "type": "Financial",
                "summary": "Overall performance above target with 12.5% revenue growth",
                "url": "/reports/monthly-performance-sept2023.pdf"
            },
            {
                "id": "rep2",
                "title": "Marketing Campaign Analysis",
                "date": "2023-09-15",
                "type": "Marketing",
                "summary": "Fall campaign exceeding expectations with 4.5x ROAS",
                "url": "/reports/fall-campaign-analysis.pdf"
            },
            {
                "id": "rep3",
                "title": "Product Performance Review",
                "date": "2023-09-20",
                "type": "Product",
                "summary": "Signature Hoodie continues as bestseller, new releases showing strong initial performance",
                "url": "/reports/product-performance-q3.pdf"
            },
            {
                "id": "rep4",
                "title": "Strategic Initiative Update",
                "date": "2023-09-25",
                "type": "Strategy",
                "summary": "International expansion on track, loyalty program revamp facing technical challenges",
                "url": "/reports/strategic-initiatives-sept2023.pdf"
            }
        ]
    }
