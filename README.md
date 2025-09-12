# 🚀 HelpubliAI - Criação de Conteúdo com IA

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-2.3-green)
![Google Gemini](https://img.shields.io/badge/Gemini-AI-orange)
![Status](https://img.shields.io/badge/Status-Production-brightgreen)

Gerador de ideias e roteiros virais para redes sociais usando Inteligência Artificial.

## ✨ Funcionalidades

- 💡 **Geração de Ideias** - Ideias criativas para TikTok, Instagram Reels, YouTube Shorts
- 📝 **Roteiros Completos** - Scripts detalhados com timing, cenários e hashtags
- 🎨 **Interface Responsiva** - Design moderno e mobile-friendly
- 🤖 **Powered by Gemini AI** - Tecnologia Google Gemini para conteúdo de qualidade
- 💾 **Histórico Local** - Salve e exporte suas criações
- 🔌 **API RESTful** - Integre com outras aplicações

## 🚀 Demo Online

**Acesse agora:** [https://contentai-clean-production.up.railway.app](https://contentai-clean-production.up.railway.app)

**Teste a API:**
```bash
curl https://contentai-clean-production.up.railway.app/api/health

🛠️ Tecnologias

    Backend: Python, Flask, Google Gemini API

    Frontend: HTML5, CSS3, JavaScript Vanilla

    Deploy: Railway, GitHub Actions

    IA: Google Generative AI

📦 Instalação Local
bash

# Clone o repositório
git clone https://github.com/LuizGabrielCN/contentai-clean.git

# Entre na pasta
cd contentai-clean/backend

# Instale dependências
pip install -r requirements.txt

# Execute
python serve_frontend.py

# Acesse: http://localhost:5000

🔌 API Endpoints

    GET /api/health - Status do serviço

    POST /api/generate-ideas - Gerar ideias de conteúdo

    POST /api/generate-script - Gerar roteiros completos

    POST /api/feedback - Enviar feedback

🎯 Exemplo de Uso
bash

# Gerar ideias
curl -X POST https://contentai-clean-production.up.railway.app/api/generate-ideas \
  -H "Content-Type: application/json" \
  -d '{"niche":"humor","audience":"jovens","count":3}'
