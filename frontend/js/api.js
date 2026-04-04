/* ============================================
   POCKET LAWYER 2.0 — API Client
   Replaces localStorage-only Store with real Flask API calls.
   ============================================ */

const API_BASE = (window.location.origin.startsWith('file') || window.location.hostname === 'localhost') 
  ? 'http://127.0.0.1:5000/api' 
  : window.location.origin + '/api';

const API = {
  _token: localStorage.getItem('pl_token'),
  _user: JSON.parse(localStorage.getItem('pl_user') || 'null'),

  // ── Auth State ──────────────────────────────────────────────────────────────

  setAuth(token, user) {
    this._token = token;
    this._user = user;
    localStorage.setItem('pl_token', token);
    localStorage.setItem('pl_user', JSON.stringify(user));
  },

  clearAuth() {
    this._token = null;
    this._user = null;
    localStorage.removeItem('pl_token');
    localStorage.removeItem('pl_user');
  },

  isLoggedIn() {
    return !!this._token && !!this._user;
  },

  getUser() {
    return this._user;
  },

  getToken() {
    return this._token;
  },

  // ── HTTP Helpers ────────────────────────────────────────────────────────────

  async _fetch(url, options = {}) {
    const headers = { ...options.headers };
    if (this._token) {
      headers['Authorization'] = `Bearer ${this._token}`;
    }
    if (!(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }

    const resp = await fetch(API_BASE + url, { ...options, headers });
    const data = await resp.json();

    if (!resp.ok) {
      if (resp.status === 401 && !url.includes('/login') && !url.includes('/register')) {
        this.clearAuth();
        window.location.href = 'login.html';
        throw new Error('Session expired');
      }
      throw new Error(data.error || `Request failed with status ${resp.status}`);
    }
    return data;
  },

  async get(url) {
    return this._fetch(url);
  },

  async post(url, body) {
    return this._fetch(url, {
      method: 'POST',
      body: JSON.stringify(body)
    });
  },

  async postForm(url, formData) {
    return this._fetch(url, {
      method: 'POST',
      body: formData,
      headers: {} // Let browser set Content-Type for FormData
    });
  },

  // ── Auth Endpoints ──────────────────────────────────────────────────────────

  async register(userData) {
    const data = await this.post('/auth/register', userData);
    this.setAuth(data.token, data.user);
    return data;
  },

  async login(email, password) {
    const data = await this.post('/auth/login', { email, password });
    this.setAuth(data.token, data.user);
    return data;
  },

  logout() {
    this.clearAuth();
    window.location.href = 'login.html';
  },

  // ── Case Endpoints ──────────────────────────────────────────────────────────

  async createCase(caseData) {
    return this.post('/cases', caseData);
  },

  async getCases() {
    return this.get('/cases');
  },

  async getCase(caseId) {
    return this.get(`/cases/${caseId}`);
  },

  async assignLawyer(caseId, lawyerId) {
    return this.post(`/cases/${caseId}/assign`, { lawyerId });
  },

  async addNote(caseId, content, hearingDate) {
    return this.post(`/cases/${caseId}/notes`, { content, hearingDate });
  },

  async exportToken(caseId) {
    return this.get(`/cases/${caseId}/token/export`);
  },

  async searchCases(query) {
    return this.get(`/search?q=${encodeURIComponent(query)}`);
  },

  // ── Chat Endpoints ──────────────────────────────────────────────────────────

  async sendChat(message, sessionId, caseId) {
    return this.post('/chat', { message, sessionId, caseId });
  },

  async getChatSessions() {
    return this.get('/chat/sessions');
  },

  async getChatSession(sessionId) {
    return this.get(`/chat/sessions/${sessionId}`);
  },

  // ── Upload Endpoints ────────────────────────────────────────────────────────

  async uploadDocument(caseId, file) {
    const formData = new FormData();
    formData.append('case_id', caseId);
    formData.append('file', file);

    // Use raw fetch for FormData (needs auth header but not content-type)
    const resp = await fetch(API_BASE + '/upload', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${this._token}` },
      body: formData
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || 'Upload failed');
    return data;
  },

  async getDocument(docId) {
    return this.get(`/documents/${docId}`);
  },

  async getDocumentRisks(docId) {
    return this.get(`/documents/${docId}/risks`);
  },

  // ── Legal Services & Appointments ──────────────────────────

  async getAppointments() {
    return this.get('/appointments');
  },

  async bookAppointment(lawyerId, dateTime, notes = '', caseId = null) {
    return this.post('/appointments/book', { lawyerId, dateTime, notes, caseId });
  },

  async listLegalServices() {
    return this.get('/services/list');
  },

  async requestEsign(formData) {
    // Expects FormData with signerName, aadhaarLast4, document (file)
    return this.postForm('/services/esign', formData);
  },

  async requestEstamp(formData) {
    // Expects FormData with state, value, firstParty, secondParty, document (file)
    return this.postForm('/services/estamp', formData);
  },

  async requestKyc(kycType = 'video') {
    return this.post('/services/kyc', { kyc_type: kycType });
  },

  async requestDraft(template, data) {
    return this.post('/services/draft', { template, data });
  },

  async getServiceLogs() {
    return this.get('/services/logs');
  },

  async getCaseSuggestions(caseId) {
    return this.get(`/cases/${caseId}/suggestions`);
  },

  async updateSuggestionStatus(suggestionId, status) {
    return this.post(`/services/suggestions/${suggestionId}/status`, { status });
  },

  getDownloadUrl(filename) {
    return `${API_BASE}/services/download/${filename}?token=${this._token}`;
  }
};
