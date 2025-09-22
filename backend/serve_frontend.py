import os
from flask import Flask, send_from_directory
import sys

# Adicionar o caminho do backend ao Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

# Configurações
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_FOLDER = os.path.join(BASE_DIR, 'frontend')

# ✅ Criar app usando a factory
app, socketio = create_app()

# ✅ Frontend routes (apenas estas rotas aqui)
@app.route('/')
def serve_frontend():
    return send_from_directory(FRONTEND_FOLDER, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    if os.path.exists(os.path.join(FRONTEND_FOLDER, path)):
        return send_from_directory(FRONTEND_FOLDER, path)
    return send_from_directory(FRONTEND_FOLDER, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Servidor HelpubliAI iniciando na porta {port}...")
    print("📍 Frontend: http://localhost:5000")
    print("🔧 API Health: http://localhost:5000/api/health")
    print("🗄️  Banco: sqlite:///contentai.db")
    print("📊 Usando rotas com persistência no banco")
    socketio.run(app, host='0.0.0.0', port=port, debug=False)