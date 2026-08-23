/* ==========================================================================
   STOCK IN / STOCK OUT CONTROLLER
   ========================================================================== */

const Stock = {
    historyList: [],

    async load() {
        await this.loadStockHistory();
        await this.populateProductDropdown();
    },

    async populateProductDropdown() {
        const select = document.getElementById('stock-product-select');
        if (!select) return;

        try {
            const res = await API.get('/products');
            const products = res.products || [];

            select.innerHTML = `<option value="">-- Select Product --</option>` +
                products.map(p => `<option value="${p.id}">${p.sku} - ${p.name} (Current Stock: ${p.quantity} ${p.unit})</option>`).join('');
        } catch (err) {
            console.error('Failed to load products for stock modal', err);
        }
    },

    async loadStockHistory() {
        const typeFilter = document.getElementById('stock-type-filter')?.value || '';
        let query = '/stock/history?limit=100';
        if (typeFilter) query += `&type=${typeFilter}`;

        try {
            const res = await API.get(query);
            this.historyList = res.movements || [];
            this.renderHistoryTable();
        } catch (err) {
            showToast('Failed to load stock history: ' + err.message, 'danger');
        }
    },

    renderHistoryTable() {
        const tbody = document.getElementById('stock-history-tbody');
        if (!tbody) return;

        if (this.historyList.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color: var(--text-muted); padding: 20px;">No stock movements recorded yet.</td></tr>`;
            return;
        }

        tbody.innerHTML = this.historyList.map(m => {
            const badgeClass = m.type === 'IN' ? 'badge-success' : 'badge-danger';
            const formattedTime = m.timestamp ? m.timestamp.replace('T', ' ').substring(0, 16) : '';
            return `
                <tr>
                    <td><small style="color: var(--text-dim);">${formattedTime}</small></td>
                    <td><code>${m.product_sku}</code></td>
                    <td><strong>${m.product_name}</strong></td>
                    <td><span class="badge ${badgeClass}">${m.type}</span></td>
                    <td><strong>${m.type === 'IN' ? '+' : '-'}${m.quantity}</strong></td>
                    <td>${m.reason || '-'}</td>
                    <td><small style="color: var(--text-muted);">${m.username}</small></td>
                </tr>
            `;
        }).join('');
    },

    openStockModal(productId = null, defaultType = 'IN') {
        const modal = document.getElementById('modal-stock-movement');
        const form = document.getElementById('form-stock-movement');

        form.reset();
        this.populateProductDropdown().then(() => {
            if (productId) {
                document.getElementById('stock-product-select').value = productId;
            }
            document.getElementById('stock-type').value = defaultType;
            modal.classList.add('active');
        });
    },

    closeStockModal() {
        const modal = document.getElementById('modal-stock-movement');
        if (modal) modal.classList.remove('active');
    },

    async saveMovement(e) {
        e.preventDefault();
        const productId = document.getElementById('stock-product-select').value;
        const type = document.getElementById('stock-type').value;
        const quantity = parseInt(document.getElementById('stock-qty').value) || 0;
        const reason = document.getElementById('stock-reason').value.trim();

        if (!productId || quantity <= 0) {
            showToast('Please select a product and enter a valid quantity.', 'warning');
            return;
        }

        try {
            await API.post('/stock/movement', {
                product_id: parseInt(productId),
                type,
                quantity,
                reason
            });

            showToast(`Stock ${type} logged successfully! Product quantity auto-updated.`, 'success');
            this.closeStockModal();
            await this.loadStockHistory();

            // Refresh products view if open
            if (window.Products && typeof window.Products.fetchProducts === 'function') {
                window.Products.fetchProducts();
            }
        } catch (err) {
            showToast(err.message, 'danger');
        }
    },

    exportPDF() {
        API.downloadBlob('/reports/export-pdf?type=stock', 'stock_movement_report.pdf');
    }
};

window.Stock = Stock;
