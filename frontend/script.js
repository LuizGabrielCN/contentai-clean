// Configurações da API
const API_BASE_URL = '';

// Elementos DOM e estado
let currentTab = 'gerador-ideias';
let currentUser = null;
let authToken = localStorage.getItem('authToken');

// Inicialização quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Esconder loading screen após 1.5s
    setTimeout(() => {
        document.getElementById('loading').style.display = 'none';
    }, 1500);

    // ✅ VERIFICAR SE TODOS OS ELEMENTOS EXISTEM
    const requiredElements = [
        'auth-section', 'user-section', 'user-email', 'user-plan',
        'login-btn', 'register-btn', 'logout-btn'
    ];
    
    requiredElements.forEach(id => {
        if (!document.getElementById(id)) {
            console.error(`Elemento #${id} não encontrado no DOM`);
        }
    });

    // Configurar navegação por tabs
    setupTabs();
    
    // Configurar event listeners
    setupEventListeners();

    // ✅ CONFIGURAR EVENTOS DE TECLADO
    setupEnterKeyLogin();
    setupEnterKeyRegister();
    
    // Configurar tracking
    setupButtonTracking();
    setupErrorTracking();
    
    // Carregar histórico do localStorage
    loadHistory();
    
    // Verificar autenticação
    checkAuthentication();

    // ✅ VERIFICAR SE HÁ UM TOKEN DE RESET NA URL
    handleResetPasswordToken();
    
    // Trackear página carregada
    trackEvent('page', 'page_view', 'homepage');
    
    console.log('✅ HelpubliAI initialized with analytics');
}

// ======================
// SISTEMA DE AUTENTICAÇÃO
// ======================


function updateAuthUI() {
    const authSection = document.getElementById('auth-section');
    const userSection = document.getElementById('user-section');
    const userEmail = document.getElementById('user-email');
    const userPlan = document.getElementById('user-plan');
    const adminBtn = document.getElementById('admin-dashboard-btn');
    
    // ✅ VERIFICAR SE ELEMENTOS EXISTEM ANTES DE USAR
    if (!authSection || !userSection || !userEmail || !userPlan) {
        console.warn('Elementos de auth UI não encontrados');
        return;
    }
    
    if (currentUser) {
        authSection.style.display = 'none';
        userSection.style.display = 'flex';
        userEmail.textContent = currentUser.email;
        userPlan.textContent = currentUser.is_premium ? 'Premium' : 'Free';
        userPlan.className = currentUser.is_premium ? 'plan-badge premium' : 'plan-badge free';
        
        // ✅ Atualizar elementos premium-only
        const premiumElements = document.querySelectorAll('.premium-only');
        premiumElements.forEach(el => {
            el.style.display = currentUser.is_premium ? 'block' : 'none';
        });

        // ✅ Mostrar botão de admin se o usuário for admin
        if (adminBtn) {
            adminBtn.style.display = currentUser.is_admin ? 'inline-block' : 'none';
        }

    } else {
        authSection.style.display = 'block';
        userSection.style.display = 'none';
        if (adminBtn) {
            adminBtn.style.display = 'none';
        }
    }
}

async function login() {
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;
    
    if (!email || !password) {
        showToast('Preencha email e senha', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        console.log('Login response:', response.status, data); // ✅ Debug
        
        if (response.ok) {
            authToken = data.access_token;
            currentUser = data.user;
            localStorage.setItem('authToken', authToken);
            
            updateAuthUI();
            updateUIForLoggedInUser(currentUser);
            
            showToast('Login realizado com sucesso!', 'success');
            document.getElementById('login-modal').style.display = 'none';
            
        } else {
            // ✅ Mudar para mostrar mensagem específica da API
            showToast(data.error || 'Erro ao fazer login', 'error');
        }
        
    } catch (error) {
        console.error('Login error:', error);
        // ✅ Mostrar mensagem mais específica
        showToast('Erro de conexão. Tente novamente.', 'error');
    }
}

async function register() {
    const email = document.getElementById('register-email').value.trim();
    const password = document.getElementById('register-password').value;
    const name = document.getElementById('register-name').value.trim();
    
    if (!email || !password) {
        showToast('Email e senha são obrigatórios', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, name })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.access_token;
            currentUser = data.user;
            localStorage.setItem('authToken', authToken);
            updateUIForLoggedInUser(currentUser);
            showToast('Conta criada com sucesso!', 'success');
            
            // Fechar modal de registro
            document.getElementById('register-modal').style.display = 'none';
        } else {
            showToast(data.error, 'error');
        }
    } catch (error) {
        showToast('Erro ao criar conta', 'error');
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    
    // ✅ ATUALIZAR UI IMEDIATAMENTE
    updateAuthUI();
    showToast('Logout realizado com sucesso!', 'success');
    
    // ✅ RECARREGAR A PÁGINA PARA LIMPAR ESTADO COMPLETO
    setTimeout(() => {
        window.location.reload();
    }, 1000);
}

async function makeAuthenticatedRequest(url, options = {}) {
    const finalOptions = {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        }
    };
    
    if (authToken) {
        finalOptions.headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    const response = await fetch(url, finalOptions);
    
    // Se token expirado, fazer logout
    if (response.status === 401) {
        logout();
        throw new Error('Sessão expirada');
    }
    
    return response;
}

function updateUIForLoggedInUser(user) {
    // ✅ Verificar se elemento existe antes de usar
    const userInfoElement = document.getElementById('user-info');
    if (userInfoElement) {
        userInfoElement.innerHTML = `
            <span>${user.email}</span>
            <span class="plan-badge ${user.is_premium ? 'premium' : 'free'}">
                ${user.is_premium ? 'Premium' : 'Free'}
            </span>
        `;
    }
    
    // ✅ Mostrar/ocultar elementos baseado no plano
    const premiumElements = document.querySelectorAll('.premium-only');
    premiumElements.forEach(el => {
        if (el) {
            el.style.display = user.is_premium ? 'block' : 'none';
        }
    });
}

async function loadUserHistory() {
    if (!currentUser) return;
    
    try {
        const response = await makeAuthenticatedRequest('/api/user/history');
        if (response.ok) {
            const data = await response.json();
            displayUserHistory(data.history);
        }
    } catch (error) {
        console.error('Erro ao carregar histórico:', error);
    }
}

async function checkAuthentication() {
    if (authToken) {
        try {
            const response = await makeAuthenticatedRequest('/api/auth/me');
            if (response.ok) {
                const data = await response.json();
                currentUser = data.user;
                
                // ✅ ATUALIZAR UI IMEDIATAMENTE
                updateAuthUI();
                updateUIForLoggedInUser(currentUser);
                
                showToast('Sessão restaurada!', 'success');
            } else {
                // Token inválido, limpar
                localStorage.removeItem('authToken');
                authToken = null;
                currentUser = null;
                updateAuthUI(); // ✅ Atualizar UI também quando desloga
            }
        } catch (error) {
            console.error('Erro ao verificar autenticação:', error);
            localStorage.removeItem('authToken');
            authToken = null;
            currentUser = null;
            updateAuthUI(); // ✅ Atualizar UI em caso de erro
        }
    }
    updateAuthUI(); // ✅ Garantir que UI está atualizada
}

// ✅ FUNÇÕES DE RESET DE SENHA

async function forgotPassword() {
    const email = document.getElementById('forgot-email').value.trim();
    if (!email) {
        showToast('Por favor, digite seu email.', 'error');
        return;
    }

    const btn = document.querySelector('#forgot-password-modal button');
    const btnText = btn.querySelector('.btn-text');
    const btnLoading = btn.querySelector('.btn-loading');

    btnText.style.display = 'none';
    btnLoading.style.display = 'inline';
    btn.disabled = true;

    try {
        const response = await fetch('/api/auth/forgot-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });

        const data = await response.json();

        if (response.ok) {
            showToast(data.message, 'success');
            document.getElementById('forgot-password-modal').style.display = 'none';
        } else {
            showToast(data.error || 'Erro ao solicitar reset de senha.', 'error');
        }
    } catch (error) {
        console.error('Forgot password error:', error);
        showToast('Erro de conexão. Tente novamente.', 'error');
    } finally {
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
        btn.disabled = false;
    }
}

async function resetPassword() {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');

    const newPassword = document.getElementById('reset-password').value;
    const confirmPassword = document.getElementById('reset-confirm-password').value;

    if (!newPassword || !confirmPassword) {
        showToast('Por favor, preencha as senhas.', 'error');
        return;
    }

    if (newPassword !== confirmPassword) {
        document.getElementById('reset-password-error').style.display = 'block';
        showToast('As senhas não coincidem!', 'error');
        return;
    } else {
        document.getElementById('reset-password-error').style.display = 'none';
    }

    try {
        const response = await fetch('/api/auth/reset-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token, password: newPassword })
        });

        const data = await response.json();

        if (response.ok) {
            showToast('Senha redefinida com sucesso! Você foi logado.', 'success');
            document.getElementById('reset-password-modal').style.display = 'none';

            // Logar o usuário automaticamente
            authToken = data.access_token;
            currentUser = data.user;
            localStorage.setItem('authToken', authToken);
            updateAuthUI();

            // Limpar o token da URL
            window.history.replaceState({}, document.title, window.location.pathname);
        } else {
            showToast(data.error || 'Token inválido ou expirado.', 'error');
        }
    } catch (error) {
        console.error('Reset password error:', error);
        showToast('Erro ao redefinir a senha.', 'error');
    }
}


// ======================
// FUNÇÕES PRINCIPAIS
// ======================

function setupTabs() {
    const navLinks = document.querySelectorAll('.nav-link');
    const tabContents = document.querySelectorAll('.tab-content');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            tabContents.forEach(content => content.classList.remove('active'));
            
            const targetTab = link.getAttribute('href').substring(1);
            document.getElementById(targetTab).classList.add('active');
            
            currentTab = targetTab;
        });
    });
}

function setupEventListeners() {
    // Função segura para adicionar event listeners
    function safeAddListener(id, event, callback) {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener(event, callback);
        } else {
            console.warn(`Elemento ${id} não encontrado para event listener`);
        }
    }

    // Botões de geração
    safeAddListener('generate-ideas-btn', 'click', generateIdeas);
    safeAddListener('generate-script-btn', 'click', generateScript);
    
    // Botões de ação
    safeAddListener('export-ideas', 'click', exportIdeas);
    safeAddListener('clear-ideas', 'click', clearIdeas);
    safeAddListener('copy-script', 'click', copyScript);
    safeAddListener('save-script', 'click', saveScript);
    
    // Botões de autenticação
    safeAddListener('login-btn', 'click', () => {
        const modal = document.getElementById('login-modal');
        if (modal) modal.style.display = 'block';
    });
    
    safeAddListener('register-btn', 'click', () => {
        const modal = document.getElementById('register-modal');
        if (modal) modal.style.display = 'block';
    });
    
    safeAddListener('logout-btn', 'click', logout);
    safeAddListener('login-submit', 'click', login);

    // ✅ ADICIONAR EVENT LISTENER PARA O LINK "ESQUECI MINHA SENHA"
    safeAddListener('forgot-password-link', 'click', (e) => {
        e.preventDefault();
        showForgotPasswordModal();
    });
    safeAddListener('register-submit', 'click', register);
    
    // Fechar modais
    document.querySelectorAll('.modal .close').forEach(closeBtn => {
        closeBtn.addEventListener('click', () => {
            const modal = closeBtn.closest('.modal');
            if (modal) modal.style.display = 'none';
        });
    });
}

// ✅ FUNÇÕES PARA CONTROLAR MODAIS

function showForgotPasswordModal() {
    document.getElementById('login-modal').style.display = 'none';
    document.getElementById('forgot-password-modal').style.display = 'block';
}

function showLoginModal() {
    document.getElementById('forgot-password-modal').style.display = 'none';
    document.getElementById('login-modal').style.display = 'block';
}

function handleResetPasswordToken() {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    if (token) {
        document.getElementById('reset-password-modal').style.display = 'block';
    }
}

// ✅ FUNÇÃO PARA VISUALIZAR SENHA
function togglePasswordVisibility(passwordFieldId, eyeIconId) {
    const passwordField = document.getElementById(passwordFieldId);
    const eyeIcon = document.getElementById(eyeIconId);
    
    if (passwordField.type === 'password') {
        passwordField.type = 'text';
        if (eyeIcon) eyeIcon.textContent = '🔒';
    } else {
        passwordField.type = 'password';
        if (eyeIcon) eyeIcon.textContent = '👁️';
    }
}

// ✅ FUNÇÃO PARA VALIDAR CONFIRMAÇÃO DE SENHA
function validatePasswordConfirmation() {
    const password = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('register-confirm-password').value;
    const errorElement = document.getElementById('password-error');
    
    if (password !== confirmPassword) {
        errorElement.style.display = 'block';
        return false;
    } else {
        errorElement.style.display = 'none';
        return true;
    }
}

// ✅ LOGIN COM ENTER
function setupEnterKeyLogin() {
    document.getElementById('login-password').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            login();
        }
    });
}

// ✅ REGISTRO COM ENTER  
function setupEnterKeyRegister() {
    document.getElementById('register-confirm-password').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            register();
        }
    });
}

// ✅ ATUALIZAR FUNÇÃO REGISTER PARA VALIDAR SENHA
async function register() {
    const email = document.getElementById('register-email').value.trim();
    const password = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('register-confirm-password').value;
    const name = document.getElementById('register-name').value.trim();
    
    if (!email || !password || !name) {
        showToast('Preencha todos os campos', 'error');
        return;
    }
    
    // ✅ VALIDAR CONFIRMAÇÃO DE SENHA
    if (password !== confirmPassword) {
        document.getElementById('password-error').style.display = 'block';
        showToast('As senhas não coincidem!', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, name })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.access_token;
            currentUser = data.user;
            localStorage.setItem('authToken', authToken);
            
            updateAuthUI();
            updateUIForLoggedInUser(currentUser);
            
            showToast('Conta criada com sucesso!', 'success');
            document.getElementById('register-modal').style.display = 'none';
            
        } else {
            showToast(data.error, 'error');
        }
        
    } catch (error) {
        showToast('Erro ao criar conta', 'error');
    }
}

// ======================
// FUNÇÕES DA API
// ======================

async function generateIdeas() {
    const niche = document.getElementById('niche').value.trim();
    const audience = document.getElementById('audience').value.trim();
    const count = document.getElementById('count').value;
    
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
        const response = await makeAuthenticatedRequest('/api/generate-ideas', {
            method: 'POST',
            body: JSON.stringify({ niche, audience, count: parseInt(count) })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayIdeas(data.ideas);
            saveToHistory('ideas', { niche, audience, ideas: data.ideas });
            showToast(`${data.ideas.length} ideias geradas com sucesso!`, 'success');
            trackEvent('generation', 'ideas_generated', `niche:${niche}, count:${data.ideas.length}`);
        } else {
            if (data.requires_auth) {
                // Mostrar modal de login se necessário autenticação
                document.getElementById('login-modal').style.display = 'block';
                showToast('Faça login para continuar usando', 'info');
            } else {
                throw new Error(data.error || 'Erro ao gerar ideias');
            }
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
        const response = await makeAuthenticatedRequest('/api/generate-script', {
            method: 'POST',
            body: JSON.stringify({ idea })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayScript(data.script);
            saveToHistory('script', { idea, script: data.script });
            showToast('Roteiro gerado com sucesso!', 'success');
            trackEvent('generation', 'script_generated', `idea:${idea.substring(0,50)}`);
        } else {
            if (data.requires_auth) {
                document.getElementById('login-modal').style.display = 'block';
                showToast('Faça login para continuar usando', 'info');
            } else {
                throw new Error(data.error || 'Erro ao gerar roteiro');
            }
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

// ... (o restante das funções permanecem iguais: displayIdeas, displayScript, useIdeaForScript, etc.)

// ======================
// FUNÇÕES DE TRACKING
// ======================

function trackEvent(category, action, label = '', value = null) {
    if (typeof gtag !== 'undefined') {
        const eventParams = {
            'event_category': category,
            'event_label': label
        };
        
        if (value !== null) {
            eventParams['value'] = value;
        }
        
        gtag('event', action, eventParams);
        console.log('📊 Event tracked:', category, action, label);
    }
}

function setupButtonTracking() {
    // Botões de geração
    document.getElementById('generate-ideas-btn').addEventListener('click', () => {
        trackEvent('ui', 'button_click', 'generate_ideas_button');
    });
    
    document.getElementById('generate-script-btn').addEventListener('click', () => {
        trackEvent('ui', 'button_click', 'generate_script_button');
    });
    
    // Botões de autenticação
    document.getElementById('login-btn').addEventListener('click', () => {
        trackEvent('auth', 'login_attempt', 'login_button');
    });
    
    document.getElementById('register-btn').addEventListener('click', () => {
        trackEvent('auth', 'register_attempt', 'register_button');
    });
}

function setupErrorTracking() {
    window.addEventListener('error', (e) => {
        trackEvent('error', 'global_error', e.message);
    });
    
    window.addEventListener('unhandledrejection', (e) => {
        trackEvent('error', 'promise_error', e.reason.message || e.reason);
    });
}

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
        }
    ];
    
    return ideas.slice(0, count);
}

function getFallbackScript(idea) {
    return `📝 ROTEIRO PARA: ${idea}\n\n⏰ DURAÇÃO: 20-25s\n🎯 PÚBLICO: Geral\n\n💡 IDEIA: ${idea}\n\n🏷️ HASHTAGS: #${idea.replace(/\s+/g, '')} #viral #conteudo`;
}

// ======================
// FUNÇÕES TEMPORÁRIAS
// ======================

// Adicione esta função de debug temporariamente
async function debugLogin() {
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;
    
    const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
    
    console.log('Status:', response.status);
    console.log('Headers:', Object.fromEntries([...response.headers]));
    
    const text = await response.text();
    console.log('Raw response:', text);
    
    try {
        const data = JSON.parse(text);
        console.log('Parsed JSON:', data);
    } catch (e) {
        console.log('Not JSON:', text);
    }
}

// ======================
// FUNÇÕES GLOBAIS
// ======================

window.useIdeaForScript = useIdeaForScript;
window.login = login;
window.register = register;
window.logout = logout;
window.exportIdeas = exportIdeas;
window.forgotPassword = forgotPassword;
window.resetPassword = resetPassword;
window.clearIdeas = clearIdeas;
window.copyScript = copyScript;
window.saveScript = saveScript;