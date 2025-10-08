import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine
from backend.models import CompetitorIntel

def cleanup_bad_competitors():
    """Remove bad competitor entries"""
    db = SessionLocal()
    
    try:
        # Find entries with bad names
        bad_patterns = [
            'Set Hashtag R 2025',
            'Set R 2025',
            'Crooks Brand Deliverables',
            'Unknown Competitor'
        ]
        
        deleted_count = 0
        
        for pattern in bad_patterns:
            entries = db.query(CompetitorIntel).filter(
                CompetitorIntel.competitor_name.like(f'%{pattern}%')
            ).all()
            
            for entry in entries:
                print(f"Deleting: {entry.competitor_name} (ID: {entry.id})")
                # Delete associated file if exists
                if entry.source_url and os.path.exists(entry.source_url):
                    os.remove(entry.source_url)
                db.delete(entry)
                deleted_count += 1
        
        db.commit()
        print(f"\n✅ Cleanup complete! Deleted {deleted_count} bad entries.")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🧹 Starting competitor database cleanup...\n")
    cleanup_bad_competitors()
