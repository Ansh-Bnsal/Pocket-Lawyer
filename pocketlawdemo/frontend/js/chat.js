/* ============================================
   POCKET LAWYER 2.0 — AI Chat Logic (Refactored)
   Updated with Decoupled AI Gateway & Multimodal Support
   ============================================ */

let activeSessionId = null;
let selectedFile = null;

document.addEventListener('DOMContentLoaded', () => {
    autoResizeInput();
    loadSessions(); // Load session history instead of just local mock history
    
    if (API.isLoggedIn()) {
        const user = API.getUser();
        const greet = document.getElementById('user-greeting');
        if (greet) greet.innerText = `Hi, ${user.name}`;
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

// 📎 MULTIMODAL FILE HANDLING
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    selectedFile = file;
    document.getElementById('selected-filename').innerText = file.name;
    
    // Show file size
    const sizeKB = (file.size / 1024).toFixed(0);
    const sizeStr = sizeKB > 1024 ? (sizeKB / 1024).toFixed(1) + ' MB' : sizeKB + ' KB';
    document.getElementById('selected-filesize').innerText = `(${sizeStr})`;
    
    document.getElementById('chat-file-preview').style.display = 'flex';
    
    // Auto-focus textarea so user can type a message alongside
    document.getElementById('chat-input').focus();
}

function clearFile() {
    selectedFile = null;
    document.getElementById('chat-file-input').value = '';
    document.getElementById('chat-file-preview').style.display = 'none';
}

async function loadSessions() {
    if (!API.isLoggedIn()) return;
    try {
        const sessions = await API.get('/chat/sessions');
        const listEl = document.getElementById('conv-list');
        if (listEl) {
            listEl.innerHTML = sessions.map(s => `
                <div class="conv-item ${s.id === activeSessionId ? 'active' : ''}" onclick="loadSessionMessages(${s.id})">
                    <h4>${s.title}</h4>
                    <p>${new Date(s.updated_at).toLocaleDateString()}</p>
                </div>
            `).join('');
        }
    } catch (err) {
        console.error('Failed to load chat sessions', err);
    }
}

async function loadSessionMessages(sessionId) {
    activeSessionId = sessionId;
    const messagesEl = document.getElementById('chat-messages');
    messagesEl.innerHTML = '<div class="loading-state">Loading conversation...</div>';
    
    // Toggle active state in sidebar
    document.querySelectorAll('.conv-item').forEach(item => item.classList.remove('active'));
    
    try {
        const data = await API.get(`/chat/sessions/${sessionId}`);
        messagesEl.innerHTML = data.messages.map(m => renderMessage(m.role, m.content)).join('');
        messagesEl.scrollTop = messagesEl.scrollHeight;
        loadSessions(); // Refresh sidebar to show active
    } catch (err) {
        messagesEl.innerHTML = '<div class="error-state">Failed to load messages.</div>';
    }
}

function newConversation() {
    activeSessionId = null;
    clearFile();
    const messagesEl = document.getElementById('chat-messages');
    messagesEl.innerHTML = `
        <div class="chat-message ai">
            <div class="chat-avatar">🧠</div>
            <div class="chat-bubble">
                <strong>I'm ready to listen.</strong><br><br>
                Tell me exactly what has happened, or 📎 **attach a document** (Agreement, Notice, or Ticket) for analysis.<br><br>
                I'll identify the key legal risks and clarify your rights under Indian Law.<br><br>
                <em style="color:var(--text-muted);font-size:0.85rem;">How can I help you today?</em>
            </div>
        </div>
    `;
    document.querySelectorAll('.conv-item').forEach(item => item.classList.remove('active'));
}

function renderMessage(role, content) {
    // Basic markdown-like formatting for better readability
    let formatted = content.replace(/\n/g, '<br>');
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    const avatar = role === 'user' ? '👤' : '🧠';
    
    return `
        <div class="chat-message ${role}">
            <div class="chat-avatar">${avatar}</div>
            <div class="chat-bubble">
                ${formatted}
            </div>
        </div>`;
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    
    if (!text && !selectedFile) return;

    if (!API.isLoggedIn()) {
        Utils.showToast('Please sign in to use the AI assistant', 'error');
        return;
    }

    const messagesEl = document.getElementById('chat-messages');

    // 1. SHOW USER MESSAGE IN UI (text + file together)
    let userDisplay = text;
    if (selectedFile) {
        const fileTag = `📎 ${selectedFile.name}`;
        userDisplay = text ? `${text}\n\n${fileTag}` : fileTag;
    }
    messagesEl.innerHTML += renderMessage('user', userDisplay);
    
    // 2. PREPARE MULTIPART DATA
    const formData = new FormData();
    formData.append('message', text);
    if (activeSessionId) formData.append('sessionId', activeSessionId);
    if (selectedFile) formData.append('file', selectedFile);

    // Clear input and preview
    input.value = '';
    input.style.height = 'auto';
    const currentFile = selectedFile;
    clearFile();

    // 3. SHOW TYPING INDICATOR
    const typingId = 'typing-' + Date.now();
    messagesEl.innerHTML += `<div class="chat-message ai" id="${typingId}"><div class="chat-avatar">🧠</div><div class="chat-bubble"><div class="typing-indicator"><span></span><span></span><span></span></div></div></div>`;
    messagesEl.scrollTop = messagesEl.scrollHeight;

    try {
        const headers = {};
        const token = API.getToken();
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const response = await fetch(API_BASE + '/chat', {
            method: 'POST',
            body: formData,
            headers: headers
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        // Remove typing indicator & setup an empty bubble for streaming
        document.getElementById(typingId)?.remove();
        const bubbleId = 'ai-msg-' + Date.now();
        messagesEl.innerHTML += `<div class="chat-message ai"><div class="chat-avatar">🧠</div><div class="chat-bubble" id="${bubbleId}"></div></div>`;
        messagesEl.scrollTop = messagesEl.scrollHeight;

        const bubbleEl = document.getElementById(bubbleId);
        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let aiText = "";
        let currentEvent = 'message';

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n');
            
            for (let line of lines) {
                if (line.startsWith('event: ')) {
                    currentEvent = line.substring(7).trim();
                } else if (line.startsWith('data: ')) {
                    const payload = line.substring(6).trim();
                    if (!payload || payload === '{}') continue;
                    try {
                        const data = JSON.parse(payload);
                        if (currentEvent === 'metadata') {
                            if (data.sessionId) activeSessionId = data.sessionId;
                        } else if (currentEvent === 'document') {
                            renderDocumentAnalysis(data, messagesEl);
                            messagesEl.scrollTop = messagesEl.scrollHeight;
                        } else {
                            if (data.text) {
                                aiText += data.text;
                                let formatted = aiText.replace(/\n/g, '<br>');
                                formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                                
                                bubbleEl.innerHTML = formatted;
                                messagesEl.scrollTop = messagesEl.scrollHeight;
                            }
                        }
                    } catch(e) { } 
                }
            }
        }
        
        loadSessions(); // Update history sidebar after conversation completes
    } catch (err) {
        document.getElementById(typingId)?.remove();
        messagesEl.innerHTML += renderMessage('ai', "I'm sorry, I couldn't reach the legal engine. Please check your connection.");
    }

    messagesEl.scrollTop = messagesEl.scrollHeight;
}

function toggleChatSidebar() {
    document.getElementById('chat-sidebar')?.classList.toggle('open');
}

function renderDocumentAnalysis(data, container) {
    if (!data.harmfulClauses && !data.missingClauses) return;
    
    let html = '<div class="chat-message ai"><div class="chat-avatar">🧠</div><div class="chat-bubble doc-analysis-block" style="width:100%; max-width:650px; padding:24px; background:var(--bg-surface); border:1px solid var(--border-color); border-radius:var(--radius-lg); box-shadow:var(--shadow-sm);">';
    html += '<h4 style="margin-bottom:20px; border-bottom:1px solid var(--border-color); padding-bottom:12px; display:flex; align-items:center; gap:8px;"><span style="font-size:1.4rem;">📄</span> Document Structural Analysis</h4>';

    if (data.harmfulClauses && data.harmfulClauses.length > 0) {
        html += '<div style="margin-bottom:20px;"><strong>⚠️ Risky Clauses Found (' + data.harmfulClauses.length + '):</strong></div>';
        data.harmfulClauses.forEach(clause => {
            let color = 'var(--text-secondary)';
            let bg = 'transparent';
            let border = 'var(--border-color)';
            
            if (clause.severity === 'HIGH') { color = '#ef4444'; bg = 'rgba(239,68,68,0.05)'; border = 'rgba(239,68,68,0.2)'; }
            if (clause.severity === 'MEDIUM') { color = '#f59e0b'; bg = 'rgba(245,158,11,0.05)'; border = 'rgba(245,158,11,0.2)'; }
            if (clause.severity === 'LOW') { color = '#10b981'; bg = 'rgba(16,185,129,0.05)'; border = 'rgba(16,185,129,0.2)'; }
            
            html += `<div style="margin-bottom:16px; padding:16px; border-radius:8px; background:${bg}; border:1px solid ${border};">`;
            html += `<strong style="color:${color}; font-size:0.75rem; text-transform:uppercase; display:block; margin-bottom:8px; letter-spacing:0.5px;">${clause.severity} RISK</strong>`;
            html += `<p style="margin:0 0 12px 0; font-style:italic; font-size:0.95rem; border-left:3px solid ${color}; padding-left:12px; color:var(--text-primary); line-height:1.5;">"${clause.originalQuote}"</p>`;
            html += `<p style="margin:0 0 8px 0; font-size:0.9rem; color:var(--text-secondary);"><strong>Implication:</strong> ${clause.explanation || clause.consequence}</p>`;
            if (clause.suggestedFix) {
                html += `<p style="margin:0; font-size:0.9rem; color:#10b981;"><strong>💡 Proposed Fix:</strong> ${clause.suggestedFix}</p>`;
            }
            html += '</div>';
        });
    }

    if (data.missingClauses && data.missingClauses.length > 0) {
        html += '<div style="margin-top:24px; margin-bottom:16px;"><strong>📋 Missing Essential Clauses:</strong></div>';
        data.missingClauses.forEach(clause => {
            html += `<div style="margin-bottom:12px; padding:16px; border-radius:8px; background:var(--bg-glass); border:1px dashed var(--primary-light);">`;
            html += `<strong style="color:var(--text-primary); font-size:1rem; display:block; margin-bottom:6px;">+ ${clause.clauseName}</strong>`;
            html += `<p style="margin:0; font-size:0.9rem; color:var(--text-secondary); line-height:1.4;">${clause.reasonWhyNeeded}</p>`;
            html += '</div>';
        });
    }
    
    html += '</div></div>';
    container.innerHTML += html;
}
