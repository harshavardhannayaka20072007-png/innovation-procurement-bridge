document.addEventListener('DOMContentLoaded', () => {
  const trigger = document.getElementById('chatbotTrigger');
  const panel = document.getElementById('chatbotPanel');
  const close = document.getElementById('chatbotClose');
  const form = document.getElementById('chatbotForm');
  const input = document.getElementById('chatbotInput');
  const messages = document.getElementById('chatbotMessages');
  const suggestions = document.getElementById('chatbotSuggestions');
  if (!trigger || !panel || !form) return;

  const role = document.body.dataset.userRole || 'user';
  const prompts = role === 'startup'
    ? ['What challenges can I apply for?', 'What is my application status?', 'What milestones need action?']
    : role === 'evaluator'
      ? ['Which applications need evaluation?', 'Which milestones need review?', 'What is pilot progress?']
      : ['Give a platform overview', 'How many applications are there?', 'Show audit ledger status'];
  const add = (text, type) => { const item = document.createElement('div'); item.className = `chatbot-message chatbot-message--${type}`; item.textContent = text; messages.appendChild(item); messages.scrollTop = messages.scrollHeight; return item; };
  const setOpen = open => { panel.hidden = !open; trigger.setAttribute('aria-expanded', String(open)); if (open) input.focus(); };
  prompts.forEach(text => { const chip = document.createElement('button'); chip.type = 'button'; chip.className = 'chatbot-chip'; chip.textContent = text; chip.addEventListener('click', () => { input.value = text; form.requestSubmit(); }); suggestions.appendChild(chip); });
  trigger.addEventListener('click', () => { setOpen(panel.hidden); if (messages.children.length === 0) add('Hello. I can help with live challenges, applications, milestones, pilots, and the audit ledger.', 'assistant'); });
  close.addEventListener('click', () => setOpen(false));
  form.addEventListener('submit', async event => {
    event.preventDefault(); const message = input.value.trim(); if (!message) return;
    add(message, 'user'); input.value = ''; const pending = add('Checking the live portal records…', 'assistant');
    try { const response = await fetch('/api/chatbot/chat', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message}) }); const data = await response.json(); pending.textContent = data.success ? data.response : (data.error || 'The assistant could not respond.'); }
    catch (_) { pending.textContent = 'The assistant is temporarily unavailable. Please try again.'; }
  });
});
