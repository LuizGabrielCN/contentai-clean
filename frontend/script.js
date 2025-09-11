// Configurações da API
const API_BASE_URL = ''; // Mesma origem agora

// Elementos DOM
let currentTab = 'gerador-ideias';

// Inicialização quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Esconder loading screen após 1.5s
    setTimeout(() => {
        document.getElementById('loading').style.display = 'none';
    }, 1500);

    // Configurar navegação por tabs
    setupTabs();
    
    // Configurar event listeners
    setupEventListeners();
    
    // Carregar histórico do localStorage
    loadHistory();
}

function setupTabs() {
    const navLinks = document.querySelectorAll('.nav-link');
    const tabContents = document.querySelectorAll('.tab-content');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Remover classe active de todos os links
            navLinks.forEach(l => l.classList.remove('active'));
            
            // Adicionar classe active ao link clicado
            link.classList.add('active');
            
            // Esconder todos os conteúdos de tab
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Mostrar o conteúdo da tab correspondente
            const targetTab = link.getAttribute('href').substring(1);
            document.getElementById(targetTab).classList.add('active');
            
            currentTab = targetTab;
        });
    });
}

function setupEventListeners() {
    // Botão de gerar ideias
    document.getElementById('generate-ideas-btn').addEventListener('click', generateIdeas);
    
    // Botão de gerar roteiro
    document.getElementById('generate-script-btn').addEventListener('click', generateScript);
    
    // Botões de ação
    document.getElementById('export-ideas').addEventListener('click', exportIdeas);
    document.getElementById('clear-ideas').addEventListener('click', clearIdeas);
    document.getElementById('copy-script').addEventListener('click', copyScript);
    document.getElementById('save-script').addEventListener('click', saveScript);
}

// Funções da API
async function generateIdeas() {
    const niche = document.getElementById('niche').value.trim();
    const audience = document.getElementById('audience').value.trim();
    const count = document.getElementById('count').value;
    
    // Validação
    if (!niche || !audience) {
        showToast('Por favor, preencha todos os campos', 'error');
        return;
    }
    
    // Mostrar loading no botão
    const btn = document.getElementById('generate-ideas-btn');
    const btnText = btn.querySelector('.btn-text');
    const btnLoading = btn.querySelector('.btn-loading');
    
    btnText.style.display = 'none';
    btnLoading.style.display = 'inline';
    btn.disabled = true;
    
    try {
        const response = await fetch('/api/generate-ideas', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ niche, audience, count: parseInt(count) })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayIdeas(data.ideas);
            saveToHistory('ideas', { niche, audience, ideas: data.ideas });
            showToast(`${data.ideas.length} ideias geradas com sucesso!`, 'success');
        } else {
            throw new Error(data.error || 'Erro ao gerar ideias');
        }
        
    } catch (error) {
        console.error('Erro:', error);
        showToast(error.message, 'error');
        
        // Fallback: mostrar ideias de exemplo
        displayIdeas(getFallbackIdeas(niche, audience, count));
    } finally {
        // Restaurar botão
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
        btn.disabled = false;
    }
}

async function generateScript() {
    const idea = document.getElementById('script-idea').value.trim();
    
    if (!idea) {
        showToast('Por favor, insira uma ideia', 'error');
        return;
    }
    
    // Mostrar loading no botão
    const btn = document.getElementById('generate-script-btn');
    const btnText = btn.querySelector('.btn-text');
    const btnLoading = btn.querySelector('.btn-loading');
    
    btnText.style.display = 'none';
    btnLoading.style.display = 'inline';
    btn.disabled = true;
    
    try {
        const response = await fetch('/api/generate-script', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ idea })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayScript(data.script);
            saveToHistory('script', { idea, script: data.script });
            showToast('Roteiro gerado com sucesso!', 'success');
        } else {
            throw new Error(data.error || 'Erro ao gerar roteiro');
        }
        
    } catch (error) {
        console.error('Erro:', error);
        showToast(error.message, 'error');
        
        // Fallback: mostrar roteiro de exemplo
        displayScript(getFallbackScript(idea));
    } finally {
        // Restaurar botão
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
        btn.disabled = false;
    }
}

// Funções de exibição
function displayIdeas(ideas) {
    const ideasGrid = document.getElementById('ideas-grid');
    const resultsSection = document.getElementById('ideas-results');
    
    // Limpar grid anterior
    ideasGrid.innerHTML = '';
    
    // Adicionar cada ideia ao grid
    ideas.forEach((idea, index) => {
        const ideaCard = document.createElement('div');
        ideaCard.className = 'idea-card';
        ideaCard.innerHTML = `
            <h5>💡 ${idea.title}</h5>
            <p>${idea.description}</p>
            <div class="hashtags">${idea.hashtags}</div>
            <div class="idea-actions">
                <button class="btn btn-outline" onclick="useIdeaForScript('${idea.title.replace(/'/g, "\\'")}')">
                    Usar para Roteiro
                </button>
            </div>
        `;
        ideasGrid.appendChild(ideaCard);
    });
    
    // Mostrar seção de resultados
    resultsSection.style.display = 'block';
}

function displayScript(script) {
    const scriptOutput = document.getElementById('script-output');
    const resultsSection = document.getElementById('script-results');
    
    // Formatar o script (substituir quebras de linha por <br>)
    const formattedScript = script.replace(/\n/g, '<br>').replace(/ /g, '&nbsp;');
    scriptOutput.innerHTML = formattedScript;
    
    // Mostrar seção de resultados
    resultsSection.style.display = 'block';
}

// Funções de utilidade
function useIdeaForScript(idea) {
    document.getElementById('script-idea').value = idea;
    
    // Mudar para a tab de roteiros
    document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
    document.querySelector('[href="#criar-roteiros"]').classList.add('active');
    
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    document.getElementById('criar-roteiros').classList.add('active');
    
    currentTab = 'criar-roteiros';
    showToast('Ideia copiada para o criador de roteiros!', 'success');
}

function exportIdeas() {
    const ideas = Array.from(document.querySelectorAll('.idea-card')).map(card => ({
        title: card.querySelector('h5').textContent.replace('💡 ', ''),
        description: card.querySelector('p').textContent,
        hashtags: card.querySelector('.hashtags').textContent
    }));
    
    const dataStr = JSON.stringify(ideas, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `ideas-contentai-${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
    
    showToast('Ideias exportadas com sucesso!', 'success');
}

function clearIdeas() {
    if (confirm('Tem certeza que deseja limpar todas as ideias geradas?')) {
        document.getElementById('ideas-grid').innerHTML = '';
        document.getElementById('ideas-results').style.display = 'none';
        showToast('Ideias limpas!', 'success');
    }
}

async function copyScript() {
    const script = document.getElementById('script-output').textContent;
    
    try {
        await navigator.clipboard.writeText(script);
        showToast('Roteiro copiado para a área de transferência!', 'success');
    } catch (error) {
        showToast('Erro ao copiar roteiro', 'error');
    }
}

function saveScript() {
    const script = document.getElementById('script-output').textContent;
    const idea = document.getElementById('script-idea').value;
    
    const blob = new Blob([script], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `roteiro-${idea.substring(0, 20).toLowerCase().replace(/\s+/g, '-')}.txt`;
    link.click();
    
    URL.revokeObjectURL(url);
    showToast('Roteiro salvo com sucesso!', 'success');
}

// Histórico e LocalStorage
function saveToHistory(type, data) {
    const history = JSON.parse(localStorage.getItem('contentai_history') || '[]');
    
    history.unshift({
        type,
        data,
        timestamp: new Date().toISOString(),
        id: Date.now()
    });
    
    // Manter apenas os últimos 50 itens
    if (history.length > 50) {
        history.pop();
    }
    
    localStorage.setItem('contentai_history', JSON.stringify(history));
    loadHistory();
}

function loadHistory() {
    const history = JSON.parse(localStorage.getItem('contentai_history') || '[]');
    const historyList = document.getElementById('history-list');
    const emptyState = document.querySelector('.empty-state');
    
    if (history.length === 0) {
        emptyState.style.display = 'block';
        historyList.innerHTML = '';
        return;
    }
    
    emptyState.style.display = 'none';
    historyList.innerHTML = '';
    
    history.forEach(item => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        
        let content = '';
        if (item.type === 'ideas') {
            content = `
                <h5>💡 ${item.data.ideas.length} Ideias - ${item.data.niche} para ${item.data.audience}</h5>
                <p>${item.data.ideas[0]?.title || 'Ideia gerada'}</p>
            `;
        } else {
            content = `
                <h5>📝 Roteiro - ${item.data.idea.substring(0, 50)}${item.data.idea.length > 50 ? '...' : ''}</h5>
            `;
        }
        
        content += `<div class="timestamp">${new Date(item.timestamp).toLocaleString('pt-BR')}</div>`;
        
        historyItem.innerHTML = content;
        historyList.appendChild(historyItem);
    });
}

// Toast notifications
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    
    setTimeout(() => {
        toast.className = 'toast';
    }, 3000);
}

// Fallbacks para quando a API não está disponível
function getFallbackIdeas(niche, audience, count) {
    const ideas = [
        {
            title: `Reações engraçadas a ${niche}`,
            description: `Vídeo mostrando reações exageradas para ${audience}`,
            hashtags: `#${niche} #${audience} #humor #viral`
        },
        {
            title: `Desafio de ${niche}`,
            description: `Desafio divertido envolvendo ${niche} para ${audience}`,
            hashtags: `#${niche} #${audience} #desafio #divertido`
        },
        {
            title: `Top 3 momentos de ${niche}`,
            description: `Compilação dos melhores momentos para ${audience}`,
            hashtags: `#${niche} #${audience} #top3 #melhoresmomentos`
        },
        {
            title: `Paródia de ${niche}`,
            description: `Paródia engraçada sobre ${niche} para ${audience}`,
            hashtags: `#${niche} #${audience} #parodia #engraçado`
        },
        {
            title: `Situações cômicas de ${niche}`,
            description: `Vídeo mostrando situações engraçadas para ${audience}`,
            hashtags: `#${niche} #${audience} #comedia #risada`
        }
    ];
    
    return ideas.slice(0, count);
}

function getFallbackScript(idea) {
    // Extrair possíveis palavras-chave da ideia para usar como hashtags
    const keywords = idea.toLowerCase().split(' ').slice(0, 3).filter(word => word.length > 3);
    const hashtagKeywords = keywords.map(kw => `#${kw}`).join(' ');
    
    return `
📝 ROTEIRO DETALHADO PARA: ${idea}

⏰ DURAÇÃO TOTAL: 20-25 segundos

🎬 CENÁRIO: Ambiente bem iluminado e casual

🎯 PÚBLICO: Jovens e adultos que apreciam conteúdo engaging

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
${hashtagKeywords}
#viral 
#engraçado 
#tiktok 
#comedia 
#conteudooriginal

💡 DICAS DE PRODUÇÃO:
• Use iluminação natural sempre que possível
• Mantenha edição rápida e dinâmica (cortes a cada 2-3 segundos)
• Adicione legendas claras e objetivas
• Use transições criativas entre cenas
• Teste o áudio antes de gravar
• Mantenha energia alta durante toda a gravação
`;
}

// Funções globais para uso nos botões HTML
window.useIdeaForScript = useIdeaForScript;