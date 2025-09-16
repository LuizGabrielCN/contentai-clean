import os
from flask import Flask, send_from_directory, jsonify, request
import sys
import os

# Adicionar o caminho do backend ao Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

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
    try:
        data = request.get_json()
        
        if not data or 'niche' not in data or 'audience' not in data:
            return jsonify({"error": "Dados incompletos"}), 400
        
        niche = data['niche']
        audience = data['audience']
        count = data.get('count', 5)
        
        # Fallback - ideias simuladas (substituir pela integração real com IA)
        ideas = [
            {
                "title": f"Reações engraçadas a {niche}",
                "description": f"Vídeo mostrando reações exageradas para {audience}",
                "hashtags": f"#{niche} #{audience} #humor #viral"
            },
            {
                "title": f"Desafio de {niche}",
                "description": f"Desafio divertido envolvendo {niche} para {audience}",
                "hashtags": f"#{niche} #{audience} #desafio #divertido"
            },
            {
                "title": f"Top 3 momentos de {niche}",
                "description": f"Compilação dos melhores momentos para {audience}",
                "hashtags": f"#{niche} #{audience} #top3 #melhoresmomentos"
            }
        ]
        
        # Retornar apenas o número solicitado de ideias
        ideas = ideas[:min(int(count), len(ideas))]
        
        return jsonify({
            "niche": niche,
            "audience": audience,
            "count": len(ideas),
            "ideas": ideas,
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@app.route('/api/generate-script', methods=['POST'])
def api_generate_script():
    try:
        data = request.get_json()
        
        if not data or 'idea' not in data:
            return jsonify({"error": "Ideia não fornecida"}), 400
        
        idea = data['idea']
        
        # Fallback - roteiro simulado (substituir pela integração real com IA)
        script = f"""
📝 ROTEIRO DETALHADO PARA: {idea}

⏰ DURAÇÃO TOTAL: 20-25 segundos

🎬 CENÁRIO: Ambiente bem iluminado e casual

🎯 PÚBLICO: Jovens e adultos que apreciam conteúdo engaging

⏱️  LINHA DO TEMPO:

[0-5 SEGUNDOS] - GANCHO INICIAL
• Entrada impactante com expressão facial exagerada
• Texto na tela: "{idea}"
• Efeito sonoro: "whoosh" para chamar atenção

[5-15 SEGUNDOS] - DESENVOLVIMENTO
• Progressão da história com cortes rápidos
• 2-3 takes mostrando diferentes ângulos
• Mudanças expressivas de rosto e linguagem corporal

[15-22 SEGUNDOS] - CLÍMAX
• Momento mais engraçado da cena
• Reação exagerada à situação
• Texto na tela: "O resultado 👀"

[22-25 SEGUNDOS] - FINAL E CHAMADA PARA AÇÃO
• Resolução rápida e satisfatória
• Olhar direto para câmera com sorriso
• Texto: "Compartilha se riu! ❤️"

🏷️  HASHTAGS SUGERIDAS:
#{idea.replace(' ', '').lower()} 
#viral 
#engraçado 
#tiktok 
#conteudooriginal
"""
        
        return jsonify({
            "idea": idea,
            "script": script,
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@app.route('/api/feedback', methods=['POST'])
def api_feedback():
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "Mensagem não fornecida"}), 400
        
        message = data['message']
        
        # Simular salvamento do feedback (em produção, salvaria em banco de dados)
        print(f"📝 Feedback recebido: {message}")
        
        return jsonify({
            "status": "success",
            "message": "Feedback recebido com sucesso!",
            "received_message": message
        })
        
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@app.route('/api/statistics')
def api_statistics():
    """Endpoint para estatísticas básicas"""
    return jsonify({
        "status": "success",
        "statistics": {
            "total_ideas_generated": 0,  # Em produção, viria de um banco de dados
            "total_scripts_generated": 0,
            "active_users": 1,
            "system_status": "operational"
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Servidor HelpubliAI iniciando na porta {port}...")
    print("📍 Frontend: http://localhost:5000")
    print("🔧 API Health: http://localhost:5000/api/health")
    app.run(host='0.0.0.0', port=port, debug=False)