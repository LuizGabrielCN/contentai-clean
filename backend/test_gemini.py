import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app.services.ai_service import AIService
import google.generativeai as genai

def test_models():
    """Testa quais modelos estão disponíveis"""
    print("🔍 Verificando modelos disponíveis...")
    
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("❌ Variável de ambiente GEMINI_API_KEY não definida. Teste abortado.")
        return
    genai.configure(api_key=api_key)
    
    try:
        models = genai.list_models()
        print("✅ Modelos disponíveis:")
        for model in models:
            if 'gemini' in model.name.lower():
                print(f"   - {model.name} (suporta: {[method for method in model.supported_generation_methods]})")
    except Exception as e:
        print(f"❌ Erro ao listar modelos: {e}")

def test_gemini():
    print("🧪 Testando integração com Gemini...")
    
    ai_service = AIService()
    
    print(f"✅ Modo Fallback: {ai_service.fallback_mode}")
    
    if ai_service.fallback_mode:
        print("❌ API Key não configurada ou modelos não disponíveis.")
        test_models()
        return
    
    # Teste simples para verificar se o modelo funciona
    try:
        test_response = ai_service.model.generate_content("Responda apenas 'OK'")
        print(f"✅ Teste de conexão: {test_response.text}")
    except Exception as e:
        print(f"❌ Erro no teste de conexão: {e}")
        test_models()
        return
    
    # Testar geração de ideias
    print("\n1. 🎯 Testando geração de ideias:")
    try:
        ideas = ai_service.generate_ideas("tecnologia", "jovens", 2)
        print(f"✅ {len(ideas)} ideias geradas com sucesso!")
        
        for i, idea in enumerate(ideas, 1):
            print(f"\n   💡 Ideia {i}:")
            print(f"   Título: {idea['title']}")
            print(f"   Descrição: {idea['description']}")
            print(f"   Hashtags: {idea['hashtags']}")
            
    except Exception as e:
        print(f"❌ Erro ao gerar ideias: {e}")

if __name__ == "__main__":
    test_gemini()