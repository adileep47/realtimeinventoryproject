/* ==========================================================================
   PRODUCT MANAGEMENT CONTROLLER (CRUD + SEARCH & FILTER + PDF EXPORT)
   ========================================================================== */

const Products = {
    productsList: [],
    categoriesList: [],
    suppliersList: [],

    async load() {
        await this.loadDropdowns();
        await this.fetchProducts();
    },

    async loadDropdowns() {
        try {
            const [catRes, supRes] = await Promise.all([
                API.get('/categories'),
                API.get('/suppliers')
            ]);
            this.categoriesList = catRes.categories || [];
            this.suppliersList = supRes.suppliers || [];

            this.populateSelectOptions();
        } catch (err) {
            console.error('Failed to load dropdowns', err);
        }
    },

    populateSelectOptions() {
        const catSelect = document.getElementById('product-filter-category');
        const catFormSelect = document.getElementById('prod-category');
        const supFormSelect = document.getElementById('prod-supplier');

        if (catSelect) {
            catSelect.innerHTML = `<option value="">All Categories</option>` +
                this.categoriesList.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
        }

        if (catFormSelect) {
            catFormSelect.innerHTML = `<option value="">None / Uncategorized</option>` +
                this.categoriesList.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
        }

        if (supFormSelect) {
            supFormSelect.innerHTML = `<option value="">None / No Supplier</option>` +
                this.suppliersList.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
        }
    },

    async fetchProducts() {
        const search = document.getElementById('product-search-input')?.value || '';
        const categoryId = document.getElementById('product-filter-category')?.value || '';
        const status = document.getElementById('product-filter-status')?.value || '';

        let query = `/products?search=${encodeURIComponent(search)}`;
        if (categoryId) query += `&category_id=${categoryId}`;
        if (status) query += `&status=${status}`;

        try {
            const res = await API.get(query);
            this.productsList = res.products || [];
            this.renderTable();
        } catch (err) {
            showToast('Failed to fetch products: ' + err.message, 'danger');
        }
    },

    renderTable() {
        const tbody = document.getElementById('products-tbody');
        if (!tbody) return;

        const user = API.getUser();
        const isAdmin = user && user.role === 'admin';

        if (this.productsList.length === 0) {
            tbody.innerHTML = `<tr><td colspan="9" style="text-align:center; color: var(--text-muted); padding: 30px;">No products found matching your search.</td></tr>`;
            return;
        }

        tbody.innerHTML = this.productsList.map(p => {
            let statusBadge = '<span class="badge badge-success">In Stock</span>';
            if (p.quantity === 0) {
                statusBadge = '<span class="badge badge-danger">Out of Stock</span>';
            } else if (p.is_low_stock) {
                statusBadge = '<span class="badge badge-warning">Low Stock Alert</span>';
            }

            return `
                <tr>
                    <td><code>${p.sku}</code></td>
                    <td><strong>${p.name}</strong></td>
                    <td><span class="badge badge-info">${p.category_name}</span></td>
                    <td>${p.supplier_name}</td>
                    <td>$${p.price.toFixed(2)}</td>
                    <td><strong>${p.quantity}</strong> ${p.unit}</td>
                    <td>${p.reorder_level} ${p.unit}</td>
                    <td>${statusBadge}</td>
                    <td>
                        <div style="display:flex; gap: 6px;">
                            <button class="btn btn-sm btn-secondary" onclick="Products.openModal(${p.id})">Edit</button>
                            <button class="btn btn-sm btn-primary" onclick="Stock.openStockModal(${p.id}, 'IN')">+ Stock</button>
                            ${isAdmin ? `<button class="btn btn-sm btn-danger" onclick="Products.deleteProduct(${p.id}, '${p.name}')">Delete</button>` : ''}
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    },

    openModal(productId = null) {
        const modal = document.getElementById('modal-product');
        const title = document.getElementById('modal-product-title');
        const form = document.getElementById('form-product');
        
        form.reset();
        document.getElementById('prod-id').value = '';

        if (productId) {
            const p = this.productsList.find(item => item.id === productId);
            if (p) {
                title.textContent = 'Edit Product';
                document.getElementById('prod-id').value = p.id;
                document.getElementById('prod-sku').value = p.sku;
                document.getElementById('prod-name').value = p.name;
                document.getElementById('prod-category').value = p.category_id || '';
                document.getElementById('prod-supplier').value = p.supplier_id || '';
                document.getElementById('prod-unit').value = p.unit;
                document.getElementById('prod-price').value = p.price;
                document.getElementById('prod-quantity').value = p.quantity;
                document.getElementById('prod-reorder').value = p.reorder_level;
            }
        } else {
            title.textContent = 'Add New Product';
        }

        modal.classList.add('active');
    },

    closeModal() {
        const modal = document.getElementById('modal-product');
        if (modal) modal.classList.remove('active');
    },

    async saveProduct(e) {
        e.preventDefault();
        const id = document.getElementById('prod-id').value;
        const payload = {
            sku: document.getElementById('prod-sku').value.trim(),
            name: document.getElementById('prod-name').value.trim(),
            category_id: document.getElementById('prod-category').value ? parseInt(document.getElementById('prod-category').value) : null,
            supplier_id: document.getElementById('prod-supplier').value ? parseInt(document.getElementById('prod-supplier').value) : null,
            unit: document.getElementById('prod-unit').value.trim() || 'pcs',
            price: parseFloat(document.getElementById('prod-price').value) || 0.0,
            quantity: parseInt(document.getElementById('prod-quantity').value) || 0,
            reorder_level: parseInt(document.getElementById('prod-reorder').value) || 10
        };

        try {
            if (id) {
                await API.put(`/products/${id}`, payload);
                showToast('Product updated successfully.', 'success');
            } else {
                await API.post('/products', payload);
                showToast('New product created successfully.', 'success');
            }
            this.closeModal();
            await this.fetchProducts();
        } catch (err) {
            showToast(err.message, 'danger');
        }
    },

    async deleteProduct(id, name) {
        if (!confirm(`Are you sure you want to delete product "${name}"?`)) return;

        try {
            await API.delete(`/products/${id}`);
            showToast(`Product "${name}" deleted.`, 'info');
            await this.fetchProducts();
        } catch (err) {
            showToast(err.message, 'danger');
        }
    },

    exportPDF() {
        API.downloadBlob('/reports/export-pdf?type=products', 'products_inventory_report.pdf');
    }
};

window.Products = Products;
