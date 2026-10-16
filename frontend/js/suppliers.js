/* ==========================================================================
   SUPPLIER MANAGEMENT CONTROLLER (CRUD)
   ========================================================================== */

const Suppliers = {
    list: [],

    async load() {
        try {
            const res = await API.get('/suppliers');
            this.list = res.suppliers || [];
            this.render();
        } catch (err) {
            showToast('Failed to load suppliers: ' + err.message, 'danger');
        }
    },

    render() {
        const tbody = document.getElementById('suppliers-tbody');
        if (!tbody) return;

        const user = API.getUser();
        const isAdmin = user && user.role === 'admin';

        if (this.list.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color: var(--text-muted); padding: 20px;">No suppliers registered yet.</td></tr>`;
            return;
        }

        tbody.innerHTML = this.list.map(s => `
            <tr>
                <td><strong>${s.name}</strong></td>
                <td>${s.contact_name || '-'}</td>
                <td>${s.email ? `<a href="mailto:${s.email}" style="color:var(--primary-color);">${s.email}</a>` : '-'}</td>
                <td>${s.phone || '-'}</td>
                <td><small>${s.address || '-'}</small></td>
                <td>
                    ${isAdmin ? `
                        <button class="btn btn-sm btn-secondary" onclick="Suppliers.openModal(${s.id})">Edit</button>
                        <button class="btn btn-sm btn-danger" onclick="Suppliers.deleteSupplier(${s.id}, '${s.name}')">Delete</button>
                    ` : '<small style="color: var(--text-dim);">Read Only</small>'}
                </td>
            </tr>
        `).join('');
    },

    openModal(supId = null) {
        const modal = document.getElementById('modal-supplier');
        const title = document.getElementById('modal-supplier-title');
        const form = document.getElementById('form-supplier');

        form.reset();
        document.getElementById('sup-id').value = '';

        if (supId) {
            const s = this.list.find(item => item.id === supId);
            if (s) {
                title.textContent = 'Edit Supplier';
                document.getElementById('sup-id').value = s.id;
                document.getElementById('sup-name').value = s.name;
                document.getElementById('sup-contact').value = s.contact_name;
                document.getElementById('sup-email').value = s.email;
                document.getElementById('sup-phone').value = s.phone;
                document.getElementById('sup-address').value = s.address;
            }
        } else {
            title.textContent = 'Add Supplier';
        }

        modal.classList.add('active');
    },

    closeModal() {
        const modal = document.getElementById('modal-supplier');
        if (modal) modal.classList.remove('active');
    },

    async saveSupplier(e) {
        e.preventDefault();
        const id = document.getElementById('sup-id').value;
        const payload = {
            name: document.getElementById('sup-name').value.trim(),
            contact_name: document.getElementById('sup-contact').value.trim(),
            email: document.getElementById('sup-email').value.trim(),
            phone: document.getElementById('sup-phone').value.trim(),
            address: document.getElementById('sup-address').value.trim()
        };

        try {
            if (id) {
                await API.put(`/suppliers/${id}`, payload);
                showToast('Supplier details updated.', 'success');
            } else {
                await API.post('/suppliers', payload);
                showToast('Supplier added successfully.', 'success');
            }
            this.closeModal();
            await this.load();
        } catch (err) {
            showToast(err.message, 'danger');
        }
    },

    async deleteSupplier(id, name) {
        if (!confirm(`Delete supplier "${name}"?`)) return;

        try {
            await API.delete(`/suppliers/${id}`);
            showToast(`Supplier "${name}" deleted.`, 'info');
            await this.load();
        } catch (err) {
            showToast(err.message, 'danger');
        }
    }
};

window.Suppliers = Suppliers;
