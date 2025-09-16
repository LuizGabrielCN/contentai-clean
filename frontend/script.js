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

    // Configurar navegação por tabs
    setupTabs();
    
    // Configurar event listeners
    setupEventListeners();
    
    // Configurar tracking
    setupButtonTracking();
    setupErrorTracking();
    
    // Carregar histórico do localStorage
    loadHistory();
    
    // Verificar autenticação
    checkAuthentication();
    
    // Trackear página carregada
    trackEvent('page', 'page_view', 'homepage');
    
    console.log('✅ HelpubliAI initialized with analytics');
}

// ======================
// SISTEMA DE AUTENTICAÇÃO
// ======================

async function checkAuthentication() {
    if (authToken) {
        try {
            const response = await makeAuthenticatedRequest('/api/auth/me');
            if (response.ok) {
                const data = await response.json();
                currentUser = data.user;
                updateUIForLoggedInUser(currentUser);
                showToast('Sessão restaurada!', 'success');
            } else {
                // Token inválido, limpar
                localStorage.removeItem('authToken');
                authToken = null;
            }
        } catch (error) {
            console.error('Erro ao verificar autenticação:', error);
        }
    }
    updateAuthUI();
}

function updateAuthUI() {
    const authSection = document.getElementById('auth-section');
    const userSection = document.getElementById('user-section');
    const userEmail = document.getElementById('user-email');
    const userPlan = document.getElementById('user-plan');
    
    if (currentUser) {
        authSection.style.display = 'none';
        userSection.style.display = 'block';
        userEmail.textContent = currentUser.email;
        userPlan.textContent = currentUser.is_premium ? 'Premium' : 'Free';
        userPlan.className = currentUser.is_premium ? 'premium-badge' : 'free-badge';
    } else {
        authSection.style.display = 'block';
        userSection.style.display = 'none';
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
        
        if (response.ok) {
            authToken = data.access_token;
            currentUser = data.user;
            localStorage.setItem('authToken', authToken);
            updateUIForLoggedInUser(currentUser);
            showToast('Login realizado com sucesso!', 'success');
            
            // Fechar modal de login
            document.getElementById('login-modal').style.display = 'none';
        } else {
            showToast(data.error, 'error');
        }
    } catch (error) {
        showToast('Erro ao fazer login', 'error');
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
    updateAuthUI();
    showToast('Logout realizado', 'success');
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
    // Atualizar UI com informações do usuário
    const userInfoElement = document.getElementById('user-info');
    if (userInfoElement) {
        userInfoElement.innerHTML = `
            <span>${user.email}</span>
            <span class="plan-badge ${user.is_premium ? 'premium' : 'free'}">
                ${user.is_premium ? 'Premium' : 'Free'}
            </span>
        `;
    }
    
    // Mostrar/ocultar elementos baseado no plano
    const premiumElements = document.querySelectorAll('.premium-only');
    premiumElements.forEach(el => {
        el.style.display = user.is_premium ? 'block' : 'none';
    });
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
    // Botões de geração
    document.getElementById('generate-ideas-btn').addEventListener('click', generateIdeas);
    document.getElementById('generate-script-btn').addEventListener('click', generateScript);
    
    // Botões de ação
    document.getElementById('export-ideas').addEventListener('click', exportIdeas);
    document.getElementById('clear-ideas').addEventListener('click', clearIdeas);
    document.getElementById('copy-script').addEventListener('click', copyScript);
    document.getElementById('save-script').addEventListener('click', saveScript);
    
    // Botões de autenticação
    document.getElementById('login-btn').addEventListener('click', () => {
        document.getElementById('login-modal').style.display = 'block';
    });
    
    document.getElementById('register-btn').addEventListener('click', () => {
        document.getElementById('register-modal').style.display = 'block';
    });
    
    document.getElementById('logout-btn').addEventListener('click', logout);
    
    document.getElementById('login-submit').addEventListener('click', login);
    document.getElementById('register-submit').addEventListener('click', register);
    
    // Fechar modais
    document.querySelectorAll('.modal .close').forEach(closeBtn => {
        closeBtn.addEventListener('click', () => {
            closeBtn.closest('.modal').style.display = 'none';
        });
    });
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

// ======================
// FUNÇÕES GLOBAIS
// ======================

window.useIdeaForScript = useIdeaForScript;
window.login = login;
window.register = register;
window.logout = logout;