from flask import Blueprint, request, jsonify
from app.services.ai_service import ai_service

# Criar Blueprint para organizar rotas
main_bp = Blueprint('main', __name__)

@main_bp.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy", 
        "message": "✅ API está funcionando perfeitamente!",
        "service": "contentai-api",
        "ai_provider": "google-gemini"
    })

@main_bp.route('/api/generate-ideas', methods=['POST'])
def generate_ideas():
    try:
        data = request.get_json()
        
        if not data or 'niche' not in data or 'audience' not in data:
            return jsonify({"error": "Dados incompletos"}), 400
        
        niche = data['niche']
        audience = data['audience']
        count = data.get('count', 5)
        
        ideas = ai_service.generate_ideas(niche, audience, count)
        
        return jsonify({
            "niche": niche,
            "audience": audience,
            "count": len(ideas),
            "ideas": ideas,
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@main_bp.route('/api/generate-script', methods=['POST'])
def generate_script():
    try:
        data = request.get_json()
        
        if not data or 'idea' not in data:
            return jsonify({"error": "Ideia não fornecida"}), 400
        
        idea = data['idea']
        script = ai_service.generate_script(idea)
        
        return jsonify({
            "idea": idea,
            "script": script,
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

# Adicione outras rotas se necessário