const chat = document.getElementById('chat');
const form = document.getElementById('chatForm');
const input = document.getElementById('question');
const quickButtons = document.querySelectorAll('.prompt-btn');
const themeToggle = document.getElementById('themeToggle');

function applyTheme(theme) {
  document.body.setAttribute('data-theme', theme);
  localStorage.setItem('stringerai-theme', theme);

  if (theme === 'dark') {
    themeToggle.querySelector('.toggle-label').textContent = 'Light mode';
  } else {
    themeToggle.querySelector('.toggle-label').textContent = 'Dark mode';
  }
}

function initTheme() {
  const stored = localStorage.getItem('stringerai-theme');
  const preferred = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  applyTheme(stored || preferred);
}

themeToggle.addEventListener('click', () => {
  const current = document.body.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  applyTheme(current);
});

function addMessage(role, text, sources = []) {
  const wrapper = document.createElement('div');
  wrapper.className = `message-row ${role}`;

  const bubble = document.createElement('div');
  bubble.className = `message ${role}`;
  bubble.textContent = text;

  if (sources.length) {
    const sourceBox = document.createElement('div');
    sourceBox.className = 'sources';
    sourceBox.textContent = 'Sources: ' + sources.join(', ');
    bubble.appendChild(sourceBox);
  }

  wrapper.appendChild(bubble);
  chat.appendChild(wrapper);
  chat.scrollTop = chat.scrollHeight;
}

function renderWelcome() {
  addMessage(
    'bot',
    'Hi! I’m StringerAI, your WVSU assistant. Ask me about admissions, tuition, history, academics, athletics, or campus life.'
  );
}

async function askQuestion(question) {
  const trimmed = question.trim();
  if (!trimmed) return;

  addMessage('user', trimmed);
  input.value = '';

  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question: trimmed })
  });

  const data = await response.json();
  addMessage('bot', data.answer || 'I could not answer that.', data.sources || []);
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  await askQuestion(input.value);
});

quickButtons.forEach((button) => {
  button.addEventListener('click', () => askQuestion(button.dataset.question));
});

initTheme();
renderWelcome();
