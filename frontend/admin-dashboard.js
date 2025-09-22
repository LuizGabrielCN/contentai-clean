// Variáveis globais
let allUsers = [];
let currentFilters = {};
let realTimeData = {
    onlineUsers: 0,
    generationsPerMinute: 0,
    activeSessions: 0
};

// Função para fazer requisições autenticadas
async function makeAuthenticatedRequest(url, options = {}) {
    const token = localStorage.getItem('authToken');
    if (!token) {
        window.location.href = '/'; // Redirecionar para login se não autenticado
        return;
    }

    const defaultOptions = {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    };

    const response = await fetch(url, { ...defaultOptions, ...options });

    // Redirect to login if unauthorized or forbidden
    if (response.status === 401 || response.status === 403) {
        localStorage.removeItem('authToken');
        window.location.href = '/';
        return;
    }

    return response;
}

// Carregar dados do dashboard
async function loadDashboardData() {
    try {
        const response = await makeAuthenticatedRequest('/api/admin/dashboard');
        if (response.ok) {
            const data = await response.json();
            const dashboard = data.dashboard;

            // Atualizar estatísticas
            document.getElementById('total-users').textContent = dashboard.users.total;
            document.getElementById('total-ideas').textContent = dashboard.content.ideas_generated;
            document.getElementById('total-scripts').textContent = dashboard.content.scripts_generated;
            document.getElementById('premium-users').textContent = dashboard.users.premium;

            // Calcular tendências (simples, baseado em dados atuais)
            // Aqui você pode implementar lógica para calcular tendências reais
            document.getElementById('users-trend').textContent = '+5%';
            document.getElementById('ideas-trend').textContent = '+12%';
            document.getElementById('scripts-trend').textContent = '+8%';
            document.getElementById('premium-trend').textContent = '+15%';

            // Atualizar email do admin
            const userResponse = await makeAuthenticatedRequest('/api/auth/me');
            if (userResponse.ok) {
                const userData = await userResponse.json();
                document.getElementById('admin-email').textContent = userData.user.email;
            }
        }
    } catch (error) {
        console.error('Erro ao carregar dados do dashboard:', error);
    }
}

// Novas funções de gestão
async function loadFullDashboard() {
    try {
        await loadDashboardData();
        await loadUsers();
        await loadRealTimeStats();
        startRealTimeUpdates();

        // Esconder tela de carregamento
        document.getElementById('loading').style.display = 'none';
    } catch (error) {
        console.error('Erro ao carregar dashboard:', error);
        document.getElementById('loading').style.display = 'none';
        showToast('Erro ao carregar dashboard', 'error');
    }
}

async function loadRealTimeStats() {
    try {
        const response = await makeAuthenticatedRequest('/admin/real-time-stats');
        if (response.ok) {
            realTimeData = await response.json();
            updateRealTimeUI();
        }
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
    }
}

function updateRealTimeUI() {
    document.getElementById('online-users').textContent = realTimeData.onlineUsers;
    document.getElementById('generations-minute').textContent = realTimeData.generationsPerMinute;
}

function startRealTimeUpdates() {
    // Atualizar a cada 30 segundos
    setInterval(loadRealTimeStats, 30000);
    
    // WebSocket para atualizações em tempo real
    setupWebSocketConnection();
}

function setupWebSocketConnection() {
    // Implementar WebSocket para updates em tempo real
    // A biblioteca do Socket.IO lida com o protocolo (ws/wss) automaticamente
    const socket = io({
        transports: ['websocket'] // Forçar o uso de WebSockets
    });
    
    socket.on('connect', () => {
        console.log('✅ Conectado ao WebSocket');
        const token = localStorage.getItem('authToken');
        if (token) {
            socket.emit('join_admin', { token: token });
        }
    });

    socket.on('stats_update', (data) => {
        handleRealTimeUpdate(data);
    });
}

function handleRealTimeUpdate(data) {
    switch (data.type) {
        case 'user_online':
            realTimeData.onlineUsers = data.count;
            break;
        case 'generation_created':
            realTimeData.generationsPerMinute = data.rate;
            break;
        case 'new_user':
            addUserToTable(data.user);
            break;
    }
    updateRealTimeUI();
}

// Gestão de Usuários Avançada
function filterUsers() {
    const searchTerm = document.getElementById('user-search').value.toLowerCase();
    const filterType = document.getElementById('user-filter').value;
    
    let filtered = allUsers;
    
    // Aplicar filtro de tipo
    if (filterType === 'premium') {
        filtered = filtered.filter(u => u.is_premium);
    } else if (filterType === 'free') {
        filtered = filtered.filter(u => !u.is_premium);
    } else if (filterType === 'admin') {
        filtered = filtered.filter(u => u.is_admin);
    }
    
    // Aplicar busca
    if (searchTerm) {
        filtered = filtered.filter(u => 
            u.email.toLowerCase().includes(searchTerm) ||
            (u.name && u.name.toLowerCase().includes(searchTerm))
        );
    }
    
    renderUsersTable(filtered);
}

async function editUser(userId) {
    try {
        const response = await makeAuthenticatedRequest(`/admin/user/${userId}`);
        if (response.ok) {
            const user = await response.json();
            showEditUserModal(user);
        }
    } catch (error) {
        showToast('Erro ao carregar usuário', 'error');
    }
}

function showEditUserModal(user) {
    const modal = document.getElementById('user-edit-modal');
    const formDiv = document.getElementById('user-edit-form');
    
    formDiv.innerHTML = `
        <form onsubmit="updateUser(${user.id}); return false;">
            <div class="form-group">
                <label>Email:</label>
                <input type="email" value="${user.email}" disabled>
            </div>
            <div class="form-group">
                <label>Nome:</label>
                <input type="text" value="${user.name || ''}" id="edit-user-name">
            </div>
            <div class="form-group">
                <label>
                    <input type="checkbox" ${user.is_premium ? 'checked' : ''} id="edit-user-premium">
                    Usuário Premium
                </label>
            </div>
            <div class="form-group">
                <label>
                    <input type="checkbox" ${user.is_admin ? 'checked' : ''} id="edit-user-admin">
                    Administrador
                </label>
            </div>
            <button type="submit" class="btn btn-primary">Salvar</button>
        </form>
    `;
    
    modal.style.display = 'block';
}

async function updateUser(userId) {
    const formData = {
        name: document.getElementById('edit-user-name').value,
        is_premium: document.getElementById('edit-user-premium').checked,
        is_admin: document.getElementById('edit-user-admin').checked
    };
    
    try {
        const response = await makeAuthenticatedRequest(`/admin/user/${userId}`, {
            method: 'PUT',
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            showToast('Usuário atualizado com sucesso!', 'success');
            document.getElementById('user-edit-modal').style.display = 'none';
            loadUsers();
        }
    } catch (error) {
        showToast('Erro ao atualizar usuário', 'error');
    }
}

// Ações em Massa
function applyBulkAction() {
    const action = document.getElementById('bulk-action').value;
    const selectedUsers = getSelectedUsers();
    
    if (!action || selectedUsers.length === 0) {
        showToast('Selecione uma ação e usuários', 'warning');
        return;
    }
    
    const actions = {
        'make_premium': { is_premium: true },
        'remove_premium': { is_premium: false },
        'make_admin': { is_admin: true },
        'remove_admin': { is_admin: false }
    };
    
    selectedUsers.forEach(userId => {
        applyUserAction(userId, actions[action]);
    });
}

function getSelectedUsers() {
    const checkboxes = document.querySelectorAll('.user-checkbox:checked');
    return Array.from(checkboxes).map(cb => parseInt(cb.dataset.userId));
}

async function applyUserAction(userId, data) {
    try {
        await makeAuthenticatedRequest(`/admin/user/${userId}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    } catch (error) {
        console.error(`Erro ao atualizar usuário ${userId}:`, error);
    }
}

// Novos endpoints no backend (routes.py)
async function loadUsers() {
    try {
        const response = await makeAuthenticatedRequest('/admin/users');
        if (response.ok) {
            const data = await response.json();
            allUsers = data.users;
            renderUsersTable(allUsers);
        }
    } catch (error) {
        console.error('Erro ao carregar usuários:', error);
    }
}

function renderUsersTable(users) {
    const tbody = document.getElementById('users-table-body');
    tbody.innerHTML = '';
    
    users.forEach(user => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td><input type="checkbox" class="user-checkbox" data-user-id="${user.id}"></td>
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
                <button onclick="confirmDeleteUser(${user.id}, '${user.email}')" class="btn-sm btn-danger">Excluir</button>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    loadFullDashboard();
});

// Função de logout
function logout() {
    localStorage.removeItem('authToken');
    window.location.href = '/';
}

// Função de confirmação de exclusão
function confirmDeleteUser(userId, userEmail) {
    if (confirm(`Tem certeza que deseja excluir o usuário ${userEmail}? Esta ação não pode ser desfeita.`)) {
        deleteUser(userId);
    }
}

// Função para excluir usuário
async function deleteUser(userId) {
    try {
        const response = await makeAuthenticatedRequest(`/admin/user/${userId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showToast('Usuário excluído com sucesso!', 'success');
            loadUsers(); // Recarregar lista de usuários
        } else {
            const error = await response.json();
            showToast(error.error || 'Erro ao excluir usuário', 'error');
        }
    } catch (error) {
        console.error('Erro ao excluir usuário:', error);
        showToast('Erro ao excluir usuário', 'error');
    }
}

// Função para renderizar gráficos com Chart.js
let usersChart = null;
let plansChart = null;

function renderCharts(dashboard) {
    // Dados para gráfico de crescimento de usuários (exemplo simples)
    const userGrowthData = {
        labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul'],
        datasets: [{
            label: 'Usuários',
            data: [10, 20, 30, 40, 50, 60, dashboard.users.total],
            borderColor: 'rgba(67, 97, 238, 1)',
            backgroundColor: 'rgba(67, 97, 238, 0.2)',
            fill: true,
            tension: 0.3
        }]
    };

    // Configuração do gráfico de crescimento de usuários
    const userGrowthConfig = {
        type: 'line',
        data: userGrowthData,
        options: {
            responsive: true,
            plugins: {
                legend: { display: true },
                tooltip: { enabled: true }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    };

    // Dados para gráfico de distribuição de planos
    const planDistributionData = {
        labels: ['Premium', 'Free'],
        datasets: [{
            label: 'Usuários',
            data: [dashboard.users.premium, dashboard.users.total - dashboard.users.premium],
            backgroundColor: [
                'rgba(76, 201, 240, 0.7)',
                'rgba(108, 117, 125, 0.7)'
            ],
            borderColor: [
                'rgba(76, 201, 240, 1)',
                'rgba(108, 117, 125, 1)'
            ],
            borderWidth: 1
        }]
    };

    // Configuração do gráfico de distribuição de planos
    const planDistributionConfig = {
        type: 'doughnut',
        data: planDistributionData,
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' },
                tooltip: { enabled: true }
            }
        }
    };

    // Renderizar ou atualizar gráfico de crescimento de usuários
    const usersCtx = document.getElementById('users-chart').getContext('2d');
    if (usersChart) {
        usersChart.data = userGrowthData;
        usersChart.update();
    } else {
        usersChart = new Chart(usersCtx, userGrowthConfig);
    }

    // Renderizar ou atualizar gráfico de distribuição de planos
    const plansCtx = document.getElementById('plans-chart').getContext('2d');
    if (plansChart) {
        plansChart.data = planDistributionData;
        plansChart.update();
    } else {
        plansChart = new Chart(plansCtx, planDistributionConfig);
    }
}

// Atualizar loadDashboardData para chamar renderCharts
async function loadDashboardData() {
    try {
        const response = await makeAuthenticatedRequest('/api/admin/dashboard');
        if (response.ok) {
            const data = await response.json();
            const dashboard = data.dashboard;

            // Atualizar estatísticas
            document.getElementById('total-users').textContent = dashboard.users.total;
            document.getElementById('total-ideas').textContent = dashboard.content.ideas_generated;
            document.getElementById('total-scripts').textContent = dashboard.content.scripts_generated;
            document.getElementById('premium-users').textContent = dashboard.users.premium;

            // Calcular tendências (simples, baseado em dados atuais)
            // Aqui você pode implementar lógica para calcular tendências reais
            document.getElementById('users-trend').textContent = '+5%';
            document.getElementById('ideas-trend').textContent = '+12%';
            document.getElementById('scripts-trend').textContent = '+8%';
            document.getElementById('premium-trend').textContent = '+15%';

            // Atualizar email do admin
            const userResponse = await makeAuthenticatedRequest('/api/auth/me');
            if (userResponse.ok) {
                const userData = await userResponse.json();
                document.getElementById('admin-email').textContent = userData.user.email;
            }

            // Renderizar gráficos
            renderCharts(dashboard);
        }
    } catch (error) {
        console.error('Erro ao carregar dados do dashboard:', error);
    }
}
