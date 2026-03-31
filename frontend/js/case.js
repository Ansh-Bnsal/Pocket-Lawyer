/* ============================================
   POCKET LAWYER 2.0 — Dashboard Logic
   Wired to real Flask API.
   ============================================ */

let selectedCaseType = '';
let selectedRisk = 'medium';
let currentFilter = 'all';

document.addEventListener('DOMContentLoaded', async () => {
  if (!Utils.requireAuth()) return;
  const user = API.getUser();

  const greetEl = document.getElementById('user-greeting');
  if (greetEl) greetEl.textContent = '👤 ' + user.name;
  const welcomeEl = document.getElementById('welcome-msg');
  if (welcomeEl) welcomeEl.textContent = 'Welcome, ' + user.name.split(' ')[0];

  await loadCases();
  renderCaseTypeSelector();
});

function handleLogout() {
  API.logout();
}

let allCases = [];

async function loadCases() {
  try {
    allCases = await API.getCases();
  } catch (err) {
    Utils.showToast('Failed to load cases: ' + err.message, 'error');
    allCases = [];
  }
  renderStats();
  renderCaseList();
}

function renderStats() {
  const cases = allCases;
  const active = cases.filter(c => c.status === 'active').length;
  const pending = cases.filter(c => c.status === 'pending').length;
  const totalDocs = cases.reduce((sum, c) => sum + (c.documents?.length || 0), 0);

  const grid = document.getElementById('stats-grid');
  if (!grid) return;
  grid.innerHTML = `
    <div class="stat-card">
      <div class="stat-card-icon blue">📋</div>
      <h3>${cases.length}</h3>
      <p>Total Cases</p>
    </div>
    <div class="stat-card">
      <div class="stat-card-icon green">🟢</div>
      <h3>${active}</h3>
      <p>Active Cases</p>
    </div>
    <div class="stat-card">
      <div class="stat-card-icon amber">🟡</div>
      <h3>${pending}</h3>
      <p>Pending</p>
    </div>
    <div class="stat-card">
      <div class="stat-card-icon purple">📂</div>
      <h3>${totalDocs}</h3>
      <p>Documents</p>
    </div>
  `;

  const badge = document.getElementById('total-cases-badge');
  if (badge) badge.textContent = cases.length;
}

function renderCaseList(filter) {
  filter = filter || currentFilter;
  let cases = [...allCases];

  if (filter !== 'all') {
    cases = cases.filter(c => c.status === filter);
  }
  cases.sort((a, b) => new Date(b.updated_at || b.created_at) - new Date(a.updated_at || a.created_at));

  const listEl = document.getElementById('case-list');
  if (!listEl) return;

  if (cases.length === 0) {
    listEl.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">📋</div>
        <h3>${filter === 'all' ? 'No Cases Yet' : 'No ' + filter + ' cases'}</h3>
        <p>${filter === 'all' ? 'Create your first case to get started with AI-powered legal case management.' : 'No cases match this filter.'}</p>
        ${filter === 'all' ? '<button class="btn btn-primary" onclick="openCreateCase()">➕ Create Your First Case</button>' : ''}
      </div>
    `;
    return;
  }

  listEl.innerHTML = cases.map(c => `
    <a href="case_detail.html?id=${c.id}" class="case-item">
      <span class="case-status-dot ${c.status}"></span>
      <div class="case-info">
        <h4>${Utils.escapeHtml(c.title)}</h4>
        <p>${Utils.getCaseTypeIcon(c.case_type)} ${Utils.getCaseTypeLabel(c.case_type)} · ${Utils.escapeHtml(Utils.truncate(c.description, 60))}</p>
      </div>
      <div class="case-meta">
        <span class="badge badge-${Utils.statusColors[c.status] || 'neutral'}">${c.status}</span>
        ${Utils.getRiskBadge(c.risk_level)}
        <span class="case-date">${Utils.timeAgo(c.updated_at || c.created_at)}</span>
      </div>
    </a>
  `).join('');
}

function filterCases(filter) {
  currentFilter = filter;
  document.querySelectorAll('.filter-chip').forEach(chip => {
    chip.classList.toggle('active', chip.textContent.toLowerCase() === filter);
  });
  renderCaseList(filter);
}

function renderCaseTypeSelector() {
  const container = document.getElementById('case-type-selector');
  if (!container) return;
  const types = Object.entries(Utils.caseTypeLabels).filter(([k]) => !k.includes(' '));
  container.innerHTML = types.map(([key, label]) => `
    <button type="button" class="case-type-option" data-type="${key}" onclick="selectCaseType('${key}')">
      <span class="type-icon">${Utils.getCaseTypeIcon(key)}</span>
      <span class="type-name">${label}</span>
    </button>
  `).join('');
}

function selectCaseType(type) {
  selectedCaseType = type;
  document.querySelectorAll('.case-type-option').forEach(el => {
    el.classList.toggle('selected', el.dataset.type === type);
  });
}

function selectRisk(level) {
  selectedRisk = level;
  document.querySelectorAll('[data-risk]').forEach(el => {
    el.classList.toggle('active', el.dataset.risk === level);
  });
}

function openCreateCase() {
  document.getElementById('modal-overlay')?.classList.remove('hidden');
}

function closeModal() {
  document.getElementById('modal-overlay')?.classList.add('hidden');
}

async function handleCreateCase(e) {
  e.preventDefault();
  const btn = e.target.querySelector('button[type="submit"]');
  btn.disabled = true;
  btn.textContent = '🧠 AI is analyzing...';

  const title = document.getElementById('case-title').value;
  const desc = document.getElementById('case-desc').value;

  try {
    const result = await API.createCase({
      title,
      description: desc,
      caseType: selectedCaseType,
      riskLevel: selectedRisk
    });
    Utils.showToast('Case created! AI analysis complete.', 'success');
    closeModal();
    document.getElementById('create-case-form').reset();
    selectedCaseType = '';
    document.querySelectorAll('.case-type-option').forEach(el => el.classList.remove('selected'));
    await loadCases();
  } catch (err) {
    Utils.showToast('Error: ' + err.message, 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Create Case';
  }
}
