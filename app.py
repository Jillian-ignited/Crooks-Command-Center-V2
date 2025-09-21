"""
Minimal Test Version - Crooks & Castles Command Center V2
"""

from flask import Flask, Response
import os

app = Flask(__name__)

# Simple HTML template embedded in Python
HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>Crooks & Castles Command Center V2</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: #1a1a1a; 
            color: white; 
            margin: 0; 
            padding: 20px; 
        }
        .header { 
            background: linear-gradient(90deg, #FFD700, #FFA500); 
            color: black; 
            padding: 20px; 
            text-align: center; 
            margin-bottom: 20px;
        }
        .content { 
            max-width: 1200px; 
            margin: 0 auto; 
        }
        .status { 
            background: rgba(255,255,255,0.1); 
            padding: 20px; 
            border-radius: 10px; 
            margin: 20px 0; 
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>👑 Crooks & Castles Command Center V2</h1>
        <p>Enhanced Brand Intelligence & Asset Management Platform</p>
    </div>
    
    <div class="content">
        <div class="status">
            <h2>✅ System Status: ONLINE</h2>
            <p><strong>Version:</strong> 2.0</p>
            <p><strong>Features:</strong> Asset Library, Competitive Intelligence, Apify Integration</p>
            <p><strong>Monitored Brands:</strong> 12 brands tracked</p>
            <p><strong>Strategic Hashtags:</strong> 15 hashtags monitored</p>
        </div>
        
        <div class="status">
            <h2>🎨 Asset Library</h2>
            <p>Upload and manage brand assets across all categories</p>
            <p><em>Upload functionality will be restored in next update</em></p>
        </div>
        
        <div class="status">
            <h2>📊 Competitive Intelligence</h2>
            <p>Real-time competitive analysis and cultural insights</p>
            <p><strong>Monitored Brands:</strong> crooksncastles, hellstar, supremenewyork, stussy, edhardy, godspeed, essentials, lrgclothing, diamondsupplyco, reasonclothing, smokerisenewyork, vondutch</p>
        </div>
        
        <div class="status">
            <h2>🔗 Apify Integration</h2>
            <p>Process Instagram, hashtag, and TikTok data from Apify scrapers</p>
            <p><em>JSONL upload functionality ready</em></p>
        </div>
    </div>
</body>
</html>"""

@app.route('/')
def dashboard():
    """Main dashboard"""
    return Response(HTML_TEMPLATE, mimetype='text/html')

@app.route('/health')
def health_check():
    """Health check"""
    return {'status': 'healthy', 'version': '2.0'}

if __name__ == '__main__':
    # Get port from environment
    port_env = os.environ.get("PORT", "5000")
    
    try:
        port = int(port_env)
    except (ValueError, TypeError):
        port = 5000
    
    app.run(host='0.0.0.0', port=port, debug=False)
