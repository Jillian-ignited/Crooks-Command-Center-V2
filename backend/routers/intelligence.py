from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timezone
from typing import Optional
import os
import json
import PyPDF2
from anthropic import Anthropic

from ..database import get_db
from ..models import IntelligenceFile

router = APIRouter()

# File upload directory
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize Anthropic client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


async def analyze_intelligence(text_content: str, filename: str):
    """Analyze intelligence content using Claude AI"""
    
    try:
        prompt = f"""Analyze this intelligence file for Crooks & Castles streetwear brand.

Filename: {filename}

Content:
{text_content[:8000]}

Provide a structured analysis covering:
1. Key insights and trends
2. Competitive intelligence (if any)
3. Market opportunities
4. Customer/audience insights
5. Actionable recommendations

Focus on insights relevant to hip-hop culture, streetwear, and urban fashion."""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        analysis_text = message.content[0].text
        
        return {
            "summary": analysis_text,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "model": "claude-sonnet-4-20250514"
        }
        
    except Exception as e:
        return {
            "summary": f"Analysis failed: {str(e)}",
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "error": True
        }


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    source: str = Form("manual_upload"),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload intelligence file with AI analysis"""
    
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.txt', '.csv', '.json', '.jsonl', '.md', '.doc', '.docx']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                400, 
                f"File type {file_ext} not supported. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        # Save file
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        file_size = len(contents)
        
        # Extract text based on file type
        text_content = ""
        
        if file_ext == '.pdf':
            # PDF extraction
            try:
                pdf_file = open(file_path, 'rb')
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                for page in pdf_reader.pages:
                    text_content += page.extract_text()
                pdf_file.close()
            except Exception as e:
                text_content = f"Error extracting PDF: {str(e)}"
        
        elif file_ext == '.json':
            # JSON extraction
            try:
                json_data = json.loads(contents.decode('utf-8'))
                text_content = json.dumps(json_data, indent=2)
            except Exception as e:
                text_content = f"Error parsing JSON: {str(e)}"
        
        elif file_ext == '.jsonl':
            # JSONL extraction (JSON Lines)
            try:
                lines = contents.decode('utf-8').split('\n')
                json_objects = []
                for line in lines:
                    line = line.strip()
                    if line:
                        try:
                            json_objects.append(json.loads(line))
                        except:
                            continue
                text_content = json.dumps(json_objects, indent=2)
            except Exception as e:
                text_content = f"Error parsing JSONL: {str(e)}"
        
        elif file_ext in ['.txt', '.md', '.csv']:
            # Plain text extraction
            try:
                text_content = contents.decode('utf-8')
            except:
                text_content = contents.decode('latin-1')
        
        elif file_ext in ['.doc', '.docx']:
            # Word document extraction (basic)
            try:
                text_content = contents.decode('utf-8', errors='ignore')
            except:
                text_content = "Word document uploaded (full text extraction not available)"
        
        else:
            text_content = "File uploaded (text extraction not available for this type)"
        
        # Perform AI analysis
        analysis_results = await analyze_intelligence(text_content, file.filename)
        
        # Create database record
        intelligence_file = IntelligenceFile(
            filename=safe_filename,
            original_filename=file.filename,
            source=source,
            file_path=file_path,
            file_size=file_size,
            file_type=file_ext,
            description=description,
            analysis_results=analysis_results,
            status="processed",
            processed_at=datetime.now(timezone.utc)
        )
        
        db.add(intelligence_file)
        db.commit()
        db.refresh(intelligence_file)
        
        return {
            "success": True,
            "file_id": intelligence_file.id,
            "filename": file.filename,
            "analysis": analysis_results,
            "message": "File uploaded and analyzed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Upload failed: {str(e)}")


@router.get("/files")
def get_intelligence_files(
    limit: int = 50,
    offset: int = 0,
    source: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of intelligence files"""
    
    query = db.query(IntelligenceFile)
    
    if source:
        query = query.filter(IntelligenceFile.source == source)
    
    total = query.count()
    
    files = query.order_by(desc(IntelligenceFile.uploaded_at)).limit(limit).offset(offset).all()
    
    return {
        "files": [
            {
                "id": f.id,
                "filename": f.original_filename,
                "source": f.source,
                "file_type": f.file_type,
                "file_size": f.file_size,
                "description": f.description,
                "status": f.status,
                "uploaded_at": f.uploaded_at.isoformat() if f.uploaded_at else None,
                "processed_at": f.processed_at.isoformat() if f.processed_at else None,
                "has_analysis": bool(f.analysis_results)
            }
            for f in files
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/files/{file_id}")
def get_file_detail(file_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific file"""
    
    file = db.query(IntelligenceFile).filter(IntelligenceFile.id == file_id).first()
    
    if not file:
        raise HTTPException(404, "File not found")
    
    return {
        "id": file.id,
        "filename": file.original_filename,
        "source": file.source,
        "brand": file.brand,
        "file_type": file.file_type,
        "file_size": file.file_size,
        "description": file.description,
        "analysis_results": file.analysis_results,
        "status": file.status,
        "uploaded_at": file.uploaded_at.isoformat() if file.uploaded_at else None,
        "processed_at": file.processed_at.isoformat() if file.processed_at else None,
        "created_by": file.created_by
    }


@router.delete("/files/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db)):
    """Delete an intelligence file"""
    
    file = db.query(IntelligenceFile).filter(IntelligenceFile.id == file_id).first()
    
    if not file:
        raise HTTPException(404, "File not found")
    
    # Delete physical file
    try:
        if os.path.exists(file.file_path):
            os.remove(file.file_path)
    except Exception as e:
        print(f"Error deleting physical file: {e}")
    
    # Delete database record
    db.delete(file)
    db.commit()
    
    return {"success": True, "message": "File deleted"}


@router.get("/sources")
def get_sources(db: Session = Depends(get_db)):
    """Get list of intelligence sources"""
    
    sources = db.query(
        IntelligenceFile.source,
        func.count(IntelligenceFile.id).label('count')
    ).group_by(IntelligenceFile.source).all()
    
    return {
        "sources": [
            {
                "name": source,
                "count": count
            }
            for source, count in sources
        ]
    }
