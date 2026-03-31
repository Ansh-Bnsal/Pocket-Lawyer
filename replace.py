import codecs

with codecs.open('frontend/case_detail.html', 'r', 'utf-8') as f:
    content = f.read()

idx = content.find('<script src="js/store.js"></script>')
if idx != -1:
    new_script = """<script src="js/api.js"></script>
  <script src="js/utils.js"></script>
  <script>
    let currentCase = null;

    document.addEventListener('DOMContentLoaded', async () => {
      if (!Utils.requireAuth()) return;
      const user = API.getUser();
      document.getElementById('user-greeting').textContent = '👤 ' + user.name;

      const params = new URLSearchParams(window.location.search);
      const caseId = params.get('id');
      if (!caseId) { window.location.href = 'dashboard.html'; return; }

      await loadCaseData(caseId);
    });

    async function loadCaseData(caseId) {
      try {
        currentCase = await API.getCase(caseId);
        document.title = currentCase.title + ' – Pocket Lawyer';
        renderCaseHeader();
        renderTimeline();
        renderDocuments();
        renderHearings();
        renderNotes();
      } catch (err) {
        Utils.showToast('Error loading case: ' + err.message, 'error');
        setTimeout(() => window.location.href = 'dashboard.html', 1500);
      }
    }

    function renderCaseHeader() {
      const c = currentCase;
      document.getElementById('case-header').innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:start;flex-wrap:wrap;gap:16px;">
          <div>
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
              <span style="font-size:1.5rem;">${Utils.getCaseTypeIcon(c.case_type)}</span>
              <h1>${Utils.escapeHtml(c.title)}</h1>
            </div>
            <p style="color:var(--text-secondary);max-width:600px;">${Utils.escapeHtml(c.description)}</p>
          </div>
          <div style="display:flex;gap:8px;flex-wrap:wrap;">
            <span class="badge badge-${Utils.statusColors[c.status] || 'neutral'}">${(c.status || 'unknown').toUpperCase()}</span>
            ${Utils.getRiskBadge(c.risk_level)}
          </div>
        </div>
        <div class="case-detail-meta">
          <div class="meta-item">📋 ${Utils.getCaseTypeLabel(c.case_type)}</div>
          <div class="meta-item">📅 Created ${Utils.formatDate(c.created_at)}</div>
          <div class="meta-item">👤 ${c.lawyer_id ? 'Lawyer Assigned' : 'No lawyer assigned'}</div>
          <div class="meta-item">📂 ${c.documents?.length || 0} documents</div>
        </div>
      `;
    }

    function switchTab(tab) {
      document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
      document.getElementById('tab-' + tab)?.classList.add('active');
      event.target.classList.add('active');
    }

    function renderTimeline() {
      const el = document.getElementById('tab-timeline');
      const events = currentCase.timeline || [];
      if (events.length === 0) {
        el.innerHTML = '<div class="empty-state"><div class="empty-icon">📅</div><h3>No events yet</h3><p>Case events will appear here as your case progresses.</p></div>';
        return;
      }
      el.innerHTML = `<div class="timeline">${events.map(ev => `
        <div class="timeline-item">
          <div class="timeline-dot"></div>
          <div class="timeline-content">
            <h4>${Utils.escapeHtml(ev.title)}</h4>
            <p>${Utils.escapeHtml(ev.description || '')}</p>
            <div class="timeline-date">${Utils.formatDateTime(ev.created_at)}</div>
          </div>
        </div>
      `).join('')}</div>`;
    }

    function renderDocuments() {
      const el = document.getElementById('tab-documents');
      const docs = currentCase.documents || [];
      el.innerHTML = `
        <div style="margin-bottom:16px;">
          <button class="btn btn-primary btn-sm" onclick="uploadDocument()">📎 Upload Document</button>
        </div>
        ${docs.length === 0 ? '<div class="empty-state"><div class="empty-icon">📂</div><h3>No documents</h3><p>Upload legal documents related to this case.</p></div>' :
        '<div class="doc-list">' + docs.map(d => `
          <div class="doc-item">
            <div class="doc-icon">📄</div>
            <div class="doc-info">
              <h4>${Utils.escapeHtml(d.filename)}</h4>
              <p>${Utils.formatFileSize(d.file_size)} · Uploaded ${Utils.formatDate(d.uploaded_at)}</p>
            </div>
            ${d.risk_analysis ? '<div style="margin-left:auto">' + Utils.getRiskBadge(JSON.parse(d.risk_analysis)?.overallRisk || 'medium') + '</div>' : ''}
          </div>
        `).join('') + '</div>'}
      `;
    }

    function uploadDocument() {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = '.pdf,.doc,.docx,.txt';
      input.onchange = async (e) => {
        if (!e.target.files.length) return;
        Utils.showToast('Uploading and analyzing document...', 'info');
        try {
          await API.uploadDocument(currentCase.id, e.target.files[0]);
          Utils.showToast('Document uploaded successfully!', 'success');
          await loadCaseData(currentCase.id);
        } catch (err) {
          Utils.showToast('Upload failed: ' + err.message, 'error');
        }
      };
      input.click();
    }

    function renderHearings() {
      const el = document.getElementById('tab-hearings');
      const hearings = currentCase.hearings || [];
      el.innerHTML = `
        <div style="margin-bottom:16px;">
          <button class="btn btn-primary btn-sm" onclick="Utils.showToast('Coming soon: Create hearing API endpoint', 'info')">📅 Add Hearing</button>
        </div>
        ${hearings.length === 0 ? '<div class="empty-state"><div class="empty-icon">⚖️</div><h3>No hearings scheduled</h3><p>Add upcoming hearing dates to keep track of court appearances.</p></div>' :
        '<div class="doc-list">' + hearings.map(h => `
          <div class="doc-item">
            <div class="doc-icon">⚖️</div>
            <div class="doc-info">
              <h4>${Utils.formatDateTime(h.hearing_date)}</h4>
              <p>${Utils.escapeHtml(h.court || 'Location TBD')} · ${Utils.escapeHtml(h.notes || '')}</p>
            </div>
          </div>
        `).join('') + '</div>'}
      `;
    }

    function renderNotes() {
      const el = document.getElementById('tab-notes');
      const notes = currentCase.notes || [];
      el.innerHTML = `
        <div style="margin-bottom:16px;">
          <form onsubmit="addNote(event)" style="display:flex;gap:12px;">
            <input type="text" id="note-input" class="form-input" placeholder="Add a note..." style="flex:1;" required>
            <button type="submit" class="btn btn-primary btn-sm">Add Note</button>
          </form>
        </div>
        ${notes.length === 0 ? '<div class="empty-state"><div class="empty-icon">📝</div><h3>No notes yet</h3><p>Add notes to keep track of important details.</p></div>' :
        '<div class="doc-list">' + notes.map(n => `
          <div class="doc-item">
            <div class="doc-icon">📝</div>
            <div class="doc-info">
              <h4>${Utils.escapeHtml(n.content)}</h4>
              <p>${Utils.formatDateTime(n.created_at)} · by ${Utils.escapeHtml(n.author_name || 'Unknown')}</p>
            </div>
          </div>
        `).join('') + '</div>'}
      `;
    }

    async function addNote(e) {
      e.preventDefault();
      const input = document.getElementById('note-input');
      const content = input.value;
      input.disabled = true;
      try {
        await API.addNote(currentCase.id, content, null);
        Utils.showToast('Note added!', 'success');
        await loadCaseData(currentCase.id);
        document.getElementById('note-input').value = '';
      } catch (err) {
        Utils.showToast('Failed to add note: ' + err.message, 'error');
      } finally {
        document.getElementById('note-input').disabled = false;
      }
    }

    function closeModal() { document.getElementById('modal-overlay').classList.add('hidden'); }
  </script>
</body>
</html>
"""
    content = content[:idx] + new_script
    with codecs.open('frontend/case_detail.html', 'w', 'utf-8') as f:
        f.write(content)
