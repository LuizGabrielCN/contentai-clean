from flask import Blueprint, request, jsonify
from app.services.ai_service import ai_service
from app.models import db, GenerationHistory, UserFeedback, AppStatistics
from datetime import datetime
import json
from functools import lru_cache
import threading
import time

# Criar Blueprint para organizar rotas
main_bp = Blueprint('main', __name__)

# ======================
# SISTEMA DE CACHE
# ======================

# ✅ Cache em memória
@lru_cache(maxsize=100)
def generate_ideas_cached(niche, audience, count):
    """Versão em cache da geração de ideias"""
    return ai_service.generate_ideas(niche, audience, count)

@lru_cache(maxsize=100)
def generate_script_cached(idea):
    """Versão em cache da geração de roteiros"""
    return ai_service.generate_script(idea)

# ✅ Funções de limpeza de cache
def clear_ideas_cache():
    generate_ideas_cached.cache_clear()
    print("🧹 Cache de ideias limpo")

def clear_script_cache():
    generate_script_cached.cache_clear()
    print("🧹 Cache de roteiros limpo")

def clear_all_cache():
    clear_ideas_cache()
    clear_script_cache()
    print("🧹 Todo o cache limpo")

# ✅ Limpeza automática periódica
def clear_cache_periodically():
    """Limpa o cache a cada hora automaticamente"""
    while True:
        time.sleep(3600)  # 1 hora
        clear_all_cache()

# ✅ Inicialização segura do cache cleaner
def init_cache_cleaner(app):
    """Inicializa o limpeza de cache de forma segura"""
    with app.app_context():
        if not hasattr(app, 'cache_cleaner_started'):
            cache_cleaner = threading.Thread(target=clear_cache_periodically, daemon=True)
            cache_cleaner.start()
            app.cache_cleaner_started = True
            print("✅ Limpeza automática de cache iniciada (a cada 1 hora)")

# ======================
# ROTAS DA API
# ======================

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
        
        # ✅ USANDO CACHE
        ideas = generate_ideas_cached(niche, audience, count)
        
        # ✅ Salvar no banco de dados
        history_entry = GenerationHistory(
            type='ideas',
            data=json.dumps({
                'niche': niche,
                'audience': audience,
                'ideas': ideas
            }),
            user_session=request.remote_addr
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
            "history_id": history_entry.id,
            "cached": True
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
        
        # ✅ USANDO CACHE
        script = generate_script_cached(idea)
        
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
            "history_id": history_entry.id,
            "cached": True
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

@main_bp.route('/admin/clear-cache', methods=['POST'])
def admin_clear_cache():
    """Rota administrativa para limpar cache manualmente"""
    try:
        clear_all_cache()
        return jsonify({
            "status": "success",
            "message": "Cache limpo com sucesso",
            "cache_info": {
                "ideas_cache_size": generate_ideas_cached.cache_info().currsize,
                "ideas_cache_hits": generate_ideas_cached.cache_info().hits,
                "ideas_cache_misses": generate_ideas_cached.cache_info().misses,
                "script_cache_size": generate_script_cached.cache_info().currsize,
                "script_cache_hits": generate_script_cached.cache_info().hits,
                "script_cache_misses": generate_script_cached.cache_info().misses
            }
        })
    except Exception as e:
        return jsonify({"error": f"Erro ao limpar cache: {str(e)}"}), 500

@main_bp.route('/api/cache-stats')
def cache_stats():
    """Estatísticas do cache"""
    return jsonify({
        "ideas_cache_size": generate_ideas_cached.cache_info().currsize,
        "ideas_cache_hits": generate_ideas_cached.cache_info().hits,
        "ideas_cache_misses": generate_ideas_cached.cache_info().misses,
        "script_cache_size": generate_script_cached.cache_info().currsize,
        "script_cache_hits": generate_script_cached.cache_info().hits,
        "script_cache_misses": generate_script_cached.cache_info().misses
    })

# ======================
# FUNÇÕES UTilitárias
# ======================

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