import os
import google.generativeai as genai
from typing import List, Dict
import logging

class AIService:
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        if not self.api_key:
            logging.warning("GEMINI_API_KEY não encontrada. Usando modo fallback.")
            self.fallback_mode = True
        else:
            genai.configure(api_key=self.api_key)
            
            # ✅ Usa um modelo que realmente existe da lista
            try:
                # Gemini 1.5 Flash é rápido e eficiente para nosso uso
                self.model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
                logging.info("✅ Gemini 1.5 Flash configurado com sucesso!")
                self.fallback_mode = False
            except Exception as e:
                logging.warning(f"❌ Erro ao configurar modelo: {e}")
                self.fallback_mode = True

    def generate_ideas(self, niche: str, audience: str, count: int = 5) -> List[Dict]:
        """Gera ideias de conteúdo usando Gemini AI"""
        
        if self.fallback_mode:
            return self._get_fallback_ideas(niche, audience, count)
        
        try:
            prompt = f"""
            Gere {count} ideias criativas de conteúdo para redes sociais (TikTok, Instagram Reels, YouTube Shorts).
            
            NICHÊ: {niche}
            PÚBLICO-ALVO: {audience}
            
            Para cada ideia, retorne APENAS um JSON object com:
            - title: título criativo (máx. 60 caracteres)
            - description: descrição detalhada (máx. 150 caracteres)  
            - hashtags: 4-5 hashtags relevantes

            Formato de resposta:
            [
                {{
                    "title": "Título da ideia 1",
                    "description": "Descrição detalhada...",
                    "hashtags": "#hashtag1 #hashtag2 #hashtag3"
                }},
                ...
            ]

            Seja criativo, viral e adequado para o público {audience} interessado em {niche}.
            """
            
            response = self.model.generate_content(prompt)
            ideas = self._parse_ai_response(response.text)
            
            return ideas[:count]
            
        except Exception as e:
            logging.error(f"Erro ao gerar ideias: {str(e)}")
            return self._get_fallback_ideas(niche, audience, count)

    def generate_script(self, idea: str) -> str:
        """Gera roteiro completo usando Gemini AI"""
        
        if self.fallback_mode:
            return self._get_fallback_script(idea)
        
        try:
            prompt = f"""
            Crie um roteiro COMPLETO e DETALHADO para um vídeo de 20-25 segundos para redes sociais.

            IDEIA: {idea}

            Estruture o roteiro com:

            📝 TÍTULO DO ROTEIRO
            ⏰ DURAÇÃO TOTAL: 20-25s

            🎬 CENÁRIO: [descrição do ambiente]
            🎯 PÚBLICO: [público-alvo]

            ⏱️ LINHA DO TEMPO:
            [0-5s] - GANCHO INICIAL: [ação rápida e impactante]
            [5-15s] - DESENVOLVIMENTO: [progressão da história]  
            [15-22s] - CLÍMAX: [momento mais engraçado/impactante]
            [22-25s] - FINAL: [resolução + call to action]

            🎵 TRILHA SONORA: [sugestão de música]
            📱 EFEITOS: [efeitos visuais e sonoros]
            🏷️ HASHTAGS: 5-6 hashtags relevantes

            💡 DICAS DE PRODUÇÃO: [3-4 dicas práticas]

            Seja detalhado, criativo e viral. Use emojis para organizar as seções.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logging.error(f"Erro ao gerar roteiro: {str(e)}")
            return self._get_fallback_script(idea)

    def _parse_ai_response(self, response_text: str) -> List[Dict]:
        """Parseia a resposta da AI para extrair o JSON"""
        import json
        import re
        
        try:
            # Tenta encontrar JSON na resposta
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                ideas = json.loads(json_match.group())
                return ideas
            else:
                raise ValueError("JSON não encontrado na resposta")
        except:
            # Fallback se o parsing falhar
            return self._get_fallback_ideas("humor", "jovens", 3)

    def _get_fallback_ideas(self, niche: str, audience: str, count: int) -> List[Dict]:
        """Ideias de fallback quando a API não está disponível"""
        ideas = [
            {
                "title": f"Reações engraçadas a {niche}",
                "description": f"Vídeo mostrando reações exageradas para {audience}",
                "hashtags": f"#{niche} #{audience} #humor #viral"
            },
            {
                "title": f"Desafio de {niche}",
                "description": f"Desafio divertido envolvendo {niche} para {audience}",
                "hashtags": f"#{niche} #{audience} #desafio #divertido"
            },
            {
                "title": f"Top 3 momentos de {niche}",
                "description": f"Compilação dos melhores momentos para {audience}",
                "hashtags": f"#{niche} #{audience} #top3 #melhoresmomentos"
            }
        ]
        return ideas[:count]

    def _get_fallback_script(self, idea: str) -> str:
        """Roteiro de fallback quando a API não está disponível"""
        return f"""
📝 ROTEIRO DETALHADO PARA: {idea}

⏰ DURAÇÃO TOTAL: 20-25 segundos

🎬 CENÁRIO: Ambiente bem iluminado e casual
🎯 PÚBLICO: Jovens e adultos que apreciam conteúdo engaging

⏱️ LINHA DO TEMPO:

[0-5 SEGUNDOS] - GANCHO INICIAL
• Entrada impactante com expressão facial exagerada
• Texto na tela: "{idea}"
• Efeito sonoro: "whoosh" para chamar atenção

[5-15 SEGUNDOS] - DESENVOLVIMENTO
• Progressão da história com cortes rápidos
• 2-3 takes mostrando diferentes ângulos
• Mudanças expressivas de rosto e linguagem corporal

[15-22 SEGUNDOS] - CLÍMAX
• Momento mais engraçado da cena
• Reação exagerada à situação
• Texto na tela: "O resultado 👀"

[22-25 SEGUNDOS] - FINAL E CHAMADA PARA AÇÃO
• Resolução rápida e satisfatória
• Olhar direto para câmera com sorriso
• Texto: "Compartilha se riu! ❤️ Salva pra ver depois! 💾"

🎵 TRILHA SONORA: Trend atual do TikTok (30% volume)
📱 EFEITOS: Transições suaves, texto animado

🏷️ HASHTAGS SUGERIDAS:
#{idea.replace(' ', '').lower()} 
#viral 
#engraçado 
#tiktok 
#conteudooriginal

💡 DICAS DE PRODUÇÃO:
• Use iluminação natural sempre que possível
• Mantenha edição rápida e dinâmica
• Adicione legendas claras e objetivas
• Teste o áudio antes de gravar
"""

# Instância global do serviço de IA
ai_service = AIService()