from app import create_app
from app.models import db, GenerationHistory, AppStatistics

def check_database():
    print("🔍 Verificando banco de dados...")
    
    app = create_app()
    
    with app.app_context():
        print("📊 Estatísticas do banco:")
        stats = AppStatistics.query.first()
        if stats:
            print("Estatísticas:", stats.to_dict())
        else:
            print("❌ Nenhuma estatística encontrada")
        
        print("\n📋 Histórico:")
        history = GenerationHistory.query.all()
        print(f"Registros: {len(history)}")
        
        for item in history:
            print(f" - {item.type}: {item.created_at} (ID: {item.id})")
        
        print(f"\n✅ Banco verificado com sucesso!")

if __name__ == "__main__":
    check_database()