/* ==========================================================================
   DASHBOARD CONTROLLER & CHART.JS INTEGRATION
   ========================================================================== */

let trendChartInstance = null;
let categoryChartInstance = null;

const Dashboard = {
    async load() {
        try {
            const res = await API.get('/dashboard/stats');
            this.renderKPIs(res.kpi);
            this.renderLowStock(res.low_stock_items);
            this.renderRecentActivity(res.recent_stock_activity);
            this.renderCharts(res.chart_stock_trend, res.chart_category_distribution);
        } catch (err) {
            showToast('Failed to load dashboard data: ' + err.message, 'danger');
        }
    },

    renderKPIs(kpi) {
        document.getElementById('kpi-total-products').textContent = kpi.total_products || 0;
        document.getElementById('kpi-low-stock').textContent = kpi.low_stock_count || 0;
        document.getElementById('kpi-out-of-stock').textContent = kpi.out_of_stock_count || 0;
        document.getElementById('kpi-valuation').textContent = `$${(kpi.total_inventory_value || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
    },

    renderLowStock(items) {
        const tbody = document.getElementById('dashboard-low-stock-tbody');
        if (!tbody) return;

        if (!items || items.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color: var(--text-muted); padding: 20px;">No low stock alerts. All items adequately stocked! 🎉</td></tr>`;
            return;
        }

        tbody.innerHTML = items.map(item => `
            <tr>
                <td><span class="badge badge-warning">${item.sku}</span></td>
                <td><strong>${item.name}</strong></td>
                <td><span class="badge badge-danger">${item.quantity} ${item.unit}</span></td>
                <td>${item.reorder_level} ${item.unit}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="Stock.openStockModal(${item.id}, 'IN')">+ Restock</button>
                </td>
            </tr>
        `).join('');
    },

    renderRecentActivity(activities) {
        const tbody = document.getElementById('dashboard-recent-activity-tbody');
        if (!tbody) return;

        if (!activities || activities.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color: var(--text-muted);">No recent stock activity logged.</td></tr>`;
            return;
        }

        tbody.innerHTML = activities.map(act => {
            const badgeClass = act.type === 'IN' ? 'badge-success' : 'badge-danger';
            const formattedTime = act.timestamp ? act.timestamp.replace('T', ' ').substring(0, 16) : '';
            return `
                <tr>
                    <td>${formattedTime}</td>
                    <td><strong>${act.product_name}</strong></td>
                    <td><span class="badge ${badgeClass}">${act.type} (${act.quantity})</span></td>
                    <td>${act.reason || '-'}</td>
                    <td><small style="color: var(--text-muted);">${act.username}</small></td>
                </tr>
            `;
        }).join('');
    },

    renderCharts(trendData, categoryData) {
        if (typeof Chart === 'undefined') return;

        // 1. Stock Movement Trend Chart
        const ctxTrend = document.getElementById('chart-stock-trend');
        if (ctxTrend) {
            if (trendChartInstance) trendChartInstance.destroy();
            trendChartInstance = new Chart(ctxTrend, {
                type: 'bar',
                data: {
                    labels: trendData.labels.length > 0 ? trendData.labels : ['Current Month'],
                    datasets: [
                        {
                            label: 'Stock IN (Added)',
                            data: trendData.stock_in.length > 0 ? trendData.stock_in : [0],
                            backgroundColor: 'rgba(16, 185, 129, 0.7)',
                            borderColor: '#10b981',
                            borderWidth: 1,
                            borderRadius: 6
                        },
                        {
                            label: 'Stock OUT (Deducted)',
                            data: trendData.stock_out.length > 0 ? trendData.stock_out : [0],
                            backgroundColor: 'rgba(239, 68, 68, 0.7)',
                            borderColor: '#ef4444',
                            borderWidth: 1,
                            borderRadius: 6
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { labels: { color: '#94a3b8' } }
                    },
                    scales: {
                        x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                        y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
                    }
                }
            });
        }

        // 2. Category Distribution Doughnut Chart
        const ctxCat = document.getElementById('chart-category-distribution');
        if (ctxCat) {
            if (categoryChartInstance) categoryChartInstance.destroy();
            categoryChartInstance = new Chart(ctxCat, {
                type: 'doughnut',
                data: {
                    labels: categoryData.labels.length > 0 ? categoryData.labels : ['No Categories'],
                    datasets: [{
                        data: categoryData.data.length > 0 ? categoryData.data : [1],
                        backgroundColor: [
                            '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4'
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'right', labels: { color: '#94a3b8' } }
                    }
                }
            });
        }
    }
};

window.Dashboard = Dashboard;
