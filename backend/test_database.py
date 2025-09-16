# test_database.py
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.models import db, GenerationHistory, AppStatistics

app = create_app()

with app.app_context():
    print("🧪 Testando banco de dados...")
    
    # Verificar se as tabelas existem
    print("📊 Estatísticas:", AppStatistics.query.first().to_dict())
    
    # Contar registros
    history_count = GenerationHistory.query.count()
    print(f"📋 Histórico: {history_count} registros")
    
    print("✅ Banco de dados funcionando!")