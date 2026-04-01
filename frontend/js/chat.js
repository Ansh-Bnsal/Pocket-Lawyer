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
        // 4. CALL REAL API GATEWAY (Using standard API helper)
        const data = await API.postForm('/chat', formData);
        
        // Remove typing indicator
        document.getElementById(typingId)?.remove();

        if (data.error) {
            messagesEl.innerHTML += renderMessage('ai', `Error: ${data.error}`);
        } else {
            activeSessionId = data.sessionId;
            messagesEl.innerHTML += renderMessage('ai', data.response);
            loadSessions(); // Update history sidebar
        }
    } catch (err) {
        document.getElementById(typingId)?.remove();
        messagesEl.innerHTML += renderMessage('ai', "I'm sorry, I couldn't reach the legal engine. Please check your connection.");
    }

    messagesEl.scrollTop = messagesEl.scrollHeight;
}

function toggleChatSidebar() {
    document.getElementById('chat-sidebar')?.classList.toggle('open');
}
