from flask import Blueprint, request, jsonify
from app.services.ai_service import ai_service
from app.models import db, GenerationHistory, UserFeedback, AppStatistics
from datetime import datetime
import json

main_bp = Blueprint('main', __name__)

def update_statistics(generation_type):
    """Atualiza estatísticas da aplicação"""
    stats = AppStatistics.query.first()
    if not stats:
        stats = AppStatistics()
        db.session.add(stats)
    
    if generation_type == 'ideas':
        stats.total_ideas_generated += 1
    elif generation_type == 'script':
        stats.total_scripts_generated += 1
    elif generation_type == 'feedback':
        stats.total_feedbacks += 1
    
    stats.last_updated = datetime.utcnow()
    db.session.commit()

@main_bp.route('/api/health')
def health_check():
    stats = AppStatistics.query.first()
    return jsonify({
        "status": "healthy", 
        "message": "✅ HelpubliAI está funcionando perfeitamente!",
        "service": "helpubli-ai",
        "ai_provider": "google-gemini",
        "ai_configured": not ai_service.fallback_mode,
        "database": "connected",
        "statistics": stats.to_dict() if stats else {}
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
        
        # ✅ Salvar no banco de dados
        history_entry = GenerationHistory(
            type='ideas',
            data=json.dumps({
                'niche': niche,
                'audience': audience,
                'ideas': ideas
            }),
            user_session=request.remote_addr  # IP como identificador de sessão
        )
        db.session.add(history_entry)
        update_statistics('ideas')
        db.session.commit()
        
        return jsonify({
            "niche": niche,
            "audience": audience,
            "count": len(ideas),
            "ideas": ideas,
            "status": "success",
            "ai_generated": not ai_service.fallback_mode,
            "history_id": history_entry.id
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
        
        # ✅ Salvar no banco de dados
        history_entry = GenerationHistory(
            type='script',
            data=json.dumps({
                'idea': idea,
                'script': script
            }),
            user_session=request.remote_addr
        )
        db.session.add(history_entry)
        update_statistics('script')
        db.session.commit()
        
        return jsonify({
            "idea": idea,
            "script": script,
            "status": "success",
            "ai_generated": not ai_service.fallback_mode,
            "history_id": history_entry.id
        })
        
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@main_bp.route('/api/feedback', methods=['POST'])
def api_feedback():
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "Mensagem não fornecida"}), 400
        
        message = data['message']
        rating = data.get('rating')
        
        # ✅ Salvar feedback no banco
        feedback = UserFeedback(
            message=message,
            rating=rating,
            user_session=request.remote_addr
        )
        db.session.add(feedback)
        update_statistics('feedback')
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "Feedback recebido com sucesso!",
            "feedback_id": feedback.id
        })
        
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@main_bp.route('/api/history', methods=['GET'])
def get_history():
    """Retorna histórico de gerações"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        history = GenerationHistory.query.order_by(
            GenerationHistory.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'history': [item.to_dict() for item in history.items],
            'total': history.total,
            'pages': history.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@main_bp.route('/api/statistics')
def api_statistics():
    """Endpoint para estatísticas detalhadas"""
    stats = AppStatistics.query.first()
    return jsonify({
        "status": "success",
        "statistics": stats.to_dict() if stats else {}
    })