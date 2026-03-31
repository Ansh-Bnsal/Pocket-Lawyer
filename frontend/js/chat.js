/* ============================================
   POCKET LAWYER 2.0 — AI Chat Logic
   Real AI responses via Flask API. No fake keyword matching.
   ============================================ */

let activeSessionId = null;

document.addEventListener('DOMContentLoaded', async () => {
  autoResizeInput();
  await loadSessions();

  // Update auth button
  if (API.isLoggedIn()) {
    const btn = document.getElementById('nav-auth-btn');
    if (btn) {
      btn.textContent = '📊 Dashboard';
      const user = API.getUser();
      btn.href = user.role === 'lawyer' ? 'lawyer_dashboard.html' : user.role === 'firm' ? 'firm_dashboard.html' : 'dashboard.html';
    }
  }
});

function autoResizeInput() {
  const input = document.getElementById('chat-input');
  if (!input) return;
  input.addEventListener('input', () => {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 120) + 'px';
  });
}

function handleChatKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

async function loadSessions() {
  const list = document.getElementById('conv-list');
  if (!list) return;

  if (!API.isLoggedIn()) {
    list.innerHTML = '<p style="color:var(--text-muted);font-size:0.82rem;padding:12px;text-align:center;">Sign in to save your conversations.</p>';
    return;
  }

  try {
    const sessions = await API.getChatSessions();
    if (sessions.length === 0) {
      list.innerHTML = '<p style="color:var(--text-muted);font-size:0.82rem;padding:12px;text-align:center;">No conversations yet. Start by describing your legal issue.</p>';
      return;
    }
    list.innerHTML = sessions.map(s => `
      <div class="conv-item ${s.id === activeSessionId ? 'active' : ''}" onclick="loadSession(${s.id})">
        <h4>${Utils.escapeHtml(s.title)}</h4>
        <p>${Utils.timeAgo(s.updated_at)}</p>
      </div>
    `).join('');
  } catch (err) {
    list.innerHTML = '<p style="color:var(--text-muted);font-size:0.82rem;padding:12px;text-align:center;">Could not load sessions.</p>';
  }
}

function newConversation() {
  activeSessionId = null;
  const messagesEl = document.getElementById('chat-messages');
  messagesEl.innerHTML = `
    <div class="chat-message ai">
      <div class="chat-avatar">🧠</div>
      <div class="chat-bubble">
        <strong>New conversation started!</strong><br><br>
        Describe your legal issue and I'll analyze it with AI to provide:<br>
        • <strong>Legal classification</strong> of your situation<br>
        • <strong>Risk assessment</strong> with severity levels<br>
        • <strong>Your legal rights</strong> in this situation<br>
        • <strong>Step-by-step action plan</strong><br><br>
        <em style="color:var(--text-muted);font-size:0.85rem;">Powered by real AI — not keyword matching.</em>
      </div>
    </div>
  `;
  loadSessions();
}

async function loadSession(id) {
  activeSessionId = id;
  const messagesEl = document.getElementById('chat-messages');

  try {
    const data = await API.getChatSession(id);
    messagesEl.innerHTML = data.messages.map(m => renderMessage(m.role, m.content)).join('');
    messagesEl.scrollTop = messagesEl.scrollHeight;
  } catch (err) {
    Utils.showToast('Failed to load session', 'error');
  }
  loadSessions();
}

function renderMessage(role, content) {
  if (role === 'user') {
    return `<div class="chat-message user"><div class="chat-avatar">👤</div><div class="chat-bubble">${Utils.escapeHtml(content)}</div></div>`;
  } else {
    // AI messages may contain formatted text with line breaks
    const formatted = content.replace(/\n/g, '<br>');
    return `<div class="chat-message ai"><div class="chat-avatar">🧠</div><div class="chat-bubble">${formatted}</div></div>`;
  }
}

async function sendMessage() {
  const input = document.getElementById('chat-input');
  const text = input.value.trim();
  if (!text) return;

  if (!API.isLoggedIn()) {
    Utils.showToast('Please sign in to use the AI assistant', 'error');
    return;
  }

  const messagesEl = document.getElementById('chat-messages');

  // Show user message immediately
  messagesEl.innerHTML += renderMessage('user', text);
  input.value = '';
  input.style.height = 'auto';

  // Show typing indicator
  messagesEl.innerHTML += `<div class="chat-message ai" id="typing-msg"><div class="chat-avatar">🧠</div><div class="chat-bubble"><div class="typing-indicator"><span></span><span></span><span></span></div></div></div>`;
  messagesEl.scrollTop = messagesEl.scrollHeight;

  // Disable send button
  const sendBtn = document.getElementById('send-btn');
  if (sendBtn) sendBtn.disabled = true;

  try {
    const result = await API.sendChat(text, activeSessionId);
    activeSessionId = result.sessionId;

    // Remove typing indicator and show response
    document.getElementById('typing-msg')?.remove();
    messagesEl.innerHTML += renderMessage('ai', result.response);
    messagesEl.scrollTop = messagesEl.scrollHeight;

    await loadSessions();
  } catch (err) {
    document.getElementById('typing-msg')?.remove();
    messagesEl.innerHTML += renderMessage('ai', '❌ Error: ' + err.message + '. Please try again.');
    messagesEl.scrollTop = messagesEl.scrollHeight;
  } finally {
    if (sendBtn) sendBtn.disabled = false;
  }
}

function toggleChatSidebar() {
  document.getElementById('chat-sidebar')?.classList.toggle('open');
}
