import os
from flask import Flask, send_from_directory, jsonify

app = Flask(__name__)

# Configurações
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_FOLDER = os.path.join(BASE_DIR, 'frontend')

# ✅ Frontend routes
@app.route('/')
def serve_frontend():
    return send_from_directory(FRONTEND_FOLDER, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    if os.path.exists(os.path.join(FRONTEND_FOLDER, path)):
        return send_from_directory(FRONTEND_FOLDER, path)
    return send_from_directory(FRONTEND_FOLDER, 'index.html')

# ✅ API routes directly here (no blueprint)
@app.route('/api/health')
def api_health():
    return jsonify({"status": "healthy", "message": "✅ HelpubliAI OK!"})

@app.route('/api/generate-ideas', methods=['POST'])
def api_generate_ideas():
    from flask import request
    # ... implementation

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)