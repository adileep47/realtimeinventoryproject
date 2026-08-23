/* ==========================================================================
   ACTIVITY LOG CONTROLLER (AUDIT TRAIL)
   ========================================================================== */

const Activity = {
    async load() {
        try {
            const res = await API.get('/activity-log?limit=100');
            this.renderTimeline(res.activities || []);
        } catch (err) {
            showToast('Failed to load activity log: ' + err.message, 'danger');
        }
    },

    renderTimeline(activities) {
        const container = document.getElementById('activity-timeline');
        if (!container) return;

        if (activities.length === 0) {
            container.innerHTML = `<div style="text-align:center; color: var(--text-muted); padding: 30px;">No system activities logged yet.</div>`;
            return;
        }

        container.innerHTML = activities.map(act => {
            const timeStr = act.timestamp ? act.timestamp.replace('T', ' ').substring(0, 19) : '';
            let actionBadge = `<span class="badge badge-info">${act.action}</span>`;

            if (act.action === 'CREATE' || act.action === 'REGISTER') actionBadge = `<span class="badge badge-success">${act.action}</span>`;
            if (act.action === 'DELETE') actionBadge = `<span class="badge badge-danger">${act.action}</span>`;
            if (act.action === 'STOCK_OUT') actionBadge = `<span class="badge badge-warning">${act.action}</span>`;

            return `
                <div class="timeline-item">
                    <div class="timeline-marker"></div>
                    <div class="timeline-content">
                        <div class="timeline-header">
                            <div>
                                <span class="timeline-user">👤 ${act.username}</span>
                                <span style="margin-left: 8px;">${actionBadge}</span>
                                <span class="badge badge-secondary" style="margin-left: 4px;">${act.entity_type}</span>
                            </div>
                            <span class="timeline-time">⏰ ${timeStr}</span>
                        </div>
                        <div class="timeline-body">
                            ${act.details}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }
};

window.Activity = Activity;
