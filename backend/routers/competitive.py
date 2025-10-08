# ADD THIS TO THE END of backend/routers/competitive.py
# (Before the last line of the file)

@router.post("/cleanup-bad-entries")
def cleanup_bad_competitor_entries(db: Session = Depends(get_db)):
    """Remove entries with bad competitor names - accessible via browser"""
    
    try:
        # Define bad patterns
        bad_patterns = [
            'Set Hashtag R 2025',
            'Set R 2025',
            'Crooks Brand Deliverables',
            'Unknown Competitor',
            'Set Hashtag',
        ]
        
        deleted_entries = []
        deleted_count = 0
        
        # Find and delete all bad entries
        for pattern in bad_patterns:
            entries = db.query(CompetitorIntel).filter(
                CompetitorIntel.competitor_name.like(f'%{pattern}%')
            ).all()
            
            for entry in entries:
                deleted_entries.append({
                    "id": entry.id,
                    "name": entry.competitor_name,
                    "source": entry.data_type
                })
                
                # Delete file if exists
                if entry.source_url and os.path.exists(entry.source_url):
                    try:
                        os.remove(entry.source_url)
                    except:
                        pass
                
                db.delete(entry)
                deleted_count += 1
        
        db.commit()
        
        # Get remaining competitors
        remaining = db.query(CompetitorIntel.competitor_name).distinct().all()
        remaining_names = [r.competitor_name for r in remaining]
        
        return {
            "success": True,
            "message": f"Cleaned up {deleted_count} bad entries",
            "deleted_count": deleted_count,
            "deleted_entries": deleted_entries,
            "remaining_competitors": remaining_names,
            "remaining_count": len(remaining_names)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")

@router.get("/cleanup-bad-entries")
def cleanup_bad_competitor_entries_get(db: Session = Depends(get_db)):
    """GET version - just visit this URL in your browser to clean up"""
    return cleanup_bad_competitor_entries(db)
