#!/usr/bin/env python3
"""
Production start script for Render deployment
Configures the Flask application for production use with gunicorn
"""

import os
from app import app

if __name__ == "__main__":
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get("PORT", 5000))
    
    # Run in production mode
    app.run(host="0.0.0.0", port=port, debug=False)
