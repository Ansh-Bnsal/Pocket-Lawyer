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

async function loadSessions(caseIdFilter = null) {
    if (!API.isLoggedIn()) return;
    try {
        const url = caseIdFilter ? `/chat/sessions?case_id=${caseIdFilter}` : '/chat/sessions';
        const sessions = await API.get(url);
        const listEl = document.getElementById('conv-list');
        if (listEl) {
            listEl.innerHTML = sessions.map(s => `
                <div class="conv-item ${s.id === activeSessionId ? 'active' : ''}" onclick="loadSessionMessages(${s.id})">
                    <h4>${s.title}</h4>
                    <span style="font-size:0.7rem; color:var(--text-muted); opacity:0.7;">Case #${s.case_id || 'N/A'}</span>
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

// ----------------------------------------------------------------------------
// 🚀 NETWORKING UTILITIES (Karpathy Style - Resilient Connection)
// ----------------------------------------------------------------------------
async function fetchWithRetry(url, options, retries = 3, backoff = 1000) {
    try {
        const response = await fetch(url, options);
        // If it's a 5xx error, it's worth retrying
        if (!response.ok && response.status >= 500 && retries > 0) throw new Error(`HTTP ${response.status}`);
        return response;
    } catch (err) {
        if (retries <= 0) throw err;
        console.warn(`Fetch failed [${err.message}]. Retrying in ${backoff}ms... (${retries} left)`);
        await new Promise(res => setTimeout(res, backoff));
        return fetchWithRetry(url, options, retries - 1, backoff * 2);
    }
}

// ----------------------------------------------------------------------------
// 🧠 TRANSIENT STORAGE MANAGER (Karpathy Style - Stage 1 Sandbox)
// ----------------------------------------------------------------------------
const TransientManager = {
    getHistory() {
        return JSON.parse(sessionStorage.getItem('transient_chat') || '[]');
    },
    addMessage(role, content) {
        const history = this.getHistory();
        history.push({ role, content, timestamp: new Date().toISOString() });
        sessionStorage.setItem('transient_chat', JSON.stringify(history));
    },
    addIntent(data) {
        const history = this.getHistory();
        history.push({ role: 'intent', data: data, timestamp: new Date().toISOString() });
        sessionStorage.setItem('transient_chat', JSON.stringify(history));
    },
    clear() {
        sessionStorage.removeItem('transient_chat');
    }
};

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
    messagesEl.insertAdjacentHTML('beforeend', renderMessage('user', userDisplay));
    
    // Track in transient sandbox if not a permanent session
    if (!activeSessionId) {
        TransientManager.addMessage('user', userDisplay);
    }
    
    // 2. PREPARE MULTIPART DATA
    const formData = new FormData();
    formData.append('message', text);
    if (activeSessionId) formData.append('sessionId', activeSessionId);
    if (selectedFile) formData.append('file', selectedFile);
    
    // Memory Continuity: Send history if this is a transient chat
    if (!activeSessionId) {
        formData.append('history', JSON.stringify(TransientManager.getHistory()));
    }

    // Clear input and preview
    input.value = '';
    input.style.height = 'auto';
    const currentFile = selectedFile;
    clearFile();

    // 3. SHOW TYPING INDICATOR
    const typingId = 'typing-' + Date.now();
    const bubbleId = 'bubble-' + Date.now();
    messagesEl.insertAdjacentHTML('beforeend', `<div class="chat-message ai" id="${typingId}"><div class="chat-avatar">🧠</div><div class="chat-bubble" id="${bubbleId}"><div class="typing-indicator"><span></span><span></span><span></span></div></div></div>`);
    messagesEl.scrollTop = messagesEl.scrollHeight;

    // Auto-Binding: Always send the current caseId if we are on a case page
    const urlParams = new URLSearchParams(window.location.search);
    const caseId = urlParams.get('id') || null;

    try {
        // 🚀 SIMPLE REQUEST PROTOCOL (Restored from Verified-Stable)
        const response = await fetch(API_BASE + '/chat', {
            method: 'POST',
            headers: { 
                'Authorization': `Bearer ${API.getToken()}`
            },
            body: formData
        });

        if (!response.ok) {
            if (response.status === 429) throw new Error('api_limit_exhausted');
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.details || `Engine Error: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let aiText = "";
        let pendingPromotion = null;
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
                        } else if (currentEvent === 'error') {
                            const errorMap = {
                                'api_limit': "I am currently reviewing a high volume of legal documents. Please give me a moment and try again. (Code: 429)",
                                'engine_error': "We are experiencing a minor technical delay in routing your query. Please refresh and try again. (Code: 500)",
                                'default': "An intermittent connection glitch occurred. Please securely resubmit your request. (Code: 0)"
                            };
                            
                            const friendlyMsg = errorMap[data.type] || errorMap['default'];
                            const errorBubble = document.getElementById(bubbleId);
                            if (errorBubble) {
                                errorBubble.innerHTML = `
                                    <div style="color:var(--text-primary); border:1px solid var(--border-color); padding:16px; border-radius:12px; background:rgba(var(--primary-rgb), 0.03); display:flex; flex-direction:column; gap:12px;">
                                        <div style="display:flex; align-items:center; gap:10px;">
                                            <span style="font-size:1.2rem;">⚖️</span>
                                            <strong style="color:var(--primary-color);">System Notice</strong>
                                        </div>
                                        <p style="font-size:0.9rem; margin:0; line-height:1.5;">${friendlyMsg}</p>
                                        <button class="btn btn-primary btn-sm" style="width:fit-content;" onclick="location.reload()">Refresh Engine</button>
                                    </div>`;
                            }
                            return; // Stop processing 
                        } else if (currentEvent === 'document') {
                            renderDocumentAnalysis(data, messagesEl);
                            messagesEl.scrollTop = messagesEl.scrollHeight;
                        } else if (currentEvent === 'intent') {
                            renderIntentAction(data, messagesEl);
                            if (!activeSessionId) {
                                TransientManager.addIntent(data);
                                if (data.is_case_worthy) pendingPromotion = data;
                            }
                            messagesEl.scrollTop = messagesEl.scrollHeight;
                        } else if (currentEvent === 'message') {
                            if (data.text) {
                                aiText += data.text;
                                const bEl = document.getElementById(bubbleId);
                                if (bEl) {
                                    bEl.innerHTML = aiText.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                                }
                                messagesEl.scrollTop = messagesEl.scrollHeight;
                            }
                        }
                    } catch(e) { } 
                }
            }
        }
        
        // Final cleanup (Typing indicator was natively overwritten by incoming text)

        
        if (!activeSessionId) {
            TransientManager.addMessage('ai', aiText);
            
            console.log("🚀 [GHOST-PROMOTION CHECKPOINT] pendingPromotion state:", pendingPromotion);
            
            // Execute Ghost-Promotion now that history is complete
            if (pendingPromotion) {
                console.log("🎯 [GHOST-PROMOTION] FIRING handlePromotion() now!");
                handlePromotion(pendingPromotion.case_reasoning || pendingPromotion.title || 'Legal Matter');
            } else {
                console.warn("⚠️ [GHOST-PROMOTION] Did NOT fire because pendingPromotion is null/undefined");
            }
        }
        
        loadSessions(); // Update history sidebar after conversation completes
    } catch (err) {
        document.getElementById(typingId)?.remove();
        
        // 🏛️ CLEAN-GLASS CATCH (Professional Shield)
        const errorMap = {
            'api_limit_exhausted': "I am currently reviewing a high volume of legal documents. Please give me a moment and try again. (Code: 429)",
            'engine_busy': "The engine is performing multiple legal analyses simultaneously. Please wait a moment. (Code: 409)",
            'default': "There was a momentary system interruption. Please refresh to continue. (Code: 500)"
        };
        
        const friendlyMsg = errorMap[err.message] || errorMap['default'];
        
        const fallbackMsg = `
            <div class="chat-message ai">
                <div class="chat-avatar">🧠</div>
                <div class="chat-bubble" style="border:1px solid var(--border-color); background:rgba(var(--primary-rgb),0.02); padding:16px;">
                    <strong style="color:var(--primary-color);">System Notice</strong>
                    <p style="font-size:0.9rem; margin:8px 0 0 0;">${friendlyMsg}</p>
                </div>
            </div>`;
        messagesEl.insertAdjacentHTML('beforeend', fallbackMsg);
        console.error("[Opaque Net Error]", err);
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
    container.insertAdjacentHTML('beforeend', html);
}

function renderIntentAction(data, container) {
    // 🏛️ AUTO CASE PROMOTER (Ghost-Promotion flagged — executed after text loop)
    if (data.is_case_worthy && !activeSessionId) {
        Utils.showToast("Legal matter detected. Securing conversation...", "info");
        // No immediate handlePromotion here, let the read() loop finish first
    }

    if (!data.next_step || !data.title) return;
    
    // Choose an icon and subtitle based on intent
    let icon = '⚖️';
    let subtitle = `Direct access to ${data.next_step.toUpperCase()} drafting.`;
    
    if (data.next_step === 'esign') { icon = '✍️'; subtitle = 'Direct access to document execution.'; }
    else if (data.next_step === 'estamp') { icon = '📜'; subtitle = 'Direct access to stamp paper acquisition.'; }
    else if (data.next_step === 'rent_agreement') { icon = '🏠'; subtitle = 'Direct access to 11-Month drafting.'; }
    else if (data.next_step === 'lawyer_appointment') { icon = '📅'; subtitle = 'Schedule a professional consultation.'; }
    else if (data.next_step === 'affidavit') { icon = '⚖️'; subtitle = 'Direct access to Sworn Affidavit drafting.'; }
    else if (data.next_step === 'kyc') { icon = '📹'; subtitle = 'Direct access to ID verification.'; }
    else if (data.next_step === 'legal_notice') { icon = '📨'; subtitle = 'Draft a formal legal notice for your dispute.'; }
    else if (data.next_step === 'will') { icon = '📝'; subtitle = 'Create your Last Will & Testament.'; }
    else if (data.next_step === 'nda') { icon = '🔒'; subtitle = 'Protect your business with an NDA.'; }
    else if (data.next_step === 'gift_deed') { icon = '🎁'; subtitle = 'Transfer assets through a legal gift deed.'; }
    else if (data.next_step === 'employment_contract') { icon = '💼'; subtitle = 'Draft a professional employment agreement.'; }
    
    const aiDataStr = JSON.stringify(data.extracted_data || {}).replace(/"/g, '&quot;');
    
    const html = `
        <div class="chat-message ai">
            <div class="chat-avatar">🧠</div>
            <div class="chat-bubble action-bar-bubble" style="width:100%; max-width:550px; padding:0; overflow:hidden; border:1px solid var(--primary-color);">
                <div class="smart-tab-card" onclick="SharedServices.openServiceModal('${data.next_step}', ${aiDataStr})" style="cursor:pointer; background:var(--bg-glass); transition:0.2s;">
                    <div style="padding:16px; border-bottom:1px solid rgba(var(--primary-rgb), 0.1); display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:0.7rem; font-weight:800; color:var(--primary-color); text-transform:uppercase; letter-spacing:1px;">AI Suggested Service</span>
                    </div>
                    <div class="action-bar-info" style="padding:20px; display:flex; gap:16px;">
                        <div class="action-bar-icon" style="background:var(--primary-color); border-radius:50%; width:40px; height:40px; display:flex; align-items:center; justify-content:center; font-size:1.2rem; flex-shrink:0;">${icon}</div>
                        <div>
                            <h4 style="margin:0 0 4px 0;">${data.title}</h4>
                            <p style="margin:0; font-size:0.8rem; color:var(--text-secondary);">${subtitle}</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    container.insertAdjacentHTML('beforeend', html);
}

async function handlePromotion(title) {
    const history = TransientManager.getHistory();
    if (history.length === 0) return;

    try {
        const res = await API.post('/chat/promote', {
            title: title,
            history: history
        });
        
        if (res.caseId) {
            TransientManager.clear();
            activeSessionId = res.sessionId;
            Utils.showToast("Case #" + res.caseId + " created", "success");
            
            // INDISPUTABLE UI FEEDBACK FOR USER
            const messagesEl = document.getElementById('chat-messages');
            if (messagesEl) {
                const headerHtml = `
                    <div style="margin: 24px 0; padding: 20px; background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; text-align: center;">
                        <div style="font-size: 2rem; margin-bottom: 8px;">✅</div>
                        <h4 style="color: #10b981; margin: 0 0 8px 0; font-size: 1.1rem;">Official Case Automatically Created</h4>
                        <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 0;">Case ID: #${res.caseId} &bull; ${title}</p>
                        <p style="color: var(--text-secondary); font-size: 0.8rem; margin: 8px 0 0 0;">This case is now permanently saved to your Dashboard and Vault.</p>
                    </div>
                `;
                messagesEl.insertAdjacentHTML('beforeend', headerHtml);
                messagesEl.scrollTop = messagesEl.scrollHeight;
            }
            
            loadSessions();
        }
    } catch (err) {
        console.error("[Promotion Error]", err);
        Utils.showToast("Could not secure conversation. Will retry on next message.", "error");
    }
}
