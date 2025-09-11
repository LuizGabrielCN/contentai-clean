import os
from flask import Flask, send_from_directory
from app import create_app

app = create_app()

# Configurações de caminho
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_FOLDER = os.path.join(BASE_DIR, 'frontend')

# ✅ Apenas UMA função para todas as rotas frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    # Serve arquivos estáticos se existirem
    if path and os.path.exists(os.path.join(FRONTEND_FOLDER, path)):
        return send_from_directory(FRONTEND_FOLDER, path)
    # Serve index.html para todas outras rotas
    return send_from_directory(FRONTEND_FOLDER, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Iniciando HelpubliAI na porta {port}")
    app.run(debug=False, port=port, host='0.0.0.0')