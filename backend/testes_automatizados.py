import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health():
    """Testa o health check da API"""
    print("🧪 Testando Health Check...")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.json()}")
    print("✅ Health Check OK\n")
    return response.status_code == 200

def test_statistics():
    """Testa as estatísticas"""
    print("📊 Testando Estatísticas...")
    response = requests.get(f"{BASE_URL}/api/statistics")
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.json()}")
    print("✅ Estatísticas OK\n")
    return response.status_code == 200

def test_generate_ideas():
    """Testa geração de ideias"""
    print("💡 Testando Geração de Ideias...")
    data = {
        "niche": "humor",
        "audience": "jovens",
        "count": 2
    }
    response = requests.post(f"{BASE_URL}/api/generate-ideas", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Ideias geradas: {len(result.get('ideas', []))}")
    for i, idea in enumerate(result.get('ideas', []), 1):
        print(f"  {i}. {idea['title']}")
    print("✅ Geração de Ideias OK\n")
    return response.status_code == 200

def test_generate_script():
    """Testa geração de roteiro"""
    print("🎬 Testando Geração de Roteiro...")
    data = {
        "idea": "Vídeo engraçado sobre situações do trabalho"
    }
    response = requests.post(f"{BASE_URL}/api/generate-script", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Roteiro gerado: {len(result.get('script', ''))} caracteres")
    print("✅ Geração de Roteiro OK\n")
    return response.status_code == 200

def test_feedback():
    """Testa envio de feedback"""
    print("📝 Testando Feedback...")
    data = {
        "message": "Teste automatizado de feedback - sistema funcionando bem!"
    }
    response = requests.post(f"{BASE_URL}/api/feedback", json=data)
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.json()}")
    print("✅ Feedback OK\n")
    return response.status_code == 200

def run_all_tests():
    """Executa todos os testes"""
    print("🚀 INICIANDO TESTES AUTOMATIZADOS DO CONTENTAI")
    print("=" * 50)
    
    tests = [
        test_health,
        test_statistics,
        test_generate_ideas,
        test_generate_script,
        test_feedback
    ]
    
    results = []
    for test in tests:
        try:
            success = test()
            results.append(success)
            time.sleep(1)  # Espera 1 segundo entre testes
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
            results.append(False)
    
    print("=" * 50)
    print("📋 RESULTADO DOS TESTES:")
    print(f"✅ Testes passados: {sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 TODOS OS TESTES PASSARAM! Sistema funcionando perfeitamente!")
    else:
        print("⚠️  Alguns testes falharam. Verifique o servidor.")
    
    return all(results)

if __name__ == "__main__":
    run_all_tests()