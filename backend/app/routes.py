from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_socketio import emit, join_room, leave_room
from flask_mail import Message
from app.services.ai_service import ai_service
from app.models import db, GenerationHistory, UserFeedback, AppStatistics, User, bcrypt
from datetime import datetime, date
import json
from functools import lru_cache
import os
import threading
import time
from email_validator import validate_email, EmailNotValidError

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
# FUNÇÕES DE AUTENTICAÇÃO
# ======================

def check_usage_limits(user_id):
    """Verifica limites de uso baseado no plano"""
    if user_id is None:  # Usuário anônimo - limite reduzido
        today = datetime.utcnow().date()
        anonymous_generations = GenerationHistory.query.filter(
            GenerationHistory.user_id.is_(None),
            GenerationHistory.user_session.like(f"%{request.remote_addr}%"),
            db.func.date(GenerationHistory.created_at) == today
        ).count()
        return anonymous_generations < 3  # 3 gerações/dia para anônimos
    
    user = User.query.get(int(user_id)) if user_id else None
    
    if user and user.is_premium:
        return True  # Sem limites para premium
    
    # Verificar uso diário para free users
    today = datetime.utcnow().date()
    today_generations = GenerationHistory.query.filter(
        GenerationHistory.user_id == int(user_id),
        db.func.date(GenerationHistory.created_at) == today
    ).count()
    
    return today_generations < 10  # Limite de 10 gerações/dia para free

# ======================
# ROTAS DE AUTENTICAÇÃO
# ======================

@main_bp.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({"error": "Email e senha são obrigatórios"}), 400
        
        # Validar email
        try:
            valid = validate_email(data['email'], check_deliverability=False)  # ✅ Não verificar entrega
            email = valid.email
        except EmailNotValidError:
            return jsonify({"error": "Email inválido"}), 400
        
        # Verificar se usuário já existe
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email já cadastrado"}), 409
        
        # Criar novo usuário
        user = User(email=email, name=data.get('name'))
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Criar token de acesso
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            "status": "success",
            "message": "Usuário criado com sucesso",
            "access_token": access_token,
            "user": user.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@main_bp.route('/admin/real-time-stats', methods=['GET'])
@jwt_required()
def get_real_time_stats():
    """Estatísticas em tempo real para admin"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user or not user.is_admin:
            return jsonify({"error": "Acesso não autorizado"}), 403

        # Usuários online (login nas últimas 30 min)
        from datetime import timedelta
        recent_time = datetime.utcnow() - timedelta(minutes=30)
        online_users = User.query.filter(User.last_login > recent_time).count()

        # Gerações por minuto (nas últimas 30 min)
        recent_generations = GenerationHistory.query.filter(GenerationHistory.created_at > recent_time).count()
        generations_per_minute = round(recent_generations / 30, 2)

        return jsonify({
            "onlineUsers": online_users,
            "generationsPerMinute": generations_per_minute,
            "activeSessions": online_users
        })

    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500



@main_bp.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({"error": "Email e senha são obrigatórios"}), 400
        
        # Buscar usuário
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({"error": "Email ou senha inválidos"}), 401
        
        # Atualizar último login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # ✅ GARANTIR que identity é o ID (integer)
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            "status": "success",
            "message": "Login realizado com sucesso",
            "access_token": access_token,
            "user": user.to_dict()
        })
        
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@main_bp.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Solicitar reset de senha"""
    try:
        data = request.get_json()
        if not data or 'email' not in data:
            return jsonify({"error": "Email é obrigatório"}), 400

        email = data['email']
        try:
            valid = validate_email(email, check_deliverability=False)
            email = valid.email
        except EmailNotValidError:
            return jsonify({"error": "Email inválido"}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            # Por segurança, não informar se o email existe ou não
            return jsonify({"status": "success", "message": "Se o email estiver cadastrado, você receberá instruções."}), 200

        reset_token = user.generate_reset_token()
        db.session.commit()

        # Enviar email
        mail = current_app.extensions.get('mail')
        if mail:
            # A URL do frontend DEVE ser configurada via variável de ambiente
            frontend_url = os.environ.get('FRONTEND_URL')
            if not frontend_url:
                current_app.logger.error("FATAL: FRONTEND_URL não está definida. O email de reset de senha não pode ser enviado.")
                # Retorna sucesso para o usuário para não expor erro de configuração, mas o email não será enviado.
                return jsonify({"status": "success", "message": "Se o email estiver cadastrado, você receberá instruções."}), 200
            reset_url = f"{frontend_url}/reset-password.html?token={reset_token}"
            
            msg = Message(
                subject="Reset de Senha - HelpubliAI",
                recipients=[user.email],
                body=f"Olá {user.name or 'usuário'},\n\nPara resetar sua senha, clique no link: {reset_url}\n\nEste link expira em 1 hora.",
                html=f"""
                <html><body>
                    <h2>Reset de Senha - HelpubliAI</h2>
                    <p>Olá {user.name or 'usuário'},</p>
                    <p>Você solicitou um reset de senha. Clique no botão abaixo para criar uma nova senha:</p>
                    <p><a href="{reset_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Resetar Senha</a></p>
                    <p><small>Este link expira em 1 hora.</small></p>
                </body></html>
                """
            )
            try:
                mail.send(msg)
                current_app.logger.info(f"✅ Email de reset enviado para {user.email}")
            except Exception as e:
                current_app.logger.error(f"⚠️ Erro ao enviar email de reset de senha: {str(e)}")
                # A requisição não deve falhar para o usuário, mas logamos o erro.
        else:
            current_app.logger.warning("⚠️ Flask-Mail não configurado - email de reset de senha não foi enviado.")

        return jsonify({"status": "success", "message": "Se o email estiver cadastrado, você receberá instruções."}), 200

    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@main_bp.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """Resetar senha com token"""
    try:
        data = request.get_json()
        if not data or 'token' not in data or 'password' not in data:
            return jsonify({"error": "Token e nova senha são obrigatórios"}), 400

        token = data['token']
        new_password = data['password']

        if len(new_password) < 6:
            return jsonify({"error": "A senha deve ter pelo menos 6 caracteres"}), 400

        user = User.verify_reset_token(token)

        if not user:
            return jsonify({"error": "Token inválido ou expirado"}), 400

        # Atualizar senha e limpar token
        user.set_password(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        user.last_login = datetime.utcnow()
        db.session.commit()

        # Criar novo token de acesso para login automático
        access_token = create_access_token(identity=user.id)

        return jsonify({
            "status": "success",
            "message": "Senha resetada com sucesso",
            "access_token": access_token,
            "user": user.to_dict()
        }), 200

    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@main_bp.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        user_identity = get_jwt_identity()
        if user_identity is None:
            return jsonify({"error": "Token inválido ou ausente"}), 401
        try:
            user_id = int(user_identity)
        except (ValueError, TypeError):
            return jsonify({"error": "Identidade do usuário inválida no token"}), 422
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404
        
        return jsonify({
            "status": "success",
            "user": user.to_dict()
        })
        
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@main_bp.route('/api/auth/upgrade', methods=['POST'])
@jwt_required()
def upgrade_to_premium():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404
        
        user.is_premium = True
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "Conta atualizada para premium",
            "user": user.to_dict()
        })
        
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

# ======================
# ROTAS DA API PRINCIPAIS
# ======================

@main_bp.route('/api/health')
def health_check():
    stats = AppStatistics.query.first()
    total_users = User.query.count()
    
    return jsonify({
        "status": "healthy", 
        "message": "✅ HelpubliAI está funcionando perfeitamente!",
        "service": "helpubli-ai",
        "ai_provider": "google-gemini",
        "ai_configured": not ai_service.fallback_mode,
        "database": "connected",
        "statistics": {
            "total_users": total_users,
            "total_ideas": stats.total_ideas_generated if stats else 0,
            "total_scripts": stats.total_scripts_generated if stats else 0,
            "total_feedbacks": stats.total_feedbacks if stats else 0
        }
    })

def _build_generation_response(history_entry, user_id, **kwargs):
    """Constrói a resposta JSON padrão para rotas de geração."""
    user = User.query.get(user_id) if user_id else None
    is_premium = user.is_premium if user else False

    response_data = {
        "status": "success",
        "ai_generated": not ai_service.fallback_mode,
        "history_id": history_entry.id,
        "user_id": user_id,
        "is_premium": is_premium
    }
    response_data.update(kwargs)
    return jsonify(response_data)

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

@main_bp.route('/api/generate-ideas', methods=['POST'])
@jwt_required(optional=True)
def generate_ideas():
    try:
        user_id = get_jwt_identity()  # Pode ser None se não autenticado
        
        # Verificar limites de uso
        if not check_usage_limits(user_id):
            return jsonify({
                "error": "Limite diário de gerações atingido. Faça login ou atualize para premium.",
                "requires_auth": True
            }), 429
        
        data = request.get_json()
        
        if not data or 'niche' not in data or 'audience' not in data:
            return jsonify({"error": "Dados incompletos"}), 400
        
        niche = data['niche']
        audience = data['audience']
        count = data.get('count', 5)
        
        # ✅ USANDO CACHE
        ideas = generate_ideas_cached(niche, audience, count)
        
        # ✅ Se a IA falhou e retornou uma lista vazia, usar fallback
        if not ideas:
            current_app.logger.warning("A geração de ideias retornou uma lista vazia. Usando fallback.")
            ideas = ai_service._get_fallback_ideas(niche, audience, count)

        # ✅ Salvar no banco de dados
        history_entry = GenerationHistory(
            type='ideas',
            data=json.dumps({
                'niche': niche,
                'audience': audience,
                'ideas': ideas
            }),
            user_id=user_id,
            user_session=request.remote_addr
        )
        db.session.add(history_entry)
        update_statistics('ideas')
        db.session.commit()
        
        return _build_generation_response(history_entry, user_id,
            niche=niche,
            audience=audience,
            count=len(ideas),
            ideas=ideas
        )
        
    except Exception as e:
        current_app.logger.error(f"Erro inesperado ao gerar ideias: {e}", exc_info=True)
        return jsonify({"error": "Ocorreu um erro inesperado ao gerar as ideias. Tente novamente."}), 500

@main_bp.route('/api/generate-script', methods=['POST'])
@jwt_required(optional=True)
def generate_script():
    try:
        user_id = get_jwt_identity()
        
        # Verificar limites de uso
        if not check_usage_limits(user_id):
            return jsonify({
                "error": "Limite diário de gerações atingido. Faça login ou atualize para premium.",
                "requires_auth": True
            }), 429
        
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
            user_id=user_id,
            user_session=request.remote_addr
        )
        db.session.add(history_entry)
        update_statistics('script')
        db.session.commit()
        
        return _build_generation_response(history_entry, user_id,
            idea=idea,
            script=script
        )
        
    except Exception as e:
        current_app.logger.error(f"Erro inesperado ao gerar roteiro: {e}", exc_info=True)
        return jsonify({"error": "Ocorreu um erro inesperado ao gerar o roteiro. Tente novamente."}), 500

@main_bp.route('/api/user/history', methods=['GET'])
@jwt_required()
def get_user_history():
    """Retorna histórico do usuário logado"""
    try:
        user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        history = GenerationHistory.query.filter_by(
            user_id=user_id
        ).order_by(
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

@main_bp.route('/api/feedback', methods=['POST'])
@jwt_required(optional=True)
def api_feedback():
    try:
        user_id = get_jwt_identity()
        
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "Mensagem não fornecida"}), 400
        
        message = data['message']
        rating = data.get('rating')
        
        # ✅ Salvar feedback no banco
        feedback = UserFeedback(
            message=message,
            rating=rating,
            user_id=int(user_id) if user_id else None,
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

@main_bp.route('/api/statistics')
def api_statistics():
    """Endpoint para estatísticas detalhadas"""
    stats = AppStatistics.query.first()
    total_users = User.query.count()
    premium_users = User.query.filter_by(is_premium=True).count()
    
    return jsonify({
        "status": "success",
        "statistics": stats.to_dict() if stats else {},
        "users": {
            "total": total_users,
            "premium": premium_users,
            "free": total_users - premium_users
        }
    })

@main_bp.route('/admin/clear-cache', methods=['POST'])
@jwt_required()
def admin_clear_cache():
    """Rota administrativa para limpar cache manualmente"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        # Apenas admin pode limpar cache
        if not user or not user.is_admin:
            return jsonify({"error": "Acesso não autorizado"}), 403
        
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

@main_bp.route('/admin/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """Listar todos os usuários (apenas admin)"""
    try:
        user_id = int(get_jwt_identity())
        current_user = User.query.get(user_id)
        
        if not current_user or not current_user.is_admin:
            return jsonify({"error": "Acesso não autorizado"}), 403
        
        users = User.query.all()
        return jsonify({
            "users": [user.to_dict() for user in users],
            "total": len(users)
        })
        
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@main_bp.route('/admin/user/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Atualizar usuário (apenas admin)"""
    try:
        admin_id = get_jwt_identity()
        admin = User.query.get(admin_id)

        if not admin or not admin.is_admin:
            return jsonify({"error": "Acesso não autorizado"}), 403

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404

        data = request.get_json()
        if 'is_premium' in data:
            user.is_premium = data['is_premium']
        if 'is_admin' in data:
            user.is_admin = data['is_admin']

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Usuário atualizado",
            "user": user.to_dict()
        })

    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@main_bp.route('/admin/user/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Excluir usuário (apenas admin)"""
    try:
        admin_id = get_jwt_identity()
        admin = User.query.get(admin_id)

        if not admin or not admin.is_admin:
            return jsonify({"error": "Acesso não autorizado"}), 403

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404

        # Não permitir excluir o próprio usuário admin
        if user.id == admin_id:
            return jsonify({"error": "Não é possível excluir o próprio usuário"}), 400

        # Excluir histórico de gerações do usuário
        GenerationHistory.query.filter_by(user_id=user_id).delete()

        # Excluir feedback do usuário
        UserFeedback.query.filter_by(user_id=user_id).delete()

        # Excluir o usuário
        db.session.delete(user)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Usuário excluído com sucesso"
        })

    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500
    
@main_bp.route('/api/admin/dashboard', methods=['GET'])
@jwt_required()
def admin_dashboard():
    """Dashboard administrativo"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user or not user.is_admin:
            return jsonify({"error": "Acesso não autorizado"}), 403
        
        # Estatísticas
        total_users = User.query.count()
        premium_users = User.query.filter_by(is_premium=True).count()
        total_ideas = GenerationHistory.query.filter_by(type='ideas').count()
        total_scripts = GenerationHistory.query.filter_by(type='script').count()
        
        return jsonify({
            "status": "success",
            "dashboard": {
                "users": {
                    "total": total_users,
                    "premium": premium_users,
                    "free": total_users - premium_users
                },
                "content": {
                    "ideas_generated": total_ideas,
                    "scripts_generated": total_scripts
                },
                "system": {
                    "ai_configured": not ai_service.fallback_mode,
                    "database": "connected"
                }
            }
        })

    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500
    
@main_bp.route('/admin/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Obter dados de um usuário específico"""
    try:
        admin_id = int(get_jwt_identity())
        admin = User.query.get(admin_id)
        
        if not admin or not admin.is_admin:
            return jsonify({"error": "Acesso não autorizado"}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404
        
        return jsonify(user.to_dict())
        
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@main_bp.route('/admin/content/history', methods=['GET'])
@jwt_required()
def get_all_content_history():
    """Retorna todo o histórico de gerações para o admin, com paginação."""
    try:
        admin_id = int(get_jwt_identity())
        admin = User.query.get(admin_id)

        if not admin or not admin.is_admin:
            return jsonify({"error": "Acesso não autorizado"}), 403

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 15, type=int)

        # Query com join para obter o email do usuário
        history_query = db.session.query(
            GenerationHistory, User.email
        ).outerjoin(
            User, GenerationHistory.user_id == User.id
        ).order_by(
            GenerationHistory.created_at.desc()
        )

        paginated_history = history_query.paginate(page=page, per_page=per_page, error_out=False)

        # Formatar a resposta
        history_list = []
        for history_item, user_email in paginated_history.items:
            item_dict = history_item.to_dict()
            item_dict['user_email'] = user_email or 'Anônimo'
            history_list.append(item_dict)

        return jsonify({
            'history': history_list,
            'total': paginated_history.total,
            'pages': paginated_history.pages,
            'current_page': page
        })

    except Exception as e:
        current_app.logger.error(f"Erro ao buscar histórico de conteúdo: {e}", exc_info=True)
        return jsonify({"error": "Erro interno ao buscar histórico"}), 500

# ======================
# WEB SOCKET EVENTS
# ======================

def init_socketio(socketio):
    """Inicializar eventos WebSocket"""

    @socketio.on('connect')
    def handle_connect():
        print('Cliente conectado ao WebSocket')
        emit('connected', {'status': 'success'})

    @socketio.on('disconnect')
    def handle_disconnect():
        print('Cliente desconectado do WebSocket')

    @socketio.on('join_admin')
    def handle_join_admin(data):
        """Admin se junta à sala de administração"""
        try:
            token = data.get('token')
            if not token:
                emit('error', {'message': 'Token não fornecido'})
                return

            # Verificar se é admin
            from flask_jwt_extended import decode_token
            decoded = decode_token(token)
            user_id = decoded['sub']
            user = User.query.get(user_id)

            if user and user.is_admin:
                join_room('admin_room')
                emit('joined_admin', {'status': 'success'})
                print(f'Admin {user.email} entrou na sala admin')
            else:
                emit('error', {'message': 'Acesso não autorizado'})

        except Exception as e:
            emit('error', {'message': f'Erro: {str(e)}'})

    @socketio.on('leave_admin')
    def handle_leave_admin():
        leave_room('admin_room')
        emit('left_admin', {'status': 'success'})

    @socketio.on('request_stats')
    def handle_request_stats():
        """Enviar estatísticas em tempo real para admin"""
        try:
            # Usuários online (login nas últimas 30 min)
            from datetime import timedelta
            recent_time = datetime.utcnow() - timedelta(minutes=30)
            online_users = User.query.filter(User.last_login > recent_time).count()

            # Gerações por minuto (nas últimas 30 min)
            recent_generations = GenerationHistory.query.filter(GenerationHistory.created_at > recent_time).count()
            generations_per_minute = round(recent_generations / 30, 2)

            # Estatísticas gerais
            total_users = User.query.count()
            premium_users = User.query.filter_by(is_premium=True).count()
            total_ideas = GenerationHistory.query.filter_by(type='ideas').count()
            total_scripts = GenerationHistory.query.filter_by(type='script').count()

            emit('stats_update', {
                'onlineUsers': online_users,
                'generationsPerMinute': generations_per_minute,
                'totalUsers': total_users,
                'premiumUsers': premium_users,
                'totalIdeas': total_ideas,
                'totalScripts': total_scripts,
                'timestamp': datetime.utcnow().isoformat()
            })

        except Exception as e:
            emit('error', {'message': f'Erro ao obter estatísticas: {str(e)}'})

def broadcast_stats_update(socketio):
    """Função para broadcast de atualizações de estatísticas"""
    try:
        # Usuários online (login nas últimas 30 min)
        from datetime import timedelta
        recent_time = datetime.utcnow() - timedelta(minutes=30)
        online_users = User.query.filter(User.last_login > recent_time).count()

        # Gerações por minuto (nas últimas 30 min)
        recent_generations = GenerationHistory.query.filter(GenerationHistory.created_at > recent_time).count()
        generations_per_minute = round(recent_generations / 30, 2)

        # Estatísticas gerais
        total_users = User.query.count()
        premium_users = User.query.filter_by(is_premium=True).count()
        total_ideas = GenerationHistory.query.filter_by(type='ideas').count()
        total_scripts = GenerationHistory.query.filter_by(type='script').count()

        socketio.emit('stats_update', {
            'onlineUsers': online_users,
            'generationsPerMinute': generations_per_minute,
            'totalUsers': total_users,
            'premiumUsers': premium_users,
            'totalIdeas': total_ideas,
            'totalScripts': total_scripts,
            'timestamp': datetime.utcnow().isoformat()
        }, room='admin_room')

    except Exception as e:
        print(f'Erro ao broadcast estatísticas: {str(e)}')

def broadcast_user_update(socketio, user_data):
    """Broadcast de atualização de usuário"""
    socketio.emit('user_update', user_data, room='admin_room')

def broadcast_new_user(socketio, user_data):
    """Broadcast de novo usuário"""
    socketio.emit('new_user', user_data, room='admin_room')
    
