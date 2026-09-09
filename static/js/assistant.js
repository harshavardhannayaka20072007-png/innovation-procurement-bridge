document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('guideToggle');
  const panel = document.getElementById('guidePanel');
  const close = document.getElementById('guideClose');
  const form = document.getElementById('guideForm');
  const input = document.getElementById('guideInput');
  const messages = document.getElementById('guideMessages');
  if (!toggle || !panel || !form) return;

  const setOpen = (open) => { panel.hidden = !open; toggle.setAttribute('aria-expanded', String(open)); if (open) input.focus(); };
  const append = (text, type) => { const item = document.createElement('div'); item.className = `guide-message guide-message--${type}`; item.textContent = text; messages.appendChild(item); messages.scrollTop = messages.scrollHeight; return item; };
  toggle.addEventListener('click', () => setOpen(panel.hidden));
  close.addEventListener('click', () => setOpen(false));
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const message = input.value.trim();
    if (!message) return;
    append(message, 'user'); input.value = '';
    const pending = append('Checking the portal record...', 'assistant');
    try {
      const response = await fetch('/assistant/ask', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message }) });
      const data = await response.json();
      pending.textContent = data.answer || 'I could not prepare guidance right now.';
      if (data.destination) { const link = document.createElement('a'); link.className = 'guide-link'; link.href = data.destination; link.textContent = data.action_label || 'Open page'; pending.appendChild(link); }
    } catch (_) { pending.textContent = 'The guide is temporarily unavailable. Please try again.'; }
    messages.scrollTop = messages.scrollHeight;
  });
});
