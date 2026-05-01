const API_HOST = window.location.hostname === '127.0.0.1' ? '127.0.0.1' : 'localhost';
const API_BASE_URL = `http://${API_HOST}:8080/api`;

async function register(email, password, role = 'ANALYST') {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, role })
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Registration failed');
    }
    return await response.json();
}

async function login(email, password) {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Login failed');
    }
    return await response.json();
}

async function forgotPassword(email) {
    const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Password reset request failed');
    }
    return await response.json();
}

async function resetPassword(token, newPassword) {
    const response = await fetch(`${API_BASE_URL}/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, newPassword })
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Password reset failed');
    }
    return await response.json();
}

async function logoutApi() {
    const token = getToken();
    if (!token) return;
    try {
        await fetch(`${API_BASE_URL}/auth/logout`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
    } catch (error) {
        console.error('Logout failed:', error);
    }
}

async function getTickets() {
    const response = await fetch(`${API_BASE_URL}/tickets`, {
        headers: { 'Authorization': `Bearer ${getToken()}` }
    });
    if (!response.ok) throw new Error('Failed to fetch tickets');
    return await response.json();
}

async function searchTicketsApi(query) {
    const response = await fetch(`${API_BASE_URL}/tickets/search?q=${encodeURIComponent(query)}`, {
        headers: { 'Authorization': `Bearer ${getToken()}` }
    });
    if (!response.ok) throw new Error('Failed to search tickets');
    return await response.json();
}

async function getTicket(id) {
    const response = await fetch(`${API_BASE_URL}/tickets/${id}`, {
        headers: { 'Authorization': `Bearer ${getToken()}` }
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to fetch ticket');
    }
    return await response.json();
}

async function createTicketApi(title, description, severity) {
    const response = await fetch(`${API_BASE_URL}/tickets`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify({ title, description, severity })
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to create ticket');
    }
    return await response.json();
}

async function updateTicket(id, updates) {
    const response = await fetch(`${API_BASE_URL}/tickets/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify(updates)
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to update ticket');
    }
    return await response.json();
}

async function deleteTicket(id) {
    const response = await fetch(`${API_BASE_URL}/tickets/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${getToken()}` }
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to delete ticket');
    }
    return null;
}

async function getAuditLogs() {
    const response = await fetch(`${API_BASE_URL}/audit`, {
        headers: { 'Authorization': `Bearer ${getToken()}` }
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to fetch audit logs');
    }
    return await response.json();
}

function getToken() {
    return localStorage.getItem('authToken');
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    setTimeout(() => toast.classList.remove('show'), 3000);
}
