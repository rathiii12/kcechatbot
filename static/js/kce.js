// Chat page: bubbles, typing dots, Markdown replies, POST /chat, history kept for this tab.
(function () {
  var log = document.getElementById('log');
  var form = document.getElementById('askForm');
  var input = document.getElementById('q');
  var sendBtn = document.getElementById('send');
  var chips = document.getElementById('suggest');
  var clearBtn = document.getElementById('clear');
  var KEY = 'kce-chat';
  var WELCOME = "Hi! I'm KCE AI Assistant 👋\nAsk me anything about courses, departments, admissions, hostel or placements.";
  var hist = [];
  try { hist = JSON.parse(sessionStorage.getItem(KEY) || '[]'); } catch (e) {}

  function save() { try { sessionStorage.setItem(KEY, JSON.stringify(hist.slice(-40))); } catch (e) {} }
  function now() { return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }); }
  function toBottom() { log.scrollTo({ top: log.scrollHeight, behavior: 'smooth' }); }

  function fill(bubble, who, text) {
    if (who === 'bot' && window.marked && window.DOMPurify) {
      bubble.innerHTML = DOMPurify.sanitize(marked.parse(text, { breaks: true }));
    } else {
      bubble.textContent = text;
      if (who === 'bot') bubble.style.whiteSpace = 'pre-line';
    }
  }

  function turn(who) {
    var t = document.createElement('div'); t.className = 'turn ' + who;
    if (who === 'bot') { var a = document.createElement('div'); a.className = 'av'; a.textContent = '🤖'; t.appendChild(a); }
    var col = document.createElement('div'); col.className = 'col';
    var bubble = document.createElement('div'); bubble.className = 'bubble';
    col.appendChild(bubble); t.appendChild(col); log.appendChild(t);
    return { turn: t, col: col, bubble: bubble };
  }

  function add(who, text, ts) {
    var m = turn(who);
    fill(m.bubble, who, text);
    var time = document.createElement('span'); time.className = 'time'; time.textContent = ts || now();
    m.col.appendChild(time);
    toBottom();
    return m;
  }

  function typing() {
    var m = turn('bot');
    m.bubble.innerHTML = '<span class="dots"><i></i><i></i><i></i></span>';
    toBottom();
    return m.turn;
  }

  async function ask(text) {
    text = (text || '').trim();
    if (!text) return;
    chips.hidden = true;
    var ts = now();
    add('me', text, ts); hist.push({ who: 'me', text: text, ts: ts });
    var dots = typing();
    input.disabled = true; sendBtn.disabled = true;
    var reply;
    try {
      var ctrl = new AbortController();
      var timer = setTimeout(function () { ctrl.abort(); }, 90000);
      var r = await fetch('/chat', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }), signal: ctrl.signal
      });
      clearTimeout(timer);
      if (!r.ok) throw new Error('HTTP ' + r.status);
      reply = (await r.json()).reply;
    } catch (e) {
      reply = 'Sorry, I could not reach the server. Please try again.';
    }
    dots.remove();
    ts = now();
    add('bot', reply, ts); hist.push({ who: 'bot', text: reply, ts: ts }); save();
    input.disabled = false; sendBtn.disabled = false; input.focus();
  }

  // restore this tab's conversation, or greet
  if (hist.length) {
    chips.hidden = true;
    hist.forEach(function (m) { add(m.who, m.text, m.ts); });
  } else {
    add('bot', WELCOME);
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var v = input.value; input.value = ''; ask(v);
  });
  document.querySelectorAll('[data-q]').forEach(function (b) {
    b.addEventListener('click', function () { ask(b.dataset.q); });
  });
  clearBtn.addEventListener('click', function () {
    hist = []; try { sessionStorage.removeItem(KEY); } catch (e) {}
    log.innerHTML = ''; chips.hidden = false; add('bot', WELCOME); input.focus();
  });

  // Landing tiles link here as /chat?q=Tell me about admissions
  var q = new URLSearchParams(location.search).get('q');
  if (q) { history.replaceState(null, '', location.pathname); ask(q); }
  else { input.focus(); }
})();