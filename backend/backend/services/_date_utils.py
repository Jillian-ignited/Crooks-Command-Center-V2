# backend/services/_date_utils.py
import datetime
from typing import Optional

def parse_due_date(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    s = raw.strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%m/%d/%y", "%m-%d-%Y", "%m-%d-%y"):
        try:
            dt = datetime.datetime.strptime(s, fmt)
            return dt.date().isoformat()
        except ValueError:
            continue
    return None