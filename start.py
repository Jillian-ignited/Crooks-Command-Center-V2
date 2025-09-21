#!/usr/bin/env python3
"""
Startup script for Crooks & Castles Command Center V2 on Render
"""
import os
import sys

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import and run the Flask app
if __name__ == "__main__":
    from app import app
    
    # Get port from environment (Render sets this)
    port = int(os.environ.get("PORT", 5000))
    
    # Run the app
    app.run(host="0.0.0.0", port=port, debug=False)
