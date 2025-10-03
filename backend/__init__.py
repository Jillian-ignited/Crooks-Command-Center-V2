# Routers package initialization
# This file makes the routers directory a Python package

__version__ = "2.0.0"
__author__ = "Crooks Command Center Team"

# Import all routers for easy access
try:
    from . import executive
    EXECUTIVE_AVAILABLE = True
except ImportError:
    EXECUTIVE_AVAILABLE = False

try:
    from . import competitive
    COMPETITIVE_AVAILABLE = True
except ImportError:
    COMPETITIVE_AVAILABLE = False

try:
    from . import competitive_analysis
    COMPETITIVE_ANALYSIS_AVAILABLE = True
except ImportError:
    COMPETITIVE_ANALYSIS_AVAILABLE = False

try:
    from . import shopify
    SHOPIFY_AVAILABLE = True
except ImportError:
    SHOPIFY_AVAILABLE = False

try:
    from . import agency
    AGENCY_AVAILABLE = True
except ImportError:
    AGENCY_AVAILABLE = False

try:
    from . import calendar
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False

try:
    from . import content_creation
    CONTENT_CREATION_AVAILABLE = True
except ImportError:
    CONTENT_CREATION_AVAILABLE = False

try:
    from . import intelligence
    INTELLIGENCE_AVAILABLE = True
except ImportError:
    INTELLIGENCE_AVAILABLE = False

try:
    from . import media
    MEDIA_AVAILABLE = True
except ImportError:
    MEDIA_AVAILABLE = False

try:
    from . import summary
    SUMMARY_AVAILABLE = True
except ImportError:
    SUMMARY_AVAILABLE = False

# Export availability status
ROUTER_STATUS = {
    "executive": EXECUTIVE_AVAILABLE,
    "competitive": COMPETITIVE_AVAILABLE,
    "competitive_analysis": COMPETITIVE_ANALYSIS_AVAILABLE,
    "shopify": SHOPIFY_AVAILABLE,
    "agency": AGENCY_AVAILABLE,
    "calendar": CALENDAR_AVAILABLE,
    "content_creation": CONTENT_CREATION_AVAILABLE,
    "intelligence": INTELLIGENCE_AVAILABLE,
    "media": MEDIA_AVAILABLE,
    "summary": SUMMARY_AVAILABLE
}

def get_available_routers():
    """Return list of available routers"""
    return [name for name, available in ROUTER_STATUS.items() if available]

def get_missing_routers():
    """Return list of missing routers"""
    return [name for name, available in ROUTER_STATUS.items() if not available]

