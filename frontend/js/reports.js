/* ==========================================================================
   REPORTS & ANALYTICS CONTROLLER + PDF EXPORTS
   ========================================================================== */

const Reports = {
    async load() {
        try {
            const res = await API.get('/reports/analytics');
            this.renderSummary(res.summary);
            this.renderMostActive(res.most_active_products);
        } catch (err) {
            showToast('Failed to load analytics: ' + err.message, 'danger');
        }
    },

    renderSummary(summary) {
        if (!summary) return;
        document.getElementById('report-total-prods').textContent = summary.total_products || 0;
        document.getElementById('report-total-val').textContent = `$${(summary.total_valuation || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
        document.getElementById('report-low-count').textContent = summary.low_stock_count || 0;
    },

    renderMostActive(items) {
        const tbody = document.getElementById('report-most-active-tbody');
        if (!tbody) return;

        if (!items || items.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color: var(--text-muted);">No stock movements logged yet.</td></tr>`;
            return;
        }

        tbody.innerHTML = items.map((item, index) => `
            <tr>
                <td><strong>#${index + 1}</strong></td>
                <td><code>${item.sku}</code></td>
                <td><strong>${item.name}</strong></td>
                <td><span class="badge badge-info">${item.total_volume} Units Moved</span></td>
            </tr>
        `).join('');
    },

    exportProductsPDF() {
        API.downloadBlob('/reports/export-pdf?type=products', 'products_inventory_report.pdf');
    },

    exportLowStockPDF() {
        API.downloadBlob('/reports/export-pdf?type=low_stock', 'low_stock_alerts_report.pdf');
    },

    exportStockHistoryPDF() {
        API.downloadBlob('/reports/export-pdf?type=stock', 'stock_movement_report.pdf');
    }
};

window.Reports = Reports;
