# Crooks Command Center — Clean Drop-In Repo

One repo with **FastAPI backend** + **Next.js frontend**. Upload real scraped CSV/JSON and get a weekly executive summary, brand intelligence, cultural calendar, and agency deliverables.

## Structure
- `/backend` — FastAPI API (upload files, analyze, summarize, calendar, agency)
- `/frontend` — Next.js UI

## Quick Start (Local)
### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd ../frontend
npm i
NEXT_PUBLIC_API_BASE=http://localhost:8000 npm run dev
```

## Uploading Data
- Go to **/intelligence** in the UI.
- Upload CSV/JSON files (any filenames). Expected fields (case-insensitive / auto-normalized):
  - `brand`, `platform`, `date` (YYYY-MM-DD), `likes`, `comments`, `shares`, `text`, `url`
- Run **Report** or use **Dashboard** to generate the Executive Summary.

## Docker (optional)
You can dockerize services if you prefer. A backend Dockerfile is provided. For simplicity, run locally while you test.

## Notes
- No mock data included. If no files are uploaded, the UI will tell you to upload first.
- Analyzer prefers the last 7–60 days. Extend `lookback_days` as needed in the UI.
- Cultural calendar is a small seed list — expand in `backend/services/calendar.py`.
