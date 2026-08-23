/* ==========================================================================
   AUTHENTICATION & USER STATE MANAGEMENT
   ========================================================================== */

const Auth = {
    init() {
        const loginForm = document.getElementById('login-form');
        const registerForm = document.getElementById('register-form');
        const logoutBtn = document.getElementById('logout-btn');

        if (loginForm) {
            loginForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const username = document.getElementById('login-username').value.trim();
                const password = document.getElementById('login-password').value;

                try {
                    const res = await API.post('/auth/login', { username, password });
                    API.setToken(res.token);
                    API.setUser(res.user);
                    showToast(`Welcome back, ${res.user.username}!`, 'success');
                    this.updateUIState();
                    window.location.hash = '#dashboard';
                } catch (err) {
                    showToast(err.message, 'danger');
                }
            });
        }

        if (registerForm) {
            registerForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const username = document.getElementById('reg-username').value.trim();
                const email = document.getElementById('reg-email').value.trim();
                const password = document.getElementById('reg-password').value;
                const role = document.getElementById('reg-role').value;

                try {
                    const res = await API.post('/auth/register', { username, email, password, role });
                    API.setToken(res.token);
                    API.setUser(res.user);
                    showToast('Account registered successfully!', 'success');
                    this.updateUIState();
                    window.location.hash = '#dashboard';
                } catch (err) {
                    showToast(err.message, 'danger');
                }
            });
        }

        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                API.clearToken();
                showToast('Logged out successfully.', 'info');
                this.updateUIState();
                window.location.hash = '#login';
            });
        }

        this.updateUIState();
    },

    updateUIState() {
        const token = API.getToken();
        const user = API.getUser();
        const appLayout = document.getElementById('app-layout');
        const authView = document.getElementById('view-auth');

        if (token && user) {
            if (appLayout) appLayout.style.display = 'flex';
            if (authView) authView.style.display = 'none';

            // Populate user info
            const nameEl = document.getElementById('user-profile-name');
            const roleEl = document.getElementById('user-profile-role');
            const avatarEl = document.getElementById('user-avatar');

            if (nameEl) nameEl.textContent = user.username;
            if (roleEl) {
                roleEl.textContent = user.role;
                roleEl.className = `role-badge ${user.role}`;
            }
            if (avatarEl) avatarEl.textContent = user.username.charAt(0).toUpperCase();

            // Toggle admin-only UI elements
            document.querySelectorAll('.admin-only').forEach(el => {
                el.style.display = user.role === 'admin' ? '' : 'none';
            });

        } else {
            if (appLayout) appLayout.style.display = 'none';
            if (authView) authView.style.display = 'flex';
        }
    }
};

window.Auth = Auth;
