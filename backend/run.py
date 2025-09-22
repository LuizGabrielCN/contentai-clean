import os
import sys

# Adiciona o diretório atual ao path do Python
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, socketio

app, _ = create_app()

if __name__ == '__main__':
    print("🚀 Iniciando ContentAI API com WebSocket...")
    print("📍 Endereço: http://localhost:5000")
    print("🔧 Health Check: http://localhost:5000/api/health")
    print("💡 Use Ctrl+C para parar o servidor")
    print("-" * 50)

    try:
        socketio.run(app, debug=True, port=5000, host='0.0.0.0')
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        print("💡 Verifique se a porta 5000 não está sendo usada")
