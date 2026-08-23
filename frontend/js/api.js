/* ==========================================================================
   API CLIENT & TOAST NOTIFICATION UTILITIES
   ========================================================================== */

const API_BASE_URL = '/api';

const API = {
    getToken() {
        return localStorage.getItem('inventory_token');
    },

    setToken(token) {
        localStorage.setItem('inventory_token', token);
    },

    clearToken() {
        localStorage.removeItem('inventory_token');
        localStorage.removeItem('inventory_user');
    },

    getUser() {
        const u = localStorage.getItem('inventory_user');
        return u ? JSON.parse(u) : null;
    },

    setUser(user) {
        localStorage.setItem('inventory_user', JSON.stringify(user));
    },

    async request(endpoint, options = {}) {
        const token = this.getToken();
        const headers = {
            'Content-Type': 'application/json',
            ...(options.headers || {})
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const config = {
            ...options,
            headers
        };

        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

            // Handle PDF binary response
            if (options.isBlob) {
                if (!response.ok) {
                    throw new Error('Failed to download PDF report');
                }
                return await response.blob();
            }

            const data = await response.json();

            if (!response.ok) {
                if (response.status === 401) {
                    this.clearToken();
                    window.location.hash = '#login';
                    showToast('Session expired. Please log in again.', 'danger');
                }
                throw new Error(data.error || 'API Request failed');
            }

            return data;
        } catch (err) {
            console.error(`API Error [${endpoint}]:`, err);
            throw err;
        }
    },

    get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    },

    post(endpoint, body) {
        return this.request(endpoint, { method: 'POST', body: JSON.stringify(body) });
    },

    put(endpoint, body) {
        return this.request(endpoint, { method: 'PUT', body: JSON.stringify(body) });
    },

    delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    },

    async downloadBlob(endpoint, filename) {
        try {
            const blob = await this.request(endpoint, { method: 'GET', isBlob: true });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
            showToast(`Downloaded ${filename}`, 'success');
        } catch (err) {
            showToast(err.message || 'Failed to download report PDF', 'danger');
        }
    }
};

// Toast notification helper
function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let icon = 'ℹ️';
    if (type === 'success') icon = '✅';
    if (type === 'danger') icon = '⚠️';
    if (type === 'warning') icon = '🔔';

    toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(50px)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}
