// ===== Configuration =====
const API_BASE_URL = 'http://localhost:8000/api/v1/chat';
const DEMO_TOKEN = 'demo-token-12345'; // Mock token for demo

// ===== State =====
let currentConversationId = null;
let conversations = [];
let selectedFile = null;
let feedbackMessageId = null;
let feedbackAnswered = null;
let feedbackSolved = null;

// ===== Initialize =====
document.addEventListener('DOMContentLoaded', () => {
    loadConversations();
});

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
        // Show empty state - this is fine for new users
    }
}

function renderConversationList() {
    const list = document.getElementById('conversation-list');
    
    if (conversations.length === 0) {
        list.innerHTML = `
            <div class="empty-state" style="padding: 20px; text-align: center; color: var(--text-light); font-size: 13px;">
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
        showLoading();
        const data = await apiRequest(`/conversations/${conversationId}`);
        
        currentConversationId = conversationId;
        
        // Update header
        document.getElementById('current-chat-title').textContent = data.title || 'Conversation';
        updateStatusBadge(data.status);
        
        // Render messages
        renderMessages(data.messages || []);
        
        // Update sidebar
        renderConversationList();
        
        // Hide welcome message
        document.getElementById('welcome-message').style.display = 'none';
        
    } catch (error) {
        showToast('Could not load conversation', 'error');
    }
}

function startNewConversation() {
    currentConversationId = null;
    
    // Reset UI
    document.getElementById('current-chat-title').textContent = 'New Conversation';
    updateStatusBadge('active');
    document.getElementById('messages').innerHTML = '';
    document.getElementById('welcome-message').style.display = 'block';
    
    // Clear input
    document.getElementById('message-input').value = '';
    removeAttachment();
    
    // Update sidebar
    renderConversationList();
}

// ===== Message Functions =====
async function sendMessage() {
    const input = document.getElementById('message-input');
    const text = input.value.trim();
    
    if (!text) return;
    
    // Disable send button
    const sendBtn = document.getElementById('send-btn');
    sendBtn.disabled = true;
    
    // Hide welcome message
    document.getElementById('welcome-message').style.display = 'none';
    
    // Add user message to UI immediately
    addMessageToUI({
        role: 'user',
        content: text,
        timestamp: new Date().toISOString(),
        has_screenshot: !!selectedFile
    });
    
    // Clear input
    input.value = '';
    autoResize(input);
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Prepare form data
        const formData = new FormData();
        formData.append('query_text', text);
        
        if (selectedFile) {
            formData.append('screenshot', selectedFile);
        }
        
        // Determine endpoint
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
        
        // Update conversation ID if new
        if (!currentConversationId) {
            currentConversationId = data.conversation_id;
            loadConversations(); // Refresh sidebar
        }
        
        // Hide typing indicator
        hideTypingIndicator();
        
        // Add assistant response
        addMessageToUI({
            message_id: data.message_id,
            role: 'assistant',
            content: data.content,
            timestamp: data.timestamp,
            documentation_links: data.documentation_links || []
        });
        
        // Update header
        document.getElementById('current-chat-title').textContent = 
            text.substring(0, 50) + (text.length > 50 ? '...' : '');
        
        // Clear attachment
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
                    ${hasFeedback ? 'Feedback Submitted' : 'Give Feedback'}
                </button>
            </div>
        `;
    }
    
    const messageHtml = `
        <div class="message ${isUser ? 'user' : 'assistant'}">
            <div class="message-avatar">
                ${isUser ? '<i class="fas fa-user"></i>' : '🏰'}
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
    
    // Validate file type
    if (!['image/jpeg', 'image/png'].includes(file.type)) {
        showToast('Only JPEG and PNG images are allowed', 'error');
        return;
    }
    
    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
        showToast('File size must be less than 5MB', 'error');
        return;
    }
    
    selectedFile = file;
    
    // Show preview
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
    
    // Reset UI
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
        
        // Update the feedback button in UI
        const feedbackBtns = document.querySelectorAll('.feedback-btn-small');
        feedbackBtns.forEach(btn => {
            if (btn.onclick.toString().includes(feedbackMessageId)) {
                btn.classList.add('submitted');
                btn.innerHTML = '<i class="fas fa-check"></i> Feedback Submitted';
                btn.disabled = true;
            }
        });
        
        // If negative feedback, offer to start new conversation or escalate
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
                    showToast('Starting a new conversation...', 'success');
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
        showToast('Your conversation has been escalated to human support', 'success');
        
        // Refresh conversations
        loadConversations();
        
    } catch (error) {
        showToast('Failed to escalate conversation', 'error');
    }
}

// ===== UI Helper Functions =====
function showTypingIndicator() {
    document.getElementById('typing-indicator').classList.remove('hidden');
    scrollToBottom();
}

function hideTypingIndicator() {
    document.getElementById('typing-indicator').classList.add('hidden');
}

function showLoading() {
    // Could add a loading spinner here
}

function updateStatusBadge(status) {
    const badge = document.getElementById('chat-status');
    badge.className = `status-badge status-${status}`;
    badge.textContent = status.charAt(0).toUpperCase() + status.slice(1);
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
    container.scrollTop = container.scrollHeight;
}

function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px';
}

function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// ===== Formatting Functions =====
function formatMessageContent(content) {
    // Basic markdown-like formatting
    let formatted = escapeHtml(content);
    
    // Bold
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Code blocks
    formatted = formatted.replace(/`(.*?)`/g, '<code>$1</code>');
    
    // Line breaks
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
