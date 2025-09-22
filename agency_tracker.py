import json, os

DATA_PATH = os.path.join('data', 'agency.json')

DEFAULT = {
  "agencies": [
    {
      "name": "High Voltage Digital",
      "phase": 1,
      "current_deliverables": 4,
      "monthly_budget": 4000,
      "budget_used": 1500,
      "on_time_delivery": 100,
      "quality_score": 95,
      "next_phase_requirements": [
        "Complete Phase 1 deliverables",
        "Client approval on creative direction",
        "Budget allocation for Phase 2 ($6,000)",
        "Resource allocation (2 additional team members)"
      ],
      "deliverables_breakdown": {
        "completed": ["Brand audit", "Competitive analysis"],
        "in_progress": ["Creative strategy", "Content calendar"],
        "pending": ["Asset creation", "Campaign launch"]
      },
      "current_projects": [
        {"name": "Brand Audit", "status": "completed", "due_date": "2025-09-15"},
        {"name": "Competitive Analysis", "status": "completed", "due_date": "2025-09-20"},
        {"name": "Creative Strategy", "status": "in_progress", "due_date": "2025-09-25"},
        {"name": "Content Calendar", "status": "in_progress", "due_date": "2025-09-30"},
        {"name": "Asset Creation", "status": "pending", "due_date": "2025-10-05"},
        {"name": "Campaign Launch", "status": "pending", "due_date": "2025-10-15"}
      ],
      "performance_metrics": {
        "response_time": "< 2 hours",
        "revision_rounds": "1.2 avg",
        "client_satisfaction": "4.8/5"
      }
    }
  ]
}

def get_agencies():
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, 'r') as f:
                return json.load(f)
        except Exception:
            return DEFAULT
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, 'w') as f:
        json.dump(DEFAULT, f, indent=2)
    return DEFAULT
