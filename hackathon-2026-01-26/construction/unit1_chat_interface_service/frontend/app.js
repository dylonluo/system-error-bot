// ===== Configuration =====
const API_BASE_URL = 'http://localhost:8000/api/v1/chat';
const DEMO_TOKEN = 'demo-token-12345';

// ===== State =====
let currentConversationId = null;
let conversations = [];
let selectedFile = null;
let feedbackMessageId = null;
let feedbackAnswered = null;
let feedbackSolved = null;
let lastConfidence = 1.0;

// ===== Typing Status Messages =====
const TYPING_MESSAGES = [
    "Thinking...",
    "Searching documentation...",
    "Finding the best answer...",
    "Almost there...",
];

// ===== Initialize =====
document.addEventListener('DOMContentLoaded', () => {
    loadConversations();
    animateWelcome();
    
    // Start with panel collapsed on mobile
    if (window.innerWidth < 768) {
        document.getElementById('side-panel').classList.add('collapsed');
    }
});

// ===== Side Panel Toggle =====
function toggleSidePanel() {
    const panel = document.getElementById('side-panel');
    panel.classList.toggle('collapsed');
}

// ===== API Functions =====
async function apiRequest(endpoint, options = {}) {
    const defaultHeaders = {
        'Authorization': `Bearer ${DEMO_TOKEN}`,
    };

    const config = {
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers,
        },
    };

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({ message: 'Request failed' }));
            throw new Error(error.message || error.detail || 'Request failed');
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// ===== Conversation Functions =====
async function loadConversations() {
    try {
        const data = await apiRequest('/conversations?limit=20');
        conversations = data.conversations || [];
        renderConversationList();
    } catch (error) {
        console.log('Could not load conversations:', error.message);
    }
}

function renderConversationList() {
    const list = document.getElementById('conversation-list');
    
    if (conversations.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                No conversations yet.<br>Start a new one!
            </div>
        `;
        return;
    }

    list.innerHTML = conversations.map(conv => `
        <div class="conversation-item ${conv.conversation_id === currentConversationId ? 'active' : ''}" 
             onclick="loadConversation('${conv.conversation_id}')">
            <span class="title">${conv.title || 'New Conversation'}</span>
            <div class="meta">
                <span class="status-dot ${conv.status}"></span>
                <span>${formatDate(conv.last_message_at)}</span>
            </div>
        </div>
    `).join('');
}

async function loadConversation(conversationId) {
    try {
        const data = await apiRequest(`/conversations/${conversationId}`);
        
        currentConversationId = conversationId;
        
        document.getElementById('current-chat-title').textContent = data.title || 'Conversation';
        updateStatusBadge(data.status);
        renderMessages(data.messages || []);
        renderConversationList();
        document.getElementById('welcome-message').style.display = 'none';
        
        // Close panel on mobile after selection
        if (window.innerWidth < 768) {
            document.getElementById('side-panel').classList.add('collapsed');
        }
        
    } catch (error) {
        showToast('Could not load conversation', 'error');
    }
}

function startNewConversation() {
    currentConversationId = null;
    
    document.getElementById('current-chat-title').textContent = 'CARES';
    updateStatusBadge('active');
    document.getElementById('messages').innerHTML = '';
    document.getElementById('welcome-message').style.display = 'block';
    
    document.getElementById('message-input').value = '';
    enableChatInput();
    removeAttachment();
    renderConversationList();
    animateWelcome();
    
    // Close panel on mobile
    if (window.innerWidth < 768) {
        document.getElementById('side-panel').classList.add('collapsed');
    }
}

// ===== Message Functions =====
async function sendMessage() {
    const input = document.getElementById('message-input');
    const text = input.value.trim();
    
    if (!text) return;
    
    const sendBtn = document.getElementById('send-btn');
    sendBtn.disabled = true;
    
    document.getElementById('welcome-message').style.display = 'none';
    
    addMessageToUI({
        role: 'user',
        content: text,
        timestamp: new Date().toISOString(),
        has_screenshot: !!selectedFile
    });
    
    input.value = '';
    autoResize(input);
    showTypingIndicator();
    
    try {
        const formData = new FormData();
        formData.append('query_text', text);
        
        if (selectedFile) {
            formData.append('screenshot', selectedFile);
        }
        
        const endpoint = currentConversationId 
            ? `/conversations/${currentConversationId}/messages`
            : '/conversations/new/messages';
        
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${DEMO_TOKEN}`,
            },
            body: formData,
        });
        
        if (!response.ok) {
            throw new Error('Failed to send message');
        }
        
        const data = await response.json();
        
        if (!currentConversationId) {
            currentConversationId = data.conversation_id;
            loadConversations();
        }
        
        hideTypingIndicator();
        
        addMessageToUIEnhanced({
            message_id: data.message_id,
            role: 'assistant',
            content: data.content,
            timestamp: data.timestamp,
            documentation_links: data.documentation_links || [],
            confidence: data.confidence || 0.8,
            intent: data.intent
        }, true);
        
        document.getElementById('current-chat-title').textContent = 
            text.substring(0, 40) + (text.length > 40 ? '...' : '');
        
        removeAttachment();
        
    } catch (error) {
        hideTypingIndicator();
        showToast('Failed to send message. Please try again.', 'error');
        console.error('Send error:', error);
    } finally {
        sendBtn.disabled = false;
    }
}

function sendQuickMessage(text) {
    document.getElementById('message-input').value = text;
    sendMessage();
}

function addMessageToUI(message) {
    const container = document.getElementById('messages');
    const isUser = message.role === 'user';
    
    let screenshotHtml = '';
    if (message.has_screenshot && selectedFile) {
        screenshotHtml = `
            <div class="message-screenshot">
                <img src="${URL.createObjectURL(selectedFile)}" alt="Screenshot">
            </div>
        `;
    } else if (message.screenshot_url) {
        screenshotHtml = `
            <div class="message-screenshot">
                <img src="${message.screenshot_url}" alt="Screenshot">
            </div>
        `;
    }
    
    let docLinksHtml = '';
    if (message.documentation_links && message.documentation_links.length > 0) {
        docLinksHtml = `
            <div class="documentation-links">
                ${message.documentation_links.map(link => `
                    <a href="${link.url}" target="_blank" class="doc-link">
                        <div class="doc-link-icon">
                            <i class="fas fa-${link.format === 'pdf' ? 'file-pdf' : 'globe'}"></i>
                        </div>
                        <div class="doc-link-content">
                            <div class="doc-link-title">${escapeHtml(link.title)}</div>
                            <div class="doc-link-description">${escapeHtml(link.description)}</div>
                            <div class="doc-link-meta">
                                <span class="doc-link-badge">${link.source}</span>
                                <span class="doc-link-badge">${Math.round(link.relevance * 100)}% match</span>
                            </div>
                        </div>
                    </a>
                `).join('')}
            </div>
        `;
    }
    
    let feedbackHtml = '';
    if (!isUser && message.message_id) {
        const hasFeedback = message.feedback;
        feedbackHtml = `
            <div class="message-actions">
                <button class="feedback-btn-small ${hasFeedback ? 'submitted' : ''}" 
                        onclick="openFeedbackModal('${message.message_id}')"
                        ${hasFeedback ? 'disabled' : ''}>
                    <i class="fas fa-${hasFeedback ? 'check' : 'comment'}"></i>
                    ${hasFeedback ? 'Thanks!' : 'Feedback'}
                </button>
            </div>
        `;
    }
    
    const messageHtml = `
        <div class="message ${isUser ? 'user' : 'assistant'}">
            <div class="message-avatar ${isUser ? '' : 'cares-avatar'}">
                ${isUser ? '<i class="fas fa-user"></i>' : '<span>C</span>'}
            </div>
            <div class="message-content">
                ${screenshotHtml}
                <div class="message-bubble">${formatMessageContent(message.content)}</div>
                ${docLinksHtml}
                ${feedbackHtml}
                <span class="message-time">${formatTime(message.timestamp)}</span>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', messageHtml);
    scrollToBottom();
}

function renderMessages(messages) {
    const container = document.getElementById('messages');
    container.innerHTML = '';
    messages.forEach(msg => addMessageToUI(msg));
}


// ===== Screenshot Functions =====
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    if (!['image/jpeg', 'image/png'].includes(file.type)) {
        showToast('Only JPEG and PNG images are allowed', 'error');
        return;
    }
    
    if (file.size > 5 * 1024 * 1024) {
        showToast('File size must be less than 5MB', 'error');
        return;
    }
    
    selectedFile = file;
    
    const preview = document.getElementById('attachment-preview');
    const previewImg = document.getElementById('preview-image');
    previewImg.src = URL.createObjectURL(file);
    preview.classList.remove('hidden');
}

function removeAttachment() {
    selectedFile = null;
    document.getElementById('file-input').value = '';
    document.getElementById('attachment-preview').classList.add('hidden');
}

// ===== Feedback Functions =====
function openFeedbackModal(messageId) {
    feedbackMessageId = messageId;
    feedbackAnswered = null;
    feedbackSolved = null;
    
    document.querySelectorAll('#feedback-modal .feedback-btn').forEach(btn => {
        btn.classList.remove('selected');
    });
    document.getElementById('submit-feedback-btn').disabled = true;
    document.getElementById('feedback-modal').classList.remove('hidden');
}

function closeFeedbackModal() {
    document.getElementById('feedback-modal').classList.add('hidden');
    feedbackMessageId = null;
}

function setFeedbackAnswer(value) {
    feedbackAnswered = value;
    updateFeedbackButtons('answered', value);
    checkFeedbackComplete();
}

function setFeedbackSolved(value) {
    feedbackSolved = value;
    updateFeedbackButtons('solved', value);
    checkFeedbackComplete();
}

function updateFeedbackButtons(type, value) {
    const container = type === 'answered' 
        ? document.querySelectorAll('.feedback-question')[0]
        : document.querySelectorAll('.feedback-question')[1];
    
    container.querySelectorAll('.feedback-btn').forEach(btn => {
        const btnValue = btn.dataset.value === 'true';
        btn.classList.toggle('selected', btnValue === value);
    });
}

function checkFeedbackComplete() {
    const submitBtn = document.getElementById('submit-feedback-btn');
    submitBtn.disabled = feedbackAnswered === null || feedbackSolved === null;
}

async function submitFeedback() {
    if (!feedbackMessageId || feedbackAnswered === null || feedbackSolved === null) return;
    
    try {
        await apiRequest(`/conversations/${currentConversationId}/feedback`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message_id: feedbackMessageId,
                answered_question: feedbackAnswered,
                problem_solved: feedbackSolved
            })
        });
        
        closeFeedbackModal();
        showToast('Thank you for your feedback!', 'success');
        
        const feedbackBtns = document.querySelectorAll('.feedback-btn-small');
        feedbackBtns.forEach(btn => {
            if (btn.onclick && btn.onclick.toString().includes(feedbackMessageId)) {
                btn.classList.add('submitted');
                btn.innerHTML = '<i class="fas fa-check"></i> Thanks!';
                btn.disabled = true;
            }
        });
        
        if (!feedbackAnswered || !feedbackSolved) {
            setTimeout(() => {
                const action = confirm(
                    "We're sorry the response wasn't helpful.\n\n" +
                    "Would you like to:\n" +
                    "• Click OK to start a new conversation\n" +
                    "• Click Cancel to escalate to human support"
                );
                
                if (action) {
                    startNewConversation();
                } else {
                    escalateConversation();
                }
            }, 500);
        }
        
    } catch (error) {
        showToast('Failed to submit feedback', 'error');
    }
}

// ===== Escalation Functions =====
function escalateConversation() {
    if (!currentConversationId) {
        showToast('Please start a conversation first', 'warning');
        return;
    }
    document.getElementById('escalation-modal').classList.remove('hidden');
}

function closeEscalationModal() {
    document.getElementById('escalation-modal').classList.add('hidden');
    document.getElementById('escalation-reason').value = '';
}

async function confirmEscalation() {
    const reason = document.getElementById('escalation-reason').value.trim();
    
    try {
        await apiRequest(`/conversations/${currentConversationId}/escalate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ reason: reason || null })
        });
        
        closeEscalationModal();
        updateStatusBadge('escalated');
        addEscalationEndMessage();
        disableChatInput();
        
        showToast('Your conversation has been escalated. Support will contact you soon.', 'success');
        loadConversations();
        
    } catch (error) {
        showToast('Failed to escalate conversation', 'error');
    }
}

function addEscalationEndMessage() {
    const container = document.getElementById('messages');
    const messageHtml = `
        <div class="escalation-end-message">
            <div class="escalation-end-icon">
                <i class="fas fa-check-circle"></i>
            </div>
            <div class="escalation-end-content">
                <h4>Request Sent Successfully</h4>
                <p>Your conversation has been sent to our support team.</p>
                <p>They will contact you via email within <strong>3-5 business hours</strong>.</p>
                <p class="escalation-end-note">This chat session has ended.</p>
            </div>
            <button class="btn-new-chat" onclick="startNewConversation()">
                <i class="fas fa-plus"></i> Start New Conversation
            </button>
        </div>
    `;
    container.insertAdjacentHTML('beforeend', messageHtml);
    scrollToBottom();
}

function disableChatInput() {
    const input = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');
    const attachBtn = document.querySelector('.input-action');
    
    input.disabled = true;
    input.placeholder = 'This conversation has been escalated.';
    sendBtn.disabled = true;
    if (attachBtn) attachBtn.disabled = true;
}

function enableChatInput() {
    const input = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');
    const attachBtn = document.querySelector('.input-action');
    
    input.disabled = false;
    input.placeholder = 'Ask me anything...';
    sendBtn.disabled = false;
    if (attachBtn) attachBtn.disabled = false;
}

// ===== UI Helper Functions =====
function showTypingIndicator() {
    document.getElementById('typing-indicator').classList.remove('hidden');
    scrollToBottom();
    
    let messageIndex = 0;
    const statusEl = document.getElementById('typing-status');
    
    window.typingInterval = setInterval(() => {
        messageIndex = (messageIndex + 1) % TYPING_MESSAGES.length;
        statusEl.textContent = TYPING_MESSAGES[messageIndex];
    }, 2000);
}

function hideTypingIndicator() {
    document.getElementById('typing-indicator').classList.add('hidden');
    if (window.typingInterval) {
        clearInterval(window.typingInterval);
    }
}

function updateStatusBadge(status) {
    const badge = document.getElementById('chat-status');
    badge.className = `status-pill status-${status}`;
    
    const labels = {
        active: 'Ready to help',
        escalated: 'Escalated',
        resolved: 'Resolved'
    };
    badge.textContent = labels[status] || status;
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const icon = toast.querySelector('.toast-icon');
    const text = toast.querySelector('.toast-message');
    
    toast.className = `toast ${type}`;
    text.textContent = message;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle'
    };
    icon.className = `toast-icon fas ${icons[type] || icons.success}`;
    
    toast.classList.remove('hidden');
    
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

function scrollToBottom() {
    const container = document.getElementById('messages-container');
    setTimeout(() => {
        container.scrollTop = container.scrollHeight;
    }, 50);
}

function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}


// ===== Formatting Functions =====
function formatMessageContent(content) {
    let formatted = escapeHtml(content);
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/`(.*?)`/g, '<code>$1</code>');
    formatted = formatted.replace(/\n/g, '<br>');
    return formatted;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    if (diff < 604800000) return `${Math.floor(diff / 86400000)}d ago`;
    
    return date.toLocaleDateString();
}

function formatTime(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// ===== Enhanced UI Functions =====
function animateWelcome() {
    const cards = document.querySelectorAll('.feature-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.5s cubic-bezier(0.16, 1, 0.3, 1)';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 200 + (index * 100));
    });
}

// Confidence meter
function showConfidenceMeter(confidence) {
    lastConfidence = confidence;
    
    let level = 'high';
    let label = 'High';
    
    if (confidence < 0.5) {
        level = 'low';
        label = 'Low';
        showConfidenceWarning();
    } else if (confidence < 0.75) {
        level = 'medium';
        label = 'Medium';
    }
    
    return `
        <div class="confidence-meter">
            <span style="font-size: 11px; color: var(--taupe);">Confidence:</span>
            <div class="confidence-bar">
                <div class="confidence-fill ${level}" style="width: ${confidence * 100}%"></div>
            </div>
            <span class="confidence-label">${Math.round(confidence * 100)}%</span>
        </div>
    `;
}

function showConfidenceWarning() {
    const warning = document.getElementById('confidence-warning');
    warning.classList.remove('hidden');
    
    setTimeout(() => {
        dismissConfidenceWarning();
    }, 10000);
}

function dismissConfidenceWarning() {
    document.getElementById('confidence-warning').classList.add('hidden');
}

// Smart suggestions
function generateSuggestions(content, intent) {
    const suggestions = [];
    const contentLower = content.toLowerCase();
    
    if (contentLower.includes('error') || contentLower.includes('issue')) {
        suggestions.push({ icon: 'fa-redo', text: 'What if that doesn\'t work?' });
        suggestions.push({ icon: 'fa-info-circle', text: 'Can you explain more?' });
    }
    
    if (contentLower.includes('order') || contentLower.includes('delivery')) {
        suggestions.push({ icon: 'fa-truck', text: 'How do I track my order?' });
        suggestions.push({ icon: 'fa-clock', text: 'When will it arrive?' });
    }
    
    if (contentLower.includes('return') || contentLower.includes('refund')) {
        suggestions.push({ icon: 'fa-box', text: 'What\'s the return policy?' });
        suggestions.push({ icon: 'fa-money-bill', text: 'When will I get my refund?' });
    }
    
    if (suggestions.length === 0) {
        suggestions.push({ icon: 'fa-question-circle', text: 'Tell me more' });
        suggestions.push({ icon: 'fa-lightbulb', text: 'Any other options?' });
    }
    
    suggestions.push({ icon: 'fa-headset', text: 'Talk to a human' });
    
    return suggestions.slice(0, 3);
}

function renderSuggestions(suggestions) {
    if (!suggestions || suggestions.length === 0) return '';
    
    return `
        <div class="smart-suggestions">
            ${suggestions.map(s => `
                <button class="suggestion-chip" onclick="sendQuickMessage('${s.text}')">
                    <i class="fas ${s.icon}"></i>${s.text}
                </button>
            `).join('')}
        </div>
    `;
}

// Enhanced message with confidence and suggestions
function addMessageToUIEnhanced(message, useTypewriter = false) {
    const container = document.getElementById('messages');
    const isUser = message.role === 'user';
    
    let screenshotHtml = '';
    if (message.has_screenshot && selectedFile) {
        screenshotHtml = `
            <div class="message-screenshot">
                <img src="${URL.createObjectURL(selectedFile)}" alt="Screenshot">
            </div>
        `;
    } else if (message.screenshot_url) {
        screenshotHtml = `
            <div class="message-screenshot">
                <img src="${message.screenshot_url}" alt="Screenshot">
            </div>
        `;
    }
    
    let docLinksHtml = '';
    if (message.documentation_links && message.documentation_links.length > 0) {
        docLinksHtml = `
            <div class="documentation-links">
                ${message.documentation_links.map(link => `
                    <a href="${link.url}" target="_blank" class="doc-link">
                        <div class="doc-link-icon">
                            <i class="fas fa-${link.format === 'pdf' ? 'file-pdf' : 'globe'}"></i>
                        </div>
                        <div class="doc-link-content">
                            <div class="doc-link-title">${escapeHtml(link.title)}</div>
                            <div class="doc-link-description">${escapeHtml(link.description)}</div>
                            <div class="doc-link-meta">
                                <span class="doc-link-badge">${link.source}</span>
                                <span class="doc-link-badge">${Math.round(link.relevance * 100)}% match</span>
                            </div>
                        </div>
                    </a>
                `).join('')}
            </div>
        `;
    }
    
    let confidenceHtml = '';
    if (!isUser && message.confidence !== undefined) {
        confidenceHtml = showConfidenceMeter(message.confidence);
    }
    
    let suggestionsHtml = '';
    if (!isUser && message.content) {
        const suggestions = generateSuggestions(message.content, message.intent);
        suggestionsHtml = renderSuggestions(suggestions);
    }
    
    let feedbackHtml = '';
    if (!isUser && message.message_id) {
        feedbackHtml = `
            <div class="message-actions">
                <button class="feedback-btn-small" onclick="openFeedbackModal('${message.message_id}')">
                    <i class="fas fa-comment"></i> Feedback
                </button>
            </div>
        `;
    }
    
    const messageHtml = `
        <div class="message ${isUser ? 'user' : 'assistant'}">
            <div class="message-avatar ${isUser ? '' : 'cares-avatar'}">
                ${isUser ? '<i class="fas fa-user"></i>' : '<span>C</span>'}
            </div>
            <div class="message-content">
                ${screenshotHtml}
                <div class="message-bubble">${formatMessageContent(message.content)}</div>
                ${docLinksHtml}
                ${confidenceHtml}
                ${suggestionsHtml}
                ${feedbackHtml}
                <span class="message-time">${formatTime(message.timestamp)}</span>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', messageHtml);
    scrollToBottom();
}
