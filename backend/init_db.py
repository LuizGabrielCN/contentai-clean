import os
from app import create_app, db
from app.models import AppStatistics

def initialize_database():
    """
    Inicializa o banco de dados. Cria o arquivo .db e todas as tabelas.
    """
    app, _ = create_app()
    with app.app_context():
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        if os.path.exists(db_path):
            print(f"⚠️  O banco de dados '{db_path}' já existe. Nenhuma ação foi tomada.")
            print("Se desejar recriar o banco, apague o arquivo e execute este script novamente.")
            return

        print("🚀 Criando todas as tabelas do banco de dados...")
        db.create_all()

        # Adicionar dados iniciais para garantir que o banco está pronto
        print("📊 Populando dados iniciais...")
        initial_stats = AppStatistics()
        db.session.add(initial_stats)
        db.session.commit()

        print("✅ Tabelas criadas com sucesso!")

if __name__ == '__main__':
    initialize_database()