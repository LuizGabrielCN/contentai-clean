// Configurações da API
const API_BASE_URL = '';
let authToken = localStorage.getItem('authToken');
let currentAdmin = null;

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    initializeAdminDashboard();
});

async function initializeAdminDashboard() {
    // Verificar autenticação e permissões
    if (!await checkAdminPermissions()) {
        window.location.href = '/';
        return;
    }

    // Configurar navegação
    setupAdminTabs();
    
    // Carregar dados iniciais
    loadDashboardData();
    loadUsers();

    // Esconder loading
    setTimeout(() => {
        document.getElementById('loading').style.display = 'none';
    }, 1000);
}

async function checkAdminPermissions() {
    if (!authToken) {
        showToast('Acesso não autorizado', 'error');
        return false;
    }

    try {
        const response = await fetch('/api/auth/me', {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const user = await response.json();
            currentAdmin = user.user;
            
            // Verificar se é admin
            const adminResponse = await fetch('/admin/users', {
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    'Content-Type': 'application/json'
                }
            });

            if (adminResponse.status === 200) {
                document.getElementById('admin-email').textContent = currentAdmin.email;
                return true;
            }
        }
    } catch (error) {
        console.error('Erro ao verificar permissões:', error);
    }

    showToast('Acesso admin requerido', 'error');
    return false;
}

function setupAdminTabs() {
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
        });
    });
}

async function loadDashboardData() {
    try {
        // Carregar estatísticas
        const [statsResponse, healthResponse] = await Promise.all([
            fetch('/api/statistics', {
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    'Content-Type': 'application/json'
                }
            }),
            fetch('/api/health', {
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    'Content-Type': 'application/json'
                }
            })
        ]);

        if (statsResponse.ok && healthResponse.ok) {
            const stats = await statsResponse.json();
            const health = await healthResponse.json();

            // Atualizar cards de estatísticas
            document.getElementById('total-users').textContent = stats.users.total;
            document.getElementById('premium-users').textContent = stats.users.premium;
            document.getElementById('total-ideas').textContent = stats.statistics.total_ideas_generated;
            document.getElementById('total-scripts').textContent = stats.statistics.total_scripts_generated;

            // Criar gráficos
            createUsersChart(stats.users);
            createPlansChart(stats.users);
        }
    } catch (error) {
        console.error('Erro ao carregar dashboard:', error);
        showToast('Erro ao carregar dados', 'error');
    }
}

async function loadUsers() {
    try {
        const response = await fetch('/admin/users', {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.json();
            renderUsersTable(data.users);
        }
    } catch (error) {
        console.error('Erro ao carregar usuários:', error);
        showToast('Erro ao carregar usuários', 'error');
    }
}

function renderUsersTable(users) {
    const tbody = document.getElementById('users-table-body');
    tbody.innerHTML = '';

    users.forEach(user => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>${user.id}</td>
            <td>${user.email}</td>
            <td>${user.name || 'N/A'}</td>
            <td>
                <span class="status-badge ${user.is_premium ? 'premium' : 'free'}">
                    ${user.is_premium ? 'Premium' : 'Free'}
                </span>
            </td>
            <td>
                <span class="status-badge ${user.is_admin ? 'admin' : 'user'}">
                    ${user.is_admin ? 'Admin' : 'User'}
                </span>
            </td>
            <td>${new Date(user.created_at).toLocaleDateString('pt-BR')}</td>
            <td>
                <button onclick="editUser(${user.id})" class="btn-sm btn-outline">Editar</button>
                <button onclick="toggleUserPremium(${user.id}, ${!user.is_premium})" 
                        class="btn-sm ${user.is_premium ? 'btn-warning' : 'btn-success'}">
                    ${user.is_premium ? 'Remover Premium' : 'Tornar Premium'}
                </button>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

function createUsersChart(usersData) {
    const ctx = document.getElementById('users-chart').getContext('2d');
    // Implementar gráfico de crescimento de usuários
}

function createPlansChart(usersData) {
    const ctx = document.getElementById('plans-chart').getContext('2d');
    // Implementar gráfico de distribuição de planos
}

function logout() {
    authToken = null;
    currentAdmin = null;
    localStorage.removeItem('authToken');
    window.location.href = '/';
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    
    setTimeout(() => {
        toast.className = 'toast';
    }, 3000);
}

// Funções para implementar posteriormente
function editUser(userId) {
    showToast('Funcionalidade em desenvolvimento', 'info');
}

async function toggleUserPremium(userId, makePremium) {
    try {
        const response = await fetch(`/admin/user/${userId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                is_premium: makePremium
            })
        });

        if (response.ok) {
            showToast(`Usuário ${makePremium ? 'tornado premium' : 'removido do premium'}`, 'success');
            loadUsers();
            loadDashboardData();
        }
    } catch (error) {
        showToast('Erro ao atualizar usuário', 'error');
    }
}