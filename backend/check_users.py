from app import create_app
from app.models import User

def check_users():
    app = create_app()
    
    with app.app_context():
        users = User.query.all()
        
        print(f"📊 Total de usuários: {len(users)}")
        print("=" * 50)
        
        for user in users:
            print(f"👤 ID: {user.id}")
            print(f"📧 Email: {user.email}")
            print(f"👤 Nome: {user.name}")
            print(f"⭐ Premium: {user.is_premium}")
            print(f"📅 Criado em: {user.created_at}")
            print(f"🔗 Último login: {user.last_login}")
            print("-" * 30)

if __name__ == "__main__":
    check_users()