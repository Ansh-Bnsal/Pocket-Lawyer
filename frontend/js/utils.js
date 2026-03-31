/* ============================================
   POCKET LAWYER 2.0 — Utilities
   Ported from v1 with minor improvements.
   ============================================ */

const Utils = {
  formatDate(isoString) {
    if (!isoString) return '';
    const d = new Date(isoString);
    return d.toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric' });
  },

  formatDateTime(isoString) {
    if (!isoString) return '';
    const d = new Date(isoString);
    return d.toLocaleDateString('en-IN', {
      year: 'numeric', month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit'
    });
  },

  timeAgo(isoString) {
    const seconds = Math.floor((new Date() - new Date(isoString)) / 1000);
    if (seconds < 60) return 'Just now';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return minutes + 'm ago';
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return hours + 'h ago';
    const days = Math.floor(hours / 24);
    if (days < 30) return days + 'd ago';
    return Utils.formatDate(isoString);
  },

  formatFileSize(bytes) {
    if (!bytes || bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  },

  escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  },

  truncate(str, len = 80) {
    if (!str) return '';
    return str.length > len ? str.substring(0, len) + '...' : str;
  },

  caseTypeLabels: {
    property: 'Property & Real Estate', family: 'Family Law',
    criminal: 'Criminal Law', corporate: 'Corporate & Business',
    labor: 'Labor & Employment', consumer: 'Consumer Rights',
    tax: 'Tax Law', civil: 'Civil Litigation',
    ip: 'Intellectual Property', other: 'Other',
    'General': 'General Legal', 'General Legal Query': 'General Legal'
  },

  caseTypeIcons: {
    property: '🏠', family: '👨‍👩‍👧', criminal: '🔒',
    corporate: '🏢', labor: '👷', consumer: '🛒',
    tax: '📊', civil: '📜', ip: '💡', other: '📋',
    'General': '📋', 'General Legal Query': '📋'
  },

  getCaseTypeLabel(type) {
    if (!type) return 'General';
    return this.caseTypeLabels[type] || type;
  },

  getCaseTypeIcon(type) {
    if (!type) return '📋';
    return this.caseTypeIcons[type] || '📋';
  },

  statusColors: { active: 'success', pending: 'warning', closed: 'neutral', resolved: 'neutral' },
  riskColors: { low: 'risk-low', medium: 'risk-medium', high: 'risk-high', LOW: 'risk-low', MEDIUM: 'risk-medium', HIGH: 'risk-high' },

  showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <span>${type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ'}</span>
      <span>${Utils.escapeHtml(message)}</span>
    `;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100px)';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  },

  requireAuth() {
    if (!API.isLoggedIn()) {
      window.location.href = 'login.html';
      return false;
    }
    return true;
  },

  getInitials(name) {
    if (!name) return '?';
    return name.split(' ').map(w => w[0]).join('').toUpperCase().substring(0, 2);
  },

  getRiskBadge(level) {
    const l = (level || 'medium').toLowerCase();
    const icon = l === 'high' ? '🔴' : l === 'medium' ? '🟡' : '🟢';
    return `<span class="${this.riskColors[l]}" style="padding:4px 12px;border-radius:20px;font-size:0.82rem;">${icon} ${l.toUpperCase()}</span>`;
  }
};
