function initDashboard() {
    loadUserInfo();
    loadTickets();
    updateTokenInfo();
}

let ticketSearchTimer = null;

function loadUserInfo() {
    const userInfo = getUserInfo();
    if (userInfo) {
        document.getElementById('userEmail').textContent = userInfo.email;
        document.getElementById('profileEmail').textContent = userInfo.email;
        document.getElementById('profileId').textContent = userInfo.userId || '-';
        document.getElementById('profileRole').textContent = userInfo.role || '-';

        if (userInfo.role === 'MANAGER' || userInfo.role === 'ADMIN') {
            document.getElementById('menuAudit').style.display = 'block';
        }
    }
}

function switchView(viewName) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.querySelectorAll('.menu-item').forEach(i => i.classList.remove('active'));
    
    document.getElementById(`${viewName}View`).classList.add('active');
    document.querySelector(`[data-view="${viewName}"]`).classList.add('active');
    
    if (viewName === 'tickets') loadTickets();
    if (viewName === 'security') updateTokenInfo();
    if (viewName === 'audit') loadAuditLogs();
}

async function loadTickets() {
    const ticketsList = document.getElementById('ticketsList');
    ticketsList.innerHTML = '<div class="loading">Loading records...</div>';
    
    try {
        const tickets = await getTickets();
        if (tickets.length === 0) {
            ticketsList.innerHTML = '<div class="loading">No active records found.</div>';
            return;
        }
        
        ticketsList.innerHTML = tickets.map(ticket => `
            <div class="ticket-card" data-id="${ticket.id}">
                <div class="ticket-header">
                    <div class="ticket-title">${escapeHtml(ticket.title)}</div>
                    <span class="ticket-severity severity-${ticket.severity.toLowerCase()}">${ticket.severity}</span>
                </div>
                <div class="ticket-description">${escapeHtml(ticket.description)}</div>
                <div class="ticket-meta">
                    <small>Status: ${ticket.status} | ID: ${ticket.id}</small>
                </div>
                <div class="ticket-footer">
                    <button class="btn btn-sm btn-secondary" onclick="confirmDeleteTicket(${ticket.id})">Delete</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        ticketsList.innerHTML = `<div class="error-message">Sync failed: ${error.message}</div>`;
    }
}

async function searchTickets() {
    const query = document.getElementById('ticketSearch')?.value.trim() || '';
    if (!query) {
        loadTickets();
        return;
    }

    const ticketsList = document.getElementById('ticketsList');
    ticketsList.innerHTML = '<div class="loading">Searching records...</div>';

    try {
        const tickets = await searchTicketsApi(query);
        if (tickets.length === 0) {
            ticketsList.innerHTML = `<div class="loading">No records found for "${escapeHtml(query)}".</div>`;
            return;
        }

        ticketsList.innerHTML = tickets.map(ticket => `
            <div class="ticket-card" data-id="${ticket.id}">
                <div class="ticket-header">
                    <div class="ticket-title">${escapeHtml(ticket.title)}</div>
                    <span class="ticket-severity severity-${ticket.severity.toLowerCase()}">${ticket.severity}</span>
                </div>
                <div class="ticket-description">${escapeHtml(ticket.description)}</div>
                <div class="ticket-meta">
                    <small>Status: ${ticket.status} | ID: ${ticket.id}</small>
                </div>
                <div class="ticket-footer">
                    <button class="btn btn-sm btn-secondary" onclick="confirmDeleteTicket(${ticket.id})">Delete</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        ticketsList.innerHTML = `<div class="error-message">Search failed: ${error.message}</div>`;
    }
}

function searchTicketsDebounced() {
    clearTimeout(ticketSearchTimer);
    ticketSearchTimer = setTimeout(searchTickets, 250);
}

function clearTicketSearch() {
    const searchInput = document.getElementById('ticketSearch');
    if (searchInput) searchInput.value = '';
    loadTickets();
}

async function loadAuditLogs() {
    const tbody = document.getElementById('auditTableBody');
    tbody.innerHTML = '<tr><td colspan="5" class="loading">Loading logs...</td></tr>';
    
    try {
        const logs = await getAuditLogs();
        tbody.innerHTML = logs.map(log => `
            <tr style="border-bottom: 1px solid var(--border-color); font-size: 0.9em;">
                <td style="padding: 10px; color: var(--text-muted);">${new Date(log.timestamp).toLocaleString()}</td>
                <td style="padding: 10px;">${escapeHtml(log.userEmail)}</td>
                <td style="padding: 10px; font-weight: bold;">${escapeHtml(log.action)}</td>
                <td style="padding: 10px;">
                    <span style="color: ${log.success ? 'var(--success-color)' : 'var(--danger-color)'};">
                        ${log.success ? 'SUCCESS' : 'FAILED'}
                    </span>
                </td>
                <td style="padding: 10px; color: var(--text-muted);">${escapeHtml(log.details)}</td>
            </tr>
        `).join('');
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="5" style="color: var(--danger-color); padding: 10px;">Access Denied or Error: ${error.message}</td></tr>`;
    }
}

function showCreateTicket() {
    document.getElementById('createTicketForm').style.display = 'block';
    document.getElementById('ticketTitle').focus();
}

function hideCreateTicket() {
    document.getElementById('createTicketForm').style.display = 'none';
    document.getElementById('ticketTitle').value = '';
    document.getElementById('ticketDescription').value = '';
    document.getElementById('ticketSeverity').value = 'LOW';
}

async function createTicket(event) {
    event.preventDefault();
    const title = document.getElementById('ticketTitle').value;
    const description = document.getElementById('ticketDescription').value;
    const severity = document.getElementById('ticketSeverity').value;
    
    try {
        await createTicketApi(title, description, severity);
        showToast('Record created successfully', 'success');
        hideCreateTicket();
        clearTicketSearch();
    } catch (error) {
        showToast(`Failed to create record: ${error.message}`, 'error');
    }
}

async function confirmDeleteTicket(id) {
    if (!confirm('Permanently delete this record?')) return;
    try {
        await deleteTicket(id);
        showToast('Record removed', 'success');
        loadTickets();
    } catch (error) {
        showToast(`Deletion failed: ${error.message}`, 'error');
    }
}

function updateTokenInfo() {
    const token = getToken();
    if (!token) return;
    try {
        document.getElementById('tokenPreview').textContent = token.substring(0, 40) + '...';
        document.getElementById('tokenIat').textContent = getTokenIssuedAt(token)?.toLocaleString() || '-';
        document.getElementById('tokenExp').textContent = getTokenExpiration(token)?.toLocaleString() || '-';
        document.getElementById('tokenTtl').textContent = getTokenTTL(token) || '-';
    } catch {}
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

setInterval(() => {
    if (document.getElementById('securityView')?.classList.contains('active')) {
        updateTokenInfo();
    }
}, 5000);
