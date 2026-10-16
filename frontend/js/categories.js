/* ==========================================================================
   CATEGORY MANAGEMENT CONTROLLER (CRUD)
   ========================================================================== */

const Categories = {
    list: [],

    async load() {
        try {
            const res = await API.get('/categories');
            this.list = res.categories || [];
            this.render();
        } catch (err) {
            showToast('Failed to load categories: ' + err.message, 'danger');
        }
    },

    render() {
        const tbody = document.getElementById('categories-tbody');
        if (!tbody) return;

        const user = API.getUser();
        const isAdmin = user && user.role === 'admin';

        if (this.list.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color: var(--text-muted); padding: 20px;">No categories configured yet.</td></tr>`;
            return;
        }

        tbody.innerHTML = this.list.map(c => `
            <tr>
                <td><strong>${c.name}</strong></td>
                <td>${c.description || '<span style="color: var(--text-dim);">No description</span>'}</td>
                <td><span class="badge badge-info">${c.product_count} Products</span></td>
                <td>
                    ${isAdmin ? `
                        <button class="btn btn-sm btn-secondary" onclick="Categories.openModal(${c.id})">Edit</button>
                        <button class="btn btn-sm btn-danger" onclick="Categories.deleteCategory(${c.id}, '${c.name}')">Delete</button>
                    ` : '<small style="color: var(--text-dim);">Read Only</small>'}
                </td>
            </tr>
        `).join('');
    },

    openModal(catId = null) {
        const modal = document.getElementById('modal-category');
        const title = document.getElementById('modal-category-title');
        const form = document.getElementById('form-category');

        form.reset();
        document.getElementById('cat-id').value = '';

        if (catId) {
            const c = this.list.find(item => item.id === catId);
            if (c) {
                title.textContent = 'Edit Category';
                document.getElementById('cat-id').value = c.id;
                document.getElementById('cat-name').value = c.name;
                document.getElementById('cat-description').value = c.description;
            }
        } else {
            title.textContent = 'Add Category';
        }

        modal.classList.add('active');
    },

    closeModal() {
        const modal = document.getElementById('modal-category');
        if (modal) modal.classList.remove('active');
    },

    async saveCategory(e) {
        e.preventDefault();
        const id = document.getElementById('cat-id').value;
        const payload = {
            name: document.getElementById('cat-name').value.trim(),
            description: document.getElementById('cat-description').value.trim()
        };

        try {
            if (id) {
                await API.put(`/categories/${id}`, payload);
                showToast('Category updated.', 'success');
            } else {
                await API.post('/categories', payload);
                showToast('Category added.', 'success');
            }
            this.closeModal();
            await this.load();
        } catch (err) {
            showToast(err.message, 'danger');
        }
    },

    async deleteCategory(id, name) {
        if (!confirm(`Delete category "${name}"?`)) return;

        try {
            await API.delete(`/categories/${id}`);
            showToast(`Category "${name}" deleted.`, 'info');
            await this.load();
        } catch (err) {
            showToast(err.message, 'danger');
        }
    }
};

window.Categories = Categories;
