import os
from flask import Flask, send_from_directory
from app import create_app

# Configurações - com caminhos absolutos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_FOLDER = os.path.join(BASE_DIR, 'frontend')

app = create_app()

# Servir arquivos estáticos
@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_FOLDER, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    file_path = os.path.join(FRONTEND_FOLDER, path)
    if os.path.exists(file_path):
        return send_from_directory(FRONTEND_FOLDER, path)
    return 'Arquivo não encontrado', 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Iniciando HelpubliAI na porta {port}")
    app.run(debug=debug, port=port, host='0.0.0.0')