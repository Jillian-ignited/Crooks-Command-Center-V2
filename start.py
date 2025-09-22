# start.py
import os
from app import app

def get_port():
    raw = os.environ.get('PORT', '5000')
    try:
        return int(raw)
    except ValueError:
        return 5000  # fallback if someone sets PORT='auto'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=get_port(), debug=False)
