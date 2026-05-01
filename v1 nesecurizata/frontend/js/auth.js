function saveToken(token) { localStorage.setItem('authToken', token); }
function getToken() { return localStorage.getItem('authToken'); }
function removeToken() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userInfo');
}

function isLoggedIn() {
    const token = getToken();
    if (!token) return false;
    try {
        const payload = parseJwt(token);
        return payload.exp > (Date.now() / 1000);
    } catch {
        return false;
    }
}

function parseJwt(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    } catch {
        return null;
    }
}

function getTokenExpiration(token) {
    const payload = parseJwt(token);
    return payload && payload.exp ? new Date(payload.exp * 1000) : null;
}

function getTokenIssuedAt(token) {
    const payload = parseJwt(token);
    return payload && payload.iat ? new Date(payload.iat * 1000) : null;
}

function getTokenTTL(token) {
    const exp = getTokenExpiration(token);
    if (!exp) return null;
    
    const diff = exp - new Date();
    if (diff < 0) return 'Expired';
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 24) return `${Math.floor(hours / 24)}d ${hours % 24}h`;
    return hours > 0 ? `${hours}h ${minutes}m` : `${minutes}m`;
}

function saveUserInfo(userInfo) { localStorage.setItem('userInfo', JSON.stringify(userInfo)); }
function getUserInfo() {
    const info = localStorage.getItem('userInfo');
    return info ? JSON.parse(info) : null;
}

async function logout() {
    await logoutApi();
    removeToken();
    window.location.href = 'index.html';
}

if (typeof window !== 'undefined' && isLoggedIn()) {
    setInterval(() => {
        if (!isLoggedIn() && !window.location.pathname.includes('index.html') && !window.location.pathname.includes('register.html')) {
            logout();
        }
    }, 60000);
}