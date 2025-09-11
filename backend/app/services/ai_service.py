import os
import google.generativeai as genai
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

class AIService:
    def __init__(self):
        print("🔄 Inicializando HelpubliAI Service...")
        
        # Obter chave API do ambiente
        self.api_key = os.environ.get('GEMINI_API_KEY')
        
        # Verificar se a chave existe
        if not self.api_key or self.api_key == 'sua_chave_aqui_cole_a_chave_que_vc_gerou':
            print("⚠️  AVISO: GEMINI_API_KEY não configurada. Usando modo simulado.")
            self.mode = 'simulated'
            return
        
        try:
            # Configurar API do Google Gemini
            genai.configure(api_key=self.api_key)
            
            # Tentar usar o modelo mais recente
            try:
                self.model = genai.GenerativeModel('gemini-pro')
                self.mode = 'gemini'
                print("✅ Modelo configurado: gemini-pro")
            except Exception as model_error:
                print(f"❌ Erro ao configurar modelo: {model_error}")
                self.mode = 'simulated'
                print("🔁 Usando modo simulado como fallback")
                
        except Exception as e:
            print(f"❌ Erro ao configurar Gemini: {e}")
            self.mode = 'simulated'
            print("🔁 Usando modo simulado como fallback")
    
    def generate_ideas(self, niche, audience, count=5):
        """Gera ideias de conteúdo"""
        if self.mode == 'simulated':
            print("🔁 Gerando ideias em modo simulado")
            return self._get_fallback_ideas(niche, audience, count)
        
        try:
            prompt = f"""
            Gere {count} ideias criativas para vídeos do TikTok/Instagram Reels no nicho de {niche} 
            para o público-alvo de {audience}. 

            REQUISITOS:
            1. Seja criativo e original
            2. Foco em humor e viralidade
            3. Títulos chamativos (máximo 60 caracteres)
            4. Descrições claras e objetivas (1-2 linhas)
            5. 3-5 hashtags relevantes

            FORMATO DE RESPOSTA (para cada ideia):
            Título: [Título criativo]
            Descrição: [Descrição de 1-2 linhas]
            Hashtags: #[hashtag1] #[hashtag2] #[hashtag3]
            ---
            """
            
            response = self.model.generate_content(prompt)
            ideas = self._parse_ideas_response(response.text, count, niche, audience)
            print(f"✅ {len(ideas)} ideias geradas usando Gemini")
            return ideas
            
        except Exception as e:
            print(f"❌ Erro ao gerar ideias: {e}")
            return self._get_fallback_ideas(niche, audience, count)
    
    def generate_script(self, idea):
        """Gera um roteiro baseado em uma ideia"""
        if self.mode == 'simulated':
            print("🔁 Gerando roteiro em modo simulado")
            return self._get_fallback_script(idea)
        
        try:
            prompt = f"""
            Crie um roteiro COMPLETO para um vídeo do TikTok/Instagram Reels baseado nesta ideia:
            "{idea}"

            ESTRUTURA DO ROTEIRO:
            1. Título do vídeo
            2. Duração total (15-30 segundos)
            3. Cenário/Ambiente
            4. Sequência temporal detalhada (ex: 0-3s, 3-8s, etc.)
            5. Ações e diálogos para cada momento
            6. Efeitos sonoros sugeridos
            7. Textos para legenda
            8. Transições recomendadas
            9. Hashtags estratégicas

            Seja detalhado e específico. Formate a resposta de maneira organizada.
            """
            
            response = self.model.generate_content(prompt)
            print("✅ Roteiro gerado usando Gemini")
            return response.text
            
        except Exception as e:
            print(f"❌ Erro ao gerar roteiro: {e}")
            return self._get_fallback_script(idea)
    
    def improve_idea(self, idea, improvement_type="geral"):
        """Melhora uma ideia existente (nova funcionalidade)"""
        if self.mode == 'simulated':
            return {
                "improved_title": f"[Melhorado] {idea}",
                "improved_description": f"Descrição aprimorada para: {idea}",
                "improved_hashtags": "#melhorado #conteudo #viral"
            }
        
        try:
            prompt = f"""
            Melhore a seguinte ideia de conteúdo: "{idea}"
            
            Tipo de melhoria: {improvement_type}
            
            Forneça:
            1. Título melhorado (mais atraente)
            2. Descrição aprimorada (mais detalhada)
            3. Novas hashtags relevantes (3-5 hashtags)
            
            Formato:
            Título: [título melhorado]
            Descrição: [descrição aprimorada]
            Hashtags: #[hashtag1] #[hashtag2] #[hashtag3]
            """
            
            response = self.model.generate_content(prompt)
            return self._parse_improvement_response(response.text)
            
        except Exception as e:
            print(f"❌ Erro ao melhorar ideia: {e}")
            return {
                "improved_title": f"[Melhorado] {idea}",
                "improved_description": f"Descrição aprimorada para: {idea}",
                "improved_hashtags": "#melhorado #conteudo #viral"
            }
    
    def _parse_ideas_response(self, response_text, expected_count, niche, audience):
        """Processa a resposta do Gemini"""
        ideas = []
        lines = response_text.split('\n')
        current_idea = {}
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('Título:') or line.startswith('Title:'):
                if current_idea:
                    ideas.append(current_idea)
                title = line.split(':', 1)[1].strip()
                current_idea = {'title': title}
            
            elif line.startswith('Descrição:') or line.startswith('Description:'):
                if current_idea:
                    current_idea['description'] = line.split(':', 1)[1].strip()
            
            elif line.startswith('Hashtags:'):
                if current_idea:
                    current_idea['hashtags'] = line.split(':', 1)[1].strip()
            
            elif line.startswith('---') and current_idea:
                ideas.append(current_idea)
                current_idea = {}
        
        if current_idea:
            ideas.append(current_idea)
        
        # Completar com ideias fallback se necessário
        while len(ideas) < expected_count:
            ideas.append(self._create_fallback_idea(len(ideas) + 1, niche, audience))
        
        return ideas[:expected_count]
    
    def _parse_improvement_response(self, response_text):
        """Processa resposta de melhoria de ideia"""
        lines = response_text.split('\n')
        result = {
            "improved_title": "",
            "improved_description": "",
            "improved_hashtags": ""
        }
        
        for line in lines:
            line = line.strip()
            if line.startswith('Título:'):
                result["improved_title"] = line.split(':', 1)[1].strip()
            elif line.startswith('Descrição:'):
                result["improved_description"] = line.split(':', 1)[1].strip()
            elif line.startswith('Hashtags:'):
                result["improved_hashtags"] = line.split(':', 1)[1].strip()
        
        return result
    
    def _create_fallback_idea(self, index, niche, audience):
        """Cria uma ideia de fallback"""
        types = ["Reação engraçada", "Desafio divertido", "Top momentos", "Paródia", "Situação cômica"]
        descriptions = [
            "Vídeo engraçado e engaging para seu público",
            "Conteúdo viral que vai fazer sucesso",
            "Ideia criativa para bombar nas redes",
            "Conteúdo divertido que todos vão compartilhar"
        ]
        
        return {
            'title': f'{types[index % len(types)]} de {niche} para {audience}',
            'description': descriptions[index % len(descriptions)],
            'hashtags': f'#{niche} #{audience} #humor #viral #engraçado'
        }
    
    def _get_fallback_ideas(self, niche, audience, count):
        """Ideias para quando a API não está disponível"""
        ideas = []
        for i in range(count):
            ideas.append(self._create_fallback_idea(i, niche, audience))
        print(f"🔁 Geradas {len(ideas)} ideias em modo simulado")
        return ideas
    
    def _get_fallback_script(self, idea):
        """Roteiro para quando a API não está disponível"""
        # Extrair possíveis palavras-chave da ideia para usar como hashtags
        keywords = idea.lower().split()[:3]  # Pega as primeiras 3 palavras
        hashtag_keywords = " ".join([f"#{kw}" for kw in keywords if len(kw) > 3])
        
        script = f"""
📝 ROTEIRO DETALHADO PARA: {idea}

⏰ DURAÇÃO TOTAL: 20-25 segundos

🎬 CENÁRIO: Ambiente bem iluminado e casual

🎯 PÚBLICO: Jovens e adultos que apreciam humor

⏱️  LINHA DO TEMPO:

[0-5 SEGUNDOS] - GANCHO INICIAL
• Entrada impactante com expressão facial exagerada
• Texto na tela explicando a situação rapidamente
• Efeito sonoro: "whoosh" ou "ding" para chamar atenção

[5-15 SEGUNDOS] - DESENVOLVIMENTO
• Progressão da história com cortes rápidos
• 2-3 takes mostrando diferentes ângulos
• Mudanças expressivas de rosto e linguagem corporal
• Música de fundo: Trend atual do TikTok (30% volume)

[15-22 SEGUNDOS] - CLÍMAX
• Momento mais engraçado da cena
• Reação exagerada à situação
• Texto na tela: "O resultado 👀" ou "E então..."
• Efeito sonoro: Risadas ou suspense

[22-25 SEGUNDOS] - FINAL E CHAMADA PARA AÇÃO
• Resolução rápida e satisfatória
• Olhar direto para câmera com sorriso
• Gestual pedindo like/compartilhamento
• Texto: "Compartilha se riu! ❤️ Salva pra ver depois! 💾"

🏷️  HASHTAGS SUGERIDAS:
{hashtag_keywords}
#viral 
#engraçado 
#tiktok 
#comedia 
#humorbrasil

💡 DICAS DE PRODUÇÃO:
• Use iluminação natural sempre que possível
• Mantenha edição rápida e dinâmica (cortes a cada 2-3 segundos)
• Adicione legendas claras e objetivas
• Use transições criativas entre cenas
• Teste o áudio antes de gravar
• Mantenha energia alta durante toda a gravação
"""
        print("🔁 Roteiro gerado em modo simulado")
        return script

# Criar instância global do serviço
try:
    ai_service = AIService()
    print("✅ Serviço de IA inicializado com sucesso!")
except Exception as e:
    print(f"❌ Erro crítico ao inicializar serviço de IA: {e}")
    # Fallback extremo
    class FallbackService:
        def generate_ideas(self, *args, **kwargs): 
            return [{
                "title": "Ideia Simulada - Modo Offline",
                "description": "Serviço de IA não disponível. Verifique a conexão.",
                "hashtags": "#simulado #offline"
            }]
        def generate_script(self, *args, **kwargs): 
            return "Roteiro simulado - Serviço de IA não disponível. Verifique sua conexão e chave API."
        def improve_idea(self, *args, **kwargs):
            return {
                "improved_title": "Modo Offline - Verifique a API",
                "improved_description": "Serviço de IA indisponível",
                "improved_hashtags": "#offline #error"
            }
    ai_service = FallbackService()