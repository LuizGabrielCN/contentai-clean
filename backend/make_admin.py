from app import create_app
from app.models import User, db

def make_admin(email):
    app, _ = create_app()
    
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"❌ Usuário com email {email} não encontrado")
            return False
        
        user.is_admin = True
        user.is_premium = True
        db.session.commit()
        
        print(f"✅ {user.email} agora é ADMINISTRADOR e PREMIUM!")
        print(f"   👤 Nome: {user.name}")
        print(f"   📧 Email: {user.email}") 
        print(f"   👑 Admin: {user.is_admin}")
        print(f"   ⭐ Premium: {user.is_premium}")
        print(f"   📅 Criado em: {user.created_at}")
        
        return True

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Uso: python make_admin.py <email>")
        sys.exit(1)
    
    make_admin(sys.argv[1])