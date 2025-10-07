from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from datetime import datetime, timedelta, timezone
from typing import Optional, List
import csv
import io

from ..database import get_db
from ..models import Deliverable, Campaign

router = APIRouter()


@router.get("/")
def get_deliverables(
    phase: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    upcoming_days: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all deliverables with filters"""
    query = db.query(Deliverable)
    
    if phase:
        query = query.filter(Deliverable.phase == phase)
    
    if status:
        query = query.filter(Deliverable.status == status)
    
    if category:
        query = query.filter(Deliverable.category == category)
    
    if upcoming_days:
        now = datetime.now(timezone.utc)
        cutoff = now + timedelta(days=upcoming_days)
        query = query.filter(
            and_(
                Deliverable.due_date.isnot(None),
                Deliverable.due_date <= cutoff,
                Deliverable.status != "complete"
            )
        )
    
    deliverables = query.order_by(Deliverable.due_date).all()
    
    return {
        "deliverables": [
            {
                "id": d.id,
                "phase": d.phase,
                "phase_name": d.phase_name,
                "category": d.category,
                "task": d.task,
                "due_date": d.due_date.isoformat() if d.due_date else None,
                "status": d.status,
                "owner": d.owner,
                "campaign_id": d.campaign_id,
                "asset_requirements": d.asset_requirements
            }
            for d in deliverables
        ],
        "total": len(deliverables)
    }


@router.get("/dashboard")
def get_deliverables_dashboard(db: Session = Depends(get_db)):
    """Get dashboard overview of deliverables"""
    
    all_deliverables = db.query(Deliverable).all()
    
    # Group by status
    by_status = {
        "not_started": len([d for d in all_deliverables if d.status == "not_started"]),
        "in_progress": len([d for d in all_deliverables if d.status == "in_progress"]),
        "complete": len([d for d in all_deliverables if d.status == "complete"]),
        "blocked": len([d for d in all_deliverables if d.status == "blocked"])
    }
    
    # Group by phase
    by_phase = {
        "Phase 1": len([d for d in all_deliverables if d.phase == "Phase 1"]),
        "Phase 2": len([d for d in all_deliverables if d.phase == "Phase 2"]),
        "Phase 3": len([d for d in all_deliverables if d.phase == "Phase 3"])
    }
    
    # Upcoming (next 7 days)
    now = datetime.now(timezone.utc)
    upcoming = [
        d for d in all_deliverables 
        if d.due_date and d.due_date <= now + timedelta(days=7) and d.status != "complete"
    ]
    
    # Overdue
    overdue = [
        d for d in all_deliverables
        if d.due_date and d.due_date < now and d.status != "complete"
    ]
    
    return {
        "total_deliverables": len(all_deliverables),
        "by_status": by_status,
        "by_phase": by_phase,
        "upcoming_count": len(upcoming),
        "overdue_count": len(overdue),
        "upcoming": [
            {
                "id": d.id,
                "task": d.task,
                "due_date": d.due_date.isoformat(),
                "phase": d.phase,
                "category": d.category,
                "days_until_due": (d.due_date - now).days
            }
            for d in sorted(upcoming, key=lambda x: x.due_date)[:5]
        ],
        "overdue": [
            {
                "id": d.id,
                "task": d.task,
                "due_date": d.due_date.isoformat(),
                "phase": d.phase,
                "category": d.category,
                "days_overdue": (now - d.due_date).days
            }
            for d in sorted(overdue, key=lambda x: x.due_date)[:5]
        ]
    }


@router.get("/by-phase/{phase}")
def get_deliverables_by_phase(phase: str, db: Session = Depends(get_db)):
    """Get all deliverables for a specific phase"""
    deliverables = db.query(Deliverable).filter(
        Deliverable.phase == phase
    ).order_by(Deliverable.due_date).all()
    
    if not deliverables:
        return {"phase": phase, "deliverables": [], "total": 0}
    
    return {
        "phase": phase,
        "phase_name": deliverables[0].phase_name if deliverables else None,
        "deliverables": [
            {
                "id": d.id,
                "category": d.category,
                "task": d.task,
                "due_date": d.due_date.isoformat() if d.due_date else None,
                "status": d.status,
                "owner": d.owner,
                "asset_requirements": d.asset_requirements,
                "campaign_id": d.campaign_id
            }
            for d in deliverables
        ],
        "total": len(deliverables),
        "completion_rate": len([d for d in deliverables if d.status == "complete"]) / len(deliverables) * 100 if deliverables else 0
    }


@router.post("/")
def create_deliverable(
    phase: str,
    category: str,
    task: str,
    phase_name: str = "",
    due_date: Optional[str] = None,
    asset_requirements: str = "",
    owner: str = "High Voltage Digital",
    db: Session = Depends(get_db)
):
    """Create a new deliverable"""
    
    due_dt = None
    if due_date:
        try:
            due_dt = datetime.fromisoformat(due_date)
            # Make sure it's timezone-aware
            if due_dt.tzinfo is None:
                due_dt = due_dt.replace(tzinfo=timezone.utc)
        except:
            pass
    
    deliverable = Deliverable(
        phase=phase,
        phase_name=phase_name,
        category=category,
        task=task,
        due_date=due_dt,
        asset_requirements=asset_requirements,
        owner=owner,
        status="not_started"
    )
    
    db.add(deliverable)
    db.commit()
    db.refresh(deliverable)
    
    return {
        "success": True,
        "deliverable_id": deliverable.id,
        "task": deliverable.task
    }


@router.put("/{deliverable_id}")
def update_deliverable(
    deliverable_id: int,
    status: Optional[str] = None,
    due_date: Optional[str] = None,
    notes: Optional[str] = None,
    assigned_to: Optional[str] = None,
    campaign_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Update a deliverable"""
    deliverable = db.query(Deliverable).filter(Deliverable.id == deliverable_id).first()
    
    if not deliverable:
        raise HTTPException(404, "Deliverable not found")
    
    if status:
        deliverable.status = status
        if status == "complete" and not deliverable.completed_date:
            deliverable.completed_date = datetime.now(timezone.utc)
    
    if due_date:
        try:
            due_dt = datetime.fromisoformat(due_date)
            if due_dt.tzinfo is None:
                due_dt = due_dt.replace(tzinfo=timezone.utc)
            deliverable.due_date = due_dt
        except:
            pass
    
    if notes:
        deliverable.notes = notes
    
    if assigned_to:
        deliverable.assigned_to = assigned_to
    
    if campaign_id is not None:
        deliverable.campaign_id = campaign_id
    
    deliverable.updated_at = datetime.now(timezone.utc)
    db.commit()
    
    return {"success": True}


@router.post("/import-csv")
async def import_deliverables_csv(
    file: UploadFile = File(...),
    phase_start_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Import deliverables from CSV file"""
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, "File must be a CSV")
    
    try:
        contents = await file.read()
        csv_text = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_text))
        
        imported = 0
        for row in csv_reader:
            # Parse due date
            due_date = None
            if row.get('Due Date'):
                try:
                    due_date = datetime.fromisoformat(row['Due Date'])
                    if due_date.tzinfo is None:
                        due_date = due_date.replace(tzinfo=timezone.utc)
                except:
                    pass
            
            # Extract phase (e.g., "Phase 1" from "Phase 1: Foundation & Awareness")
            phase_full = row.get('Phase', '')
            phase = phase_full.split(':')[0].strip() if ':' in phase_full else phase_full.strip()
            phase_name = phase_full.split(':', 1)[1].strip() if ':' in phase_full else ''
            
            deliverable = Deliverable(
                phase=phase,
                phase_name=phase_name,
                category=row.get('Category', ''),
                task=row.get('Task', ''),
                asset_requirements=row.get('Asset Requirements', ''),
                due_date=due_date,
                status=row.get('Status', 'not_started').lower().replace(' ', '_'),
                owner=row.get('Owner') if row.get('Owner') else 'High Voltage Digital'
            )
            
            db.add(deliverable)
            imported += 1
        
        db.commit()
        
        return {
            "success": True,
            "imported": imported,
            "message": f"Successfully imported {imported} deliverables"
        }
        
    except Exception as e:
        raise HTTPException(400, f"Error importing CSV: {str(e)}")


@router.delete("/{deliverable_id}")
def delete_deliverable(deliverable_id: int, db: Session = Depends(get_db)):
    """Delete a deliverable"""
    deliverable = db.query(Deliverable).filter(Deliverable.id == deliverable_id).first()
    
    if not deliverable:
        raise HTTPException(404, "Deliverable not found")
    
    db.delete(deliverable)
    db.commit()
    
    return {"success": True}


@router.post("/activate-phase")
def activate_phase(
    phase: str,
    start_date: str,
    db: Session = Depends(get_db)
):
    """Activate a phase and set due dates relative to start date
    
    Example: Activate Phase 1 on 10/15/2025
    """
    
    try:
        phase_start = datetime.fromisoformat(start_date)
        if phase_start.tzinfo is None:
            phase_start = phase_start.replace(tzinfo=timezone.utc)
    except:
        raise HTTPException(400, "Invalid date format. Use YYYY-MM-DD")
    
    # Get all deliverables for this phase
    deliverables = db.query(Deliverable).filter(Deliverable.phase == phase).all()
    
    if not deliverables:
        raise HTTPException(404, f"No deliverables found for {phase}")
    
    # Update status and calculate due dates
    updated = 0
    for d in deliverables:
        if d.status == "not_started":
            d.status = "in_progress"
        
        # If deliverable doesn't have a due date yet, calculate one
        if not d.due_date:
            # Example: Ad creative due 2 weeks after phase start
            if "creative" in d.category.lower():
                d.due_date = phase_start + timedelta(days=14)
            # Social posts due weekly
            elif "social" in d.category.lower():
                d.due_date = phase_start + timedelta(days=7)
            # Reporting due end of month
            elif "report" in d.category.lower():
                d.due_date = phase_start + timedelta(days=30)
            # Email/SMS due bi-weekly
            elif "email" in d.category.lower() or "sms" in d.category.lower():
                d.due_date = phase_start + timedelta(days=14)
            else:
                d.due_date = phase_start + timedelta(days=14)  # Default 2 weeks
        
        updated += 1
    
    db.commit()
    
    return {
        "success": True,
        "phase": phase,
        "start_date": start_date,
        "deliverables_updated": updated,
        "message": f"{phase} activated starting {start_date}"
    }


@router.get("/upcoming")
def get_upcoming_deliverables(days: int = 7, db: Session = Depends(get_db)):
    """Get deliverables due in the next X days"""
    
    now = datetime.now(timezone.utc)
    cutoff = now + timedelta(days=days)
    
    deliverables = db.query(Deliverable).filter(
        and_(
            Deliverable.due_date.isnot(None),
            Deliverable.due_date <= cutoff,
            Deliverable.due_date >= now,
            Deliverable.status != "complete"
        )
    ).order_by(Deliverable.due_date).all()
    
    return {
        "upcoming_days": days,
        "count": len(deliverables),
        "deliverables": [
            {
                "id": d.id,
                "task": d.task,
                "due_date": d.due_date.isoformat(),
                "phase": d.phase,
                "category": d.category,
                "status": d.status,
                "days_until_due": (d.due_date - now).days
            }
            for d in deliverables
        ]
    }


@router.get("/overdue")
def get_overdue_deliverables(db: Session = Depends(get_db)):
    """Get all overdue deliverables"""
    
    now = datetime.now(timezone.utc)
    
    deliverables = db.query(Deliverable).filter(
        and_(
            Deliverable.due_date.isnot(None),
            Deliverable.due_date < now,
            Deliverable.status != "complete"
        )
    ).order_by(Deliverable.due_date).all()
    
    return {
        "count": len(deliverables),
        "deliverables": [
            {
                "id": d.id,
                "task": d.task,
                "due_date": d.due_date.isoformat(),
                "phase": d.phase,
                "category": d.category,
                "status": d.status,
                "days_overdue": (now - d.due_date).days
            }
            for d in deliverables
        ]
    }
