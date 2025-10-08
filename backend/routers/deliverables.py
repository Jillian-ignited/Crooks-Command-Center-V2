from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from datetime import datetime, timezone
from typing import Optional
import csv
from io import StringIO

from ..database import get_db
from ..models import Deliverable

router = APIRouter()


@router.get("/")
def get_deliverables(
    phase: Optional[str] = None,
    status: Optional[str] = None,
    deliverable_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get all deliverables with optional filters"""
    
    query = db.query(Deliverable)
    
    if phase:
        query = query.filter(Deliverable.phase == phase)
    
    if status:
        query = query.filter(Deliverable.status == status)
    
    if deliverable_type:
        query = query.filter(Deliverable.deliverable_type == deliverable_type)
    
    total = query.count()
    deliverables = query.order_by(Deliverable.due_date).limit(limit).offset(offset).all()
    
    return {
        "deliverables": [
            {
                "id": d.id,
                "title": d.title,
                "description": d.description,
                "type": d.type,
                "deliverable_type": d.deliverable_type,
                "status": d.status,
                "priority": d.priority,
                "assigned_to": d.assigned_to,
                "due_date": d.due_date.isoformat() if d.due_date else None,
                "completed_at": d.completed_at.isoformat() if d.completed_at else None,
                "phase": d.phase,
                "dependencies": d.dependencies,
                "blocks": d.blocks,
                "created_at": d.created_at.isoformat() if d.created_at else None
            }
            for d in deliverables
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.post("/")
def create_deliverable(
    title: str,
    description: Optional[str] = None,
    type: str = "other",
    deliverable_type: str = "agency_output",
    status: str = "not_started",
    priority: str = "medium",
    assigned_to: Optional[str] = None,
    due_date: Optional[str] = None,
    phase: Optional[str] = None,
    dependencies: Optional[list] = None,
    blocks: Optional[list] = None,
    db: Session = Depends(get_db)
):
    """Create a new deliverable"""
    
    # Parse due date
    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        except:
            pass
    
    deliverable = Deliverable(
        title=title,
        description=description,
        type=type,
        deliverable_type=deliverable_type,
        status=status,
        priority=priority,
        assigned_to=assigned_to,
        due_date=parsed_due_date,
        phase=phase,
        dependencies=dependencies,
        blocks=blocks
    )
    
    db.add(deliverable)
    db.commit()
    db.refresh(deliverable)
    
    return {
        "id": deliverable.id,
        "title": deliverable.title,
        "status": deliverable.status,
        "created_at": deliverable.created_at.isoformat()
    }


@router.get("/dashboard")
def get_deliverables_dashboard(db: Session = Depends(get_db)):
    """Get deliverables dashboard with stats and upcoming items"""
    
    # Get all deliverables
    all_deliverables = db.query(Deliverable).all()
    
    # Calculate stats
    total = len(all_deliverables)
    brand_inputs = [d for d in all_deliverables if d.deliverable_type == "brand_input"]
    agency_outputs = [d for d in all_deliverables if d.deliverable_type == "agency_output"]
    
    # Status counts
    not_started = len([d for d in all_deliverables if d.status == "not_started"])
    in_progress = len([d for d in all_deliverables if d.status == "in_progress"])
    completed = len([d for d in all_deliverables if d.status == "completed"])
    blocked = len([d for d in all_deliverables if d.status == "blocked"])
    
    # Priority counts
    high_priority = len([d for d in all_deliverables if d.priority == "high"])
    
    # Overdue items
    today = datetime.now(timezone.utc)
    overdue = [
        d for d in all_deliverables 
        if d.due_date and d.due_date < today and d.status != "completed"
    ]
    
    # Upcoming (next 7 days)
    from datetime import timedelta
    next_week = today + timedelta(days=7)
    upcoming = [
        d for d in all_deliverables 
        if d.due_date and today <= d.due_date <= next_week and d.status != "completed"
    ]
    
    # Phase breakdown
    phases = {}
    for d in all_deliverables:
        if d.phase:
            if d.phase not in phases:
                phases[d.phase] = {"total": 0, "completed": 0, "in_progress": 0}
            phases[d.phase]["total"] += 1
            if d.status == "completed":
                phases[d.phase]["completed"] += 1
            elif d.status == "in_progress":
                phases[d.phase]["in_progress"] += 1
    
    return {
        "stats": {
            "total": total,
            "brand_inputs": len(brand_inputs),
            "agency_outputs": len(agency_outputs),
            "not_started": not_started,
            "in_progress": in_progress,
            "completed": completed,
            "blocked": blocked,
            "high_priority": high_priority,
            "overdue_count": len(overdue),
            "upcoming_count": len(upcoming)
        },
        "overdue": [
            {
                "id": d.id,
                "title": d.title,
                "deliverable_type": d.deliverable_type,
                "due_date": d.due_date.isoformat(),
                "priority": d.priority,
                "phase": d.phase
            }
            for d in sorted(overdue, key=lambda x: x.due_date)[:10]
        ],
        "upcoming": [
            {
                "id": d.id,
                "title": d.title,
                "deliverable_type": d.deliverable_type,
                "due_date": d.due_date.isoformat(),
                "priority": d.priority,
                "phase": d.phase
            }
            for d in sorted(upcoming, key=lambda x: x.due_date)[:10]
        ],
        "phases": phases
    }


@router.get("/by-phase/{phase}")
def get_deliverables_by_phase(phase: str, db: Session = Depends(get_db)):
    """Get deliverables for a specific phase"""
    
    deliverables = db.query(Deliverable).filter(
        Deliverable.phase.ilike(f"%{phase}%")
    ).order_by(Deliverable.due_date).all()
    
    # Separate by deliverable type
    brand_inputs = [d for d in deliverables if d.deliverable_type == "brand_input"]
    agency_outputs = [d for d in deliverables if d.deliverable_type == "agency_output"]
    
    return {
        "phase": phase,
        "total": len(deliverables),
        "brand_inputs": [
            {
                "id": d.id,
                "title": d.title,
                "description": d.description,
                "type": d.type,
                "status": d.status,
                "priority": d.priority,
                "due_date": d.due_date.isoformat() if d.due_date else None,
                "assigned_to": d.assigned_to,
                "blocks": d.blocks
            }
            for d in sorted(brand_inputs, key=lambda x: x.due_date if x.due_date else datetime.max)
        ],
        "agency_outputs": [
            {
                "id": d.id,
                "title": d.title,
                "description": d.description,
                "type": d.type,
                "status": d.status,
                "priority": d.priority,
                "due_date": d.due_date.isoformat() if d.due_date else None,
                "assigned_to": d.assigned_to,
                "dependencies": d.dependencies
            }
            for d in sorted(agency_outputs, key=lambda x: x.due_date if x.due_date else datetime.max)
        ]
    }


@router.put("/{deliverable_id}")
def update_deliverable(
    deliverable_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to: Optional[str] = None,
    due_date: Optional[str] = None,
    phase: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Update a deliverable"""
    
    deliverable = db.query(Deliverable).filter(Deliverable.id == deliverable_id).first()
    
    if not deliverable:
        raise HTTPException(404, "Deliverable not found")
    
    if title:
        deliverable.title = title
    if description:
        deliverable.description = description
    if status:
        deliverable.status = status
        if status == "completed" and not deliverable.completed_at:
            deliverable.completed_at = datetime.now(timezone.utc)
        elif status != "completed":
            deliverable.completed_at = None
    if priority:
        deliverable.priority = priority
    if assigned_to:
        deliverable.assigned_to = assigned_to
    if due_date:
        try:
            deliverable.due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        except:
            pass
    if phase:
        deliverable.phase = phase
    
    deliverable.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(deliverable)
    
    return {"success": True, "deliverable_id": deliverable.id}


@router.delete("/{deliverable_id}")
def delete_deliverable(deliverable_id: int, db: Session = Depends(get_db)):
    """Delete a deliverable"""
    
    deliverable = db.query(Deliverable).filter(Deliverable.id == deliverable_id).first()
    
    if not deliverable:
        raise HTTPException(404, "Deliverable not found")
    
    db.delete(deliverable)
    db.commit()
    
    return {"success": True, "message": "Deliverable deleted"}


@router.post("/import-agency-csv")
async def import_agency_deliverables_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import agency deliverables from CSV"""
    
    try:
        contents = await file.read()
        decoded = contents.decode('utf-8')
        
        csv_file = StringIO(decoded)
        reader = csv.DictReader(csv_file)
        
        created = 0
        for row in reader:
            # Parse due date
            due_date = None
            if row.get('Due Date'):
                try:
                    due_date = datetime.strptime(row['Due Date'], '%Y-%m-%d')
                except:
                    pass
            
            # Create deliverable
            deliverable = Deliverable(
                title=row.get('Task', ''),
                description=f"Phase: {row.get('Phase', '')}\nCategory: {row.get('Category', '')}",
                type=row.get('Category', 'other').lower().replace(' ', '_').replace('&', 'and'),
                deliverable_type="agency_output",
                status=row.get('Status', 'Not Started').lower().replace(' ', '_'),
                phase=row.get('Phase', ''),
                assigned_to=row.get('Owner', None) if row.get('Owner') else None,
                due_date=due_date,
                priority="high" if "BFCM" in row.get('Task', '') or "holiday" in row.get('Task', '') else "medium"
            )
            
            db.add(deliverable)
            created += 1
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Imported {created} agency deliverables"
        }
        
    except Exception as e:
        raise HTTPException(500, f"Import failed: {str(e)}")


@router.post("/generate-brand-inputs")
def generate_brand_input_deliverables(db: Session = Depends(get_db)):
    """Generate brand input deliverables (what Crooks provides to HVA)"""
    
    brand_inputs = [
        # PHASE 1: Foundation & Awareness
        {
            "title": "Product Photography (3-4 hero products)",
            "description": "High-res product shots for ad creative. Include hero shots, detail shots, and lifestyle if possible.",
            "type": "creative_assets",
            "deliverable_type": "brand_input",
            "phase": "Phase 1: Foundation & Awareness (Sep - Oct 2025)",
            "due_date": "2025-10-05",
            "priority": "high",
            "blocks": ["Develop 3–4 ad creatives/month"]
        },
        {
            "title": "Brand Guidelines Document",
            "description": "Logo files, fonts, colors, brand voice, messaging guidelines",
            "type": "brand_strategy",
            "deliverable_type": "brand_input",
            "phase": "Phase 1: Foundation & Awareness (Sep - Oct 2025)",
            "due_date": "2025-10-05",
            "priority": "high",
            "blocks": ["Develop 3–4 ad creatives/month", "Create & publish 8–12 posts/month"]
        },
        {
            "title": "Target Audience Profile",
            "description": "Demographics, psychographics, pain points, desires. The Rebel, Ruler, Creator archetypes.",
            "type": "brand_strategy",
            "deliverable_type": "brand_input",
            "phase": "Phase 1: Foundation & Awareness (Sep - Oct 2025)",
            "due_date": "2025-10-05",
            "priority": "high",
            "blocks": ["Set up low-spend campaigns", "Provide overarching paid/social/email strategy"]
        },
        {
            "title": "Meta Business Manager Admin Access",
            "description": "Add HVA as admin to Meta Business Manager for ad account access",
            "type": "access_and_setup",
            "deliverable_type": "brand_input",
            "phase": "Phase 1: Foundation & Awareness (Sep - Oct 2025)",
            "due_date": "2025-10-06",
            "priority": "high",
            "blocks": ["Set up low-spend campaigns on Meta & Google"]
        },
        {
            "title": "Google Ads Account Admin Access",
            "description": "Grant HVA admin access to Google Ads account",
            "type": "access_and_setup",
            "deliverable_type": "brand_input",
            "phase": "Phase 1: Foundation & Awareness (Sep - Oct 2025)",
            "due_date": "2025-10-06",
            "priority": "high",
            "blocks": ["Set up low-spend campaigns on Meta & Google"]
        },
        {
            "title": "Social Media Account Credentials",
            "description": "Admin access to Instagram, TikTok, Facebook, Twitter",
            "type": "access_and_setup",
            "deliverable_type": "brand_input",
            "phase": "Phase 1: Foundation & Awareness (Sep - Oct 2025)",
            "due_date": "2025-10-06",
            "priority": "high",
            "blocks": ["Create & publish 8–12 posts/month"]
        },
        {
            "title": "Email Platform Access (Klaviyo)",
            "description": "Admin access to email marketing platform",
            "type": "access_and_setup",
            "deliverable_type": "brand_input",
            "phase": "Phase 1: Foundation & Awareness (Sep - Oct 2025)",
            "due_date": "2025-10-06",
            "priority": "high",
            "blocks": ["Send 2 emails/month"]
        },
        {
            "title": "Shopify Admin Access",
            "description": "Grant HVA staff account access to Shopify",
            "type": "access_and_setup",
            "deliverable_type": "brand_input",
            "phase": "Phase 1: Foundation & Awareness (Sep - Oct 2025)",
            "due_date": "2025-10-06",
            "priority": "high",
            "blocks": ["Begin uploading products"]
        },
        {
            "title": "Phase 1 Ad Spend Budget Approval",
            "description": "Approve monthly ad spend budget for Meta & Google",
            "type": "budget_and_approvals",
            "deliverable_type": "brand_input",
            "phase": "Phase 1: Foundation & Awareness (Sep - Oct 2025)",
            "due_date": "2025-10-06",
            "priority": "high",
            "blocks": ["Set up low-spend campaigns on Meta & Google"]
        },
        {
            "title": "Google Analytics Access",
            "description": "Grant admin access to GA4 for tracking and reporting",
            "type": "tracking_and_data",
            "deliverable_type": "brand_input",
            "phase": "Phase 1: Foundation & Awareness (Sep - Oct 2025)",
            "due_date": "2025-10-06",
            "priority": "medium",
            "blocks": ["Deliver weekly performance reports"]
        },
        {
            "title": "Lifestyle Content for Social",
            "description": "Brand imagery, behind-the-scenes, street culture content for social posts",
            "type": "creative_assets",
            "deliverable_type": "brand_input",
            "phase": "Phase 1: Foundation & Awareness (Sep - Oct 2025)",
            "due_date": "2025-10-10",
            "priority": "medium",
            "blocks": ["Create & publish 8–12 posts/month"]
        },
        
        # PHASE 2: Growth & Q4 Push
        {
            "title": "Product Photography (15-20 products for BFCM)",
            "description": "Expanded product photography for Q4 campaigns. Include all colorways and angles.",
            "type": "creative_assets",
            "deliverable_type": "brand_input",
            "phase": "Phase 2: Growth & Q4 Push (Nov - Dec 2025)",
            "due_date": "2025-11-01",
            "priority": "high",
            "blocks": ["Produce 6–8 creatives/month", "Launch dedicated BFCM campaigns"]
        },
        {
            "title": "BFCM Discount Strategy & Approval",
            "description": "Black Friday / Cyber Monday discount structure, codes, exclusions",
            "type": "budget_and_approvals",
            "deliverable_type": "brand_input",
            "phase": "Phase 2: Growth & Q4 Push (Nov - Dec 2025)",
            "due_date": "2025-11-10",
            "priority": "high",
            "blocks": ["Launch dedicated BFCM campaigns", "Send 4–6 emails/month"]
        },
        {
            "title": "Holiday Promotional Calendar",
            "description": "Key dates, themes, promotions for Nov-Dec period",
            "type": "brand_strategy",
            "deliverable_type": "brand_input",
            "phase": "Phase 2: Growth & Q4 Push (Nov - Dec 2025)",
            "due_date": "2025-11-01",
            "priority": "high",
            "blocks": ["Conduct campaign-specific strategy sessions"]
        },
        {
            "title": "Gift Guide Product Selection",
            "description": "Curated list of products for holiday gift guides with pricing",
            "type": "product_information",
            "deliverable_type": "brand_input",
            "phase": "Phase 2: Growth & Q4 Push (Nov - Dec 2025)",
            "due_date": "2025-11-05",
            "priority": "high",
            "blocks": ["Send 4–6 emails/month", "Publish 12–16 posts/month"]
        },
        {
            "title": "Holiday-Themed Lifestyle Content",
            "description": "Seasonal imagery, gift-giving scenarios, holiday vibes",
            "type": "creative_assets",
            "deliverable_type": "brand_input",
            "phase": "Phase 2: Growth & Q4 Push (Nov - Dec 2025)",
            "due_date": "2025-11-03",
            "priority": "medium",
            "blocks": ["Publish 12–16 posts/month", "Produce 6–8 creatives/month"]
        },
        {
            "title": "Product Information Sheets (Batch 1)",
            "description": "SKU details, specs, materials, sizing, pricing for first batch of products",
            "type": "product_information",
            "deliverable_type": "brand_input",
            "phase": "Phase 2: Growth & Q4 Push (Nov - Dec 2025)",
            "due_date": "2025-11-10",
            "priority": "high",
            "blocks": ["Begin uploading products & writing descriptions"]
        },
        {
            "title": "Increased Q4 Ad Spend Approval",
            "description": "Approve increased budget for Q4 push period",
            "type": "budget_and_approvals",
            "deliverable_type": "brand_input",
            "phase": "Phase 2: Growth & Q4 Push (Nov - Dec 2025)",
            "due_date": "2025-11-01",
            "priority": "high",
            "blocks": ["Run full-funnel campaigns", "Launch dedicated BFCM campaigns"]
        },
        {
            "title": "Shipping & Return Policies (Holiday)",
            "description": "Updated policies for holiday season with cutoff dates",
            "type": "brand_strategy",
            "deliverable_type": "brand_input",
            "phase": "Phase 2: Growth & Q4 Push (Nov - Dec 2025)",
            "due_date": "2025-11-05",
            "priority": "medium",
            "blocks": ["Send 4–6 emails/month"]
        },
        {
            "title": "UGC Content or Creator Briefs",
            "description": "User-generated content sourcing or creator partnership briefs",
            "type": "creative_assets",
            "deliverable_type": "brand_input",
            "phase": "Phase 2: Growth & Q4 Push (Nov - Dec 2025)",
            "due_date": "2025-11-01",
            "priority": "medium",
            "blocks": ["Produce 6–8 creatives/month"]
        },
        
        # PHASE 3: Full Retainer
        {
            "title": "Monthly Product Photography (8-12 products)",
            "description": "Ongoing monthly product shoots for new releases and seasonal updates",
            "type": "creative_assets",
            "deliverable_type": "brand_input",
            "phase": "Phase 3: Full Retainer (Jan 2026 onward)",
            "due_date": "2026-01-15",
            "priority": "high",
            "blocks": ["Produce 8–12 new creatives/month"]
        },
        {
            "title": "New Site Architecture & Sitemap",
            "description": "Post-relaunch site structure for SEO audit",
            "type": "brand_strategy",
            "deliverable_type": "brand_input",
            "phase": "Phase 3: Full Retainer (Jan 2026 onward)",
            "due_date": "2026-01-10",
            "priority": "high",
            "blocks": ["Conduct technical SEO audit"]
        },
        {
            "title": "SEO Keyword Priorities & Goals",
            "description": "Target keywords, search volume priorities, competitive landscape",
            "type": "brand_strategy",
            "deliverable_type": "brand_input",
            "phase": "Phase 3: Full Retainer (Jan 2026 onward)",
            "due_date": "2026-01-15",
            "priority": "high",
            "blocks": ["Develop keyword strategy & content plan"]
        },
        {
            "title": "Conversion Goals & KPIs",
            "description": "Define success metrics for CRO testing",
            "type": "tracking_and_data",
            "deliverable_type": "brand_input",
            "phase": "Phase 3: Full Retainer (Jan 2026 onward)",
            "due_date": "2026-01-10",
            "priority": "high",
            "blocks": ["Run A/B testing for PDPs, landing pages, checkout"]
        },
        {
            "title": "Video Content or Shoot Coordination",
            "description": "Video assets for ads, social, and site. Either provide or coordinate shoots.",
            "type": "creative_assets",
            "deliverable_type": "brand_input",
            "phase": "Phase 3: Full Retainer (Jan 2026 onward)",
            "due_date": "2026-01-20",
            "priority": "medium",
            "blocks": ["Produce 8–12 new creatives/month"]
        },
        {
            "title": "Brand Refresh Assets (Post-Rebrand)",
            "description": "Updated logos, brand guidelines, visual identity if rebrand is complete",
            "type": "creative_assets",
            "deliverable_type": "brand_input",
            "phase": "Phase 3: Full Retainer (Jan 2026 onward)",
            "due_date": "2026-01-05",
            "priority": "high",
            "blocks": ["Produce 8–12 new creatives/month", "Publish 16–20 posts/month"]
        },
        {
            "title": "Welcome Series Brand Story & Copy Direction",
            "description": "Brand narrative for email welcome flow",
            "type": "brand_strategy",
            "deliverable_type": "brand_input",
            "phase": "Phase 3: Full Retainer (Jan 2026 onward)",
            "due_date": "2026-01-10",
            "priority": "medium",
            "blocks": ["Launch full program (flows: welcome, abandoned cart, post-purchase)"]
        },
        {
            "title": "Abandoned Cart Incentive Approval",
            "description": "Approve discount/incentive strategy for cart abandonment flow",
            "type": "budget_and_approvals",
            "deliverable_type": "brand_input",
            "phase": "Phase 3: Full Retainer (Jan 2026 onward)",
            "due_date": "2026-01-10",
            "priority": "medium",
            "blocks": ["Launch full program (flows: welcome, abandoned cart, post-purchase)"]
        },
        {
            "title": "Full Backend Site Access for CRO",
            "description": "Theme editor access for A/B testing and optimization",
            "type": "access_and_setup",
            "deliverable_type": "brand_input",
            "phase": "Phase 3: Full Retainer (Jan 2026 onward)",
            "due_date": "2026-01-05",
            "priority": "high",
            "blocks": ["Run A/B testing for PDPs, landing pages, checkout"]
        },
        {
            "title": "Seasonal Lookbook Content",
            "description": "Seasonal brand photography for campaigns and site merchandising",
            "type": "creative_assets",
            "deliverable_type": "brand_input",
            "phase": "Phase 3: Full Retainer (Jan 2026 onward)",
            "due_date": "2026-01-31",
            "priority": "medium",
            "blocks": ["Publish 16–20 posts/month"]
        },
        {
            "title": "New SKU Launch Calendar",
            "description": "Product release schedule for upcoming quarter",
            "type": "product_information",
            "deliverable_type": "brand_input",
            "phase": "Phase 3: Full Retainer (Jan 2026 onward)",
            "due_date": "2026-01-15",
            "priority": "high",
            "blocks": ["Manage ongoing SKU uploads"]
        },
        {
            "title": "Quarterly Budget & Scaling Approval",
            "description": "Q1 2026 budget approval and scaling strategy",
            "type": "budget_and_approvals",
            "deliverable_type": "brand_input",
            "phase": "Phase 3: Full Retainer (Jan 2026 onward)",
            "due_date": "2026-01-05",
            "priority": "high",
            "blocks": ["Scale budget allocations"]
        },
    ]
    
    created = 0
    for item in brand_inputs:
        due_date = None
        if item.get('due_date'):
            try:
                due_date = datetime.strptime(item['due_date'], '%Y-%m-%d')
            except:
                pass
        
        deliverable = Deliverable(
            title=item['title'],
            description=item['description'],
            type=item['type'],
            deliverable_type=item['deliverable_type'],
            phase=item['phase'],
            due_date=due_date,
            priority=item['priority'],
            status="not_started",
            blocks=item.get('blocks')
        )
        
        db.add(deliverable)
        created += 1
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Created {created} brand input deliverables"
    }


@router.post("/activate-phase")
def activate_phase(phase: str, db: Session = Depends(get_db)):
    """Activate a phase - useful for moving from planning to execution"""
    
    deliverables = db.query(Deliverable).filter(
        Deliverable.phase.ilike(f"%{phase}%")
    ).all()
    
    updated = 0
    for d in deliverables:
        if d.status == "not_started":
            d.status = "ready"
            updated += 1
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Activated {updated} deliverables in {phase}"
    }


@router.get("/upcoming")
def get_upcoming_deliverables(days: int = 7, db: Session = Depends(get_db)):
    """Get deliverables due in the next X days"""
    
    from datetime import timedelta
    
    today = datetime.now(timezone.utc)
    end_date = today + timedelta(days=days)
    
    deliverables = db.query(Deliverable).filter(
        and_(
            Deliverable.due_date >= today,
            Deliverable.due_date <= end_date,
            Deliverable.status != "completed"
        )
    ).order_by(Deliverable.due_date).all()
    
    return {
        "upcoming": [
            {
                "id": d.id,
                "title": d.title,
                "deliverable_type": d.deliverable_type,
                "type": d.type,
                "status": d.status,
                "priority": d.priority,
                "due_date": d.due_date.isoformat(),
                "phase": d.phase,
                "assigned_to": d.assigned_to
            }
            for d in deliverables
        ],
        "total": len(deliverables),
        "days_ahead": days
    }


@router.get("/overdue")
def get_overdue_deliverables(db: Session = Depends(get_db)):
    """Get overdue deliverables"""
    
    today = datetime.now(timezone.utc)
    
    deliverables = db.query(Deliverable).filter(
        and_(
            Deliverable.due_date < today,
            Deliverable.status != "completed"
        )
    ).order_by(Deliverable.due_date).all()
    
    return {
        "overdue": [
            {
                "id": d.id,
                "title": d.title,
                "deliverable_type": d.deliverable_type,
                "type": d.type,
                "status": d.status,
                "priority": d.priority,
                "due_date": d.due_date.isoformat(),
                "phase": d.phase,
                "assigned_to": d.assigned_to,
                "days_overdue": (today - d.due_date).days
            }
            for d in deliverables
        ],
        "total": len(deliverables)
    }
