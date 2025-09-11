import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app.services.ai_service import AIService

def test_gemini():
    print("Testando integração com Gemini Pro...")
    
    ai_service = AIService()
    
    # Testar geração de ideias
    print("\n1. Testando geração de ideias:")
    ideas = ai_service.generate_ideas("humor", "jovens", 3)
    for i, idea in enumerate(ideas, 1):
        print(f"\nIdeia {i}:")
        print(f"Título: {idea['title']}")
        print(f"Descrição: {idea['description']}")
        print(f"Hashtags: {idea['hashtags']}")
    
    # Testar geração de roteiro
    print("\n2. Testando geração de roteiro:")
    script = ai_service.generate_script("Vídeo de humor sobre situações awkward no elevador")
    print(f"Roteiro:\n{script}")

if __name__ == "__main__":
    test_gemini()