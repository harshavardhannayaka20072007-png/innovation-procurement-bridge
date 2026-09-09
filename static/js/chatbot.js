/**
 * NEXORA AI Assistant Chatbot Frontend Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  const triggerBtn = document.getElementById('chatbot-trigger-btn');
  const chatPanel = document.getElementById('chatbot-panel');
  const closeBtn = document.getElementById('chatbot-close-btn');
  const clearBtn = document.getElementById('chatbot-clear-btn');
  const messageInput = document.getElementById('chatbot-input');
  const sendBtn = document.getElementById('chatbot-send-btn');
  const messagesContainer = document.getElementById('chatbot-messages');
  const suggestionsContainer = document.getElementById('chatbot-suggestions');
  const userRoleBadge = document.getElementById('chatbot-user-role-badge');

  if (!triggerBtn || !chatPanel) return;

  // Detect current session user role from HTML data attribute or element
  const currentRole = document.body.getAttribute('data-user-role') || 'guest';

  // Define Quick Suggestions by Role
  const roleSuggestions = {
    government: [
      "What challenges are currently available?",
      "Which startup has the highest readiness score?",
      "Why is one startup ranked higher than another?",
      "What is the current pilot performance?",
      "Should this pilot be considered for Scale, Improve or Stop?"
    ],
    startup: [
      "What challenges can I apply for?",
      "What is my application status?",
      "What is my readiness score?",
      "What milestones are pending?",
      "What evidence is required?"
    ],
    evaluator: [
      "Which applications need evaluation?",
      "Which startup has the strongest evaluation?",
      "Which pilot milestones need attention?",
      "What KPI results are available?"
    ],
    admin: [
      "Give an overview of platform activity.",
      "How many challenges exist?",
      "How many applications exist?",
      "How many active pilots exist?",
      "Which stages have pending work?"
    ],
    guest: [
      "What challenges are available?",
      "How does the procurement bridge work?",
      "How do startups apply?"
    ]
  };

  // Populate Role Suggestions
  function loadRoleSuggestions() {
    const list = roleSuggestions[currentRole] || roleSuggestions.guest;
    if (suggestionsContainer) {
      suggestionsContainer.innerHTML = list.map(q => 
        `<span class="suggestion-chip">${escapeHtml(q)}</span>`
      ).join('');

      // Add click event listeners to chips
      suggestionsContainer.querySelectorAll('.suggestion-chip').forEach(chip => {
        chip.addEventListener('click', () => {
          messageInput.value = chip.textContent;
          sendMessage();
        });
      });
    }

    if (userRoleBadge) {
      userRoleBadge.textContent = currentRole.toUpperCase();
    }
  }

  loadRoleSuggestions();

  // Toggle Panel Open/Close
  triggerBtn.addEventListener('click', () => {
    const isOpen = chatPanel.classList.contains('open');
    if (isOpen) {
      chatPanel.classList.remove('open');
      triggerBtn.classList.remove('active');
    } else {
      chatPanel.classList.add('open');
      triggerBtn.classList.add('active');
      messageInput.focus();
      if (messagesContainer.children.length === 0) {
        showWelcomeMessage();
      }
    }
  });

  closeBtn.addEventListener('click', () => {
    chatPanel.classList.remove('open');
    triggerBtn.classList.remove('active');
  });

  // Clear Chat History
  clearBtn.addEventListener('click', () => {
    messagesContainer.innerHTML = '';
    showWelcomeMessage();
  });

  // Send Message Triggers
  sendBtn.addEventListener('click', sendMessage);
  messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  function showWelcomeMessage() {
    const welcomeText = `Hello! I am the **NEXORA AI Assistant**. I have direct authorization to query real NEXORA application records for your active role (**${currentRole.toUpperCase()}**).\n\nHow can I help you evaluate challenges, analyze startup readiness, or check pilot progress today?`;
    appendMessage('ai', welcomeText);
  }

  async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text) return;

    // Append user message
    appendMessage('user', text);
    messageInput.value = '';
    sendBtn.disabled = true;

    // Show Typing Indicator
    showTypingIndicator();

    try {
      const response = await fetch('/api/chatbot/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });

      removeTypingIndicator();
      sendBtn.disabled = false;

      const data = await response.json();

      if (data.success) {
        appendMessage('ai', data.response);
      } else {
        appendMessage('ai', `⚠️ **Error**: ${data.error || 'Failed to process request.'}`);
      }

    } catch (err) {
      removeTypingIndicator();
      sendBtn.disabled = false;
      appendMessage('ai', `⚠️ **Network Error**: Unable to reach NEXORA AI backend service.`);
    }
  }

  function appendMessage(sender, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-message ${sender}`;

    const formattedText = parseSimpleMarkdown(text);
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    msgDiv.innerHTML = `
      <div class="chat-bubble">
        ${formattedText}
      </div>
      <div class="chat-timestamp">${timeStr}</div>
    `;

    messagesContainer.appendChild(msgDiv);
    scrollToBottom();
  }

  function showTypingIndicator() {
    const indicatorDiv = document.createElement('div');
    indicatorDiv.id = 'chatbot-typing-indicator';
    indicatorDiv.className = 'chat-message ai';
    indicatorDiv.innerHTML = `
      <div class="typing-indicator">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    `;
    messagesContainer.appendChild(indicatorDiv);
    scrollToBottom();
  }

  function removeTypingIndicator() {
    const indicator = document.getElementById('chatbot-typing-indicator');
    if (indicator) indicator.remove();
  }

  function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  function escapeHtml(string) {
    return String(string).replace(/[&<>"']/g, function(s) {
      return {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
      }[s];
    });
  }

  // Simple Markdown Parser Helper
  function parseSimpleMarkdown(md) {
    if (!md) return '';
    let html = escapeHtml(md);

    // Headers ###
    html = html.replace(/^### (.*$)/gim, '<h6 class="fw-bold mt-2 mb-1">$1</h6>');
    html = html.replace(/^## (.*$)/gim, '<h6 class="fw-bold fs-6 mt-2 mb-1">$1</h6>');

    // Bold **text**
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Italic *text*
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Blockquotes > text
    html = html.replace(/^&gt; (.*$)/gim, '<blockquote>$1</blockquote>');

    // Bullet Points - or *
    html = html.replace(/^\s*[\-\*]\s+(.*$)/gim, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/gms, '<ul class="mb-2 ps-3">$1<\/ul>');

    // Paragraph breaks
    html = html.replace(/\n\n/g, '<br><br>');
    html = html.replace(/\n/g, '<br>');

    return html;
  }
});
