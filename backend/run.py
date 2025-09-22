import os
import sys
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

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

    # Para desenvolvimento, debug=True é útil, mas o reloader pode causar problemas.
    # Usar allow_unsafe_werkzeug=True permite que o Socket.IO gerencie o loop de eventos
    # enquanto ainda obtemos os logs de depuração do Flask.
    try:
        socketio.run(app, debug=True, port=5000, host='0.0.0.0', allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        print("💡 Verifique se a porta 5000 não está sendo usada")
