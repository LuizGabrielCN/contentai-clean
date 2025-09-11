import os
from flask import Flask, send_from_directory
from app import create_app

# Configurações
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_FOLDER = os.path.join(BASE_DIR, 'frontend')

app = create_app()

# ✅ Apenas UMA rota para servir o frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    if path and os.path.exists(os.path.join(FRONTEND_FOLDER, path)):
        return send_from_directory(FRONTEND_FOLDER, path)
    # Serve index.html para qualquer rota não encontrada
    return send_from_directory(FRONTEND_FOLDER, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'production') == 'development'
    print(f"🚀 Iniciando HelpubliAI na porta {port}")
    app.run(debug=debug, port=port, host='0.0.0.0')