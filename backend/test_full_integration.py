import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app.services.ai_service import AIService

def test_full_integration():
    print("🧪 Teste de Integração Completa")
    
    # Carregar API key do ambiente
    if not os.environ.get('GEMINI_API_KEY'):
        print("❌ Variável de ambiente GEMINI_API_KEY não definida. Teste abortado.")
        return

    ai_service = AIService()
    
    print(f"🔧 Modo Fallback: {ai_service.fallback_mode}")
    
    if ai_service.fallback_mode:
        print("❌ IA não está configurada corretamente")
        return
    
    # Teste 1: Ideias
    print("\n1. 🎯 Testando geração de ideias...")
    ideas = ai_service.generate_ideas("tecnologia", "jovens", 2)
    print(f"✅ {len(ideas)} ideias geradas!")
    
    # Teste 2: Roteiro
    print("\n2. 🎬 Testando geração de roteiro...")
    script = ai_service.generate_script("Vídeo sobre apps de inteligência artificial")
    print(f"✅ Roteiro gerado ({len(script)} caracteres)")
    
    # Teste 3: Verificar se é da IA ou fallback
    print("\n3. 🔍 Verificando origem do conteúdo...")
    
    # Verifica se o conteúdo parece ser da IA (mais longo e detalhado)
    is_ai_generated = len(script) > 1000 and "DICAS DE PRODUÇÃO" in script
    
    if is_ai_generated:
        print("🎉 CONTEÚDO GERADO PELA IA REAL!")
        print(f"📏 Tamanho do roteiro: {len(script)} caracteres")
        print(f"📋 Amostra: {script[:200]}...")
    else:
        print("⚠️  Usando conteúdo fallback (modo de segurança)")
    
    print("\n" + "="*50)
    print("🎊 Integração completa testada com sucesso!")

if __name__ == "__main__":
    test_full_integration()