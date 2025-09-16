import requests
import json

def test_api():
    print("🧪 Testando APIs...")
    
    # Testar health check
    print("\n1. 🩺 Health Check:")
    response = requests.get('http://localhost:5000/api/health')
    print(f"Status: {response.status_code}")
    print(f"Resposta: {json.dumps(response.json(), indent=2)}")
    
    # Testar geração de ideias
    print("\n2. 💡 Gerando ideias:")
    response = requests.post(
        'http://localhost:5000/api/generate-ideas',
        json={'niche': 'tecnologia', 'audience': 'jovens', 'count': 2}
    )
    print(f"Status: {response.status_code}")
    print(f"Resposta: {json.dumps(response.json(), indent=2)}")
    
    # Testar estatísticas
    print("\n3. 📊 Estatísticas:")
    response = requests.get('http://localhost:5000/api/statistics')
    print(f"Status: {response.status_code}")
    print(f"Resposta: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    test_api()