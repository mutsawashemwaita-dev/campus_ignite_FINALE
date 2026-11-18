/* ============================================================
   CAMPUS IGNITE – Global JavaScript
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

  // ── Auto-dismiss Django messages as toasts ──────────────
  const alerts = document.querySelectorAll('.ci-auto-alert');
  alerts.forEach(function (el) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      bsAlert.close();
    }, 4500);
  });

  // ── Mark notification as read via AJAX ─────────────────
  document.querySelectorAll('.mark-read-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const url  = btn.dataset.url;
      const item = document.getElementById('notif-' + btn.dataset.id);
      fetch(url, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCsrf(), 'Content-Type': 'application/json' }
      }).then(function (r) {
        if (r.ok && item) {
          item.classList.remove('unread');
          btn.remove();
          updateBadge(-1);
        }
      });
    });
  });

  // Mark all read
  const markAllBtn = document.getElementById('mark-all-read');
  if (markAllBtn) {
    markAllBtn.addEventListener('click', function () {
      fetch(markAllBtn.dataset.url, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCsrf() }
      }).then(function (r) {
        if (r.ok) { location.reload(); }
      });
    });
  }

  // ── Mobile sidebar toggle ───────────────────────────────
  const toggleBtn = document.getElementById('sidebar-toggle');
  const sidebar   = document.querySelector('.ci-sidebar');
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', function () {
      sidebar.classList.toggle('open');
    });
  }

  // ── Confirm delete modals ───────────────────────────────
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      if (!confirm(el.dataset.confirm)) { e.preventDefault(); }
    });
  });

  // ── Preview image before upload ─────────────────────────
  const photoInput = document.getElementById('id_photo');
  const photoPreview = document.getElementById('photo-preview');
  if (photoInput && photoPreview) {
    photoInput.addEventListener('change', function () {
      const file = photoInput.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function (e) { photoPreview.src = e.target.result; };
        reader.readAsDataURL(file);
      }
    });
  }

  // ── Headcount character counter for textareas ───────────
  document.querySelectorAll('textarea[maxlength]').forEach(function (ta) {
    const counter = document.createElement('small');
    counter.className = 'text-muted d-block text-end';
    ta.parentNode.appendChild(counter);
    function update() { counter.textContent = ta.value.length + ' / ' + ta.maxLength; }
    ta.addEventListener('input', update);
    update();
  });

  // ── Dynamic Live Greeting & Clock ──────────────────────────
  initLiveGreetingAndClock();

  // ── Animated Number Counters ────────────────────────────────
  animateCounters();

  // ── Quick Jump / Command Palette Spotlight ─────────────────
  initCommandPalette();

  // ── Tactile Click Ripples ──────────────────────────────────
  initTactileRipples();
});

// ── Dynamic Live Greeting & Clock ───────────────────────────
function initLiveGreetingAndClock() {
  const greetingEl = document.getElementById('ciGreetingTime');
  const clockEl = document.getElementById('ciLiveClock');

  if (greetingEl) {
    const hour = new Date().getHours();
    let text = 'Good day';
    if (hour >= 4 && hour < 12) text = 'Good morning';
    else if (hour >= 12 && hour < 17) text = 'Good afternoon';
    else if (hour >= 17 && hour < 22) text = 'Good evening';
    else text = 'Welcome back';
    greetingEl.textContent = text;
  }

  if (clockEl) {
    const updateTime = function () {
      const now = new Date();
      const options = { weekday: 'short', month: 'short', day: 'numeric' };
      const dateStr = now.toLocaleDateString(undefined, options);
      const timeStr = now.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
      clockEl.textContent = `${dateStr} • ${timeStr}`;
    };
    updateTime();
    setInterval(updateTime, 30000);
  }
}

// ── Animated Number Counters ────────────────────────────────
function animateCounters() {
  const counters = document.querySelectorAll('.ci-counter');
  counters.forEach(function (el) {
    const rawTarget = el.dataset.target || el.textContent;
    const target = parseInt(rawTarget.replace(/[^0-9]/g, ''), 10);
    if (isNaN(target)) return;

    const duration = 750; // ms
    const startTime = performance.now();

    function update(now) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // easeOutCubic: 1 - Math.pow(1 - progress, 3)
      const ease = 1 - Math.pow(1 - progress, 3);
      const current = Math.floor(ease * target);
      el.textContent = current.toLocaleString();

      if (progress < 1) {
        requestAnimationFrame(update);
      } else {
        el.textContent = target.toLocaleString();
      }
    }

    requestAnimationFrame(update);
  });
}

// ── Quick Jump / Command Palette Spotlight ──────────────────
function initCommandPalette() {
  const modalEl = document.getElementById('ciCommandModal');
  if (!modalEl) return;

  const inputEl = document.getElementById('ciCommandInput');
  const resultsEl = document.getElementById('ciCommandResults');
  const triggers = document.querySelectorAll('#ciCommandTrigger, .ci-cmd-open-btn');

  const COMMANDS = [
    { title: 'Dashboard', desc: 'Overview, stats & active alerts', url: '/dashboard/', icon: 'fa-th-large', cat: 'Main' },
    { title: 'Manage People', desc: 'Directory of users & accounts', url: '/auth/users/', icon: 'fa-users', cat: 'People' },
    { title: 'Pastoral Team', desc: 'Pastors & pastoral oversight', url: '/pastors/', icon: 'fa-cross', cat: 'People' },
    { title: 'Leadership Directory', desc: 'Executive, committee & cell leaders', url: '/leadership/', icon: 'fa-users-cog', cat: 'People' },
    { title: 'Student Anchors', desc: 'Student anchor leaders', url: '/leadership/anchors/', icon: 'fa-anchor', cat: 'People' },
    { title: 'Alumni Network', desc: 'Graduated members directory', url: '/auth/alumni/', icon: 'fa-user-graduate', cat: 'People' },
    { title: 'Church Calendar', desc: 'Events, meetings & services schedule', url: '/calendar/', icon: 'fa-calendar-days', cat: 'Ministry' },
    { title: 'Evangelism Hub', desc: 'Outreach records, converts & stats', url: '/evangelism/', icon: 'fa-fire', cat: 'Ministry' },
    { title: 'Cells & Fellowships', desc: 'Active cell groups & meetings', url: '/cells/', icon: 'fa-people-group', cat: 'Ministry' },
    { title: 'Departments', desc: 'Music, media, ushering & teams', url: '/departments/', icon: 'fa-layer-group', cat: 'Ministry' },
    { title: 'Birthdays', desc: 'Upcoming member celebrations', url: '/departments/birthdays/', icon: 'fa-birthday-cake', cat: 'Ministry' },
    { title: 'Record Service', desc: 'Add new Sunday service headcount & sermon', url: '/services/create/', icon: 'fa-church', cat: 'Actions' },
    { title: 'Services History', desc: 'All past services & attendance', url: '/services/', icon: 'fa-bible', cat: 'Ministry' },
    { title: 'Newbies & First-Timers', desc: 'New believers & visitors register', url: '/newbies/', icon: 'fa-user-plus', cat: 'Ministry' },
    { title: 'Reports Inbox', desc: 'Cell & consolidated weekly reports', url: '/cells/reports/consolidated/all/', icon: 'fa-inbox', cat: 'Reports' },
    { title: 'Send Consolidated Report', desc: 'Submit weekly report packet', url: '/cells/reports/consolidated/', icon: 'fa-file-export', cat: 'Reports' },
    { title: 'Notifications', desc: 'System alerts, birthdays & activity', url: '/notifications/', icon: 'fa-bell', cat: 'Account' },
    { title: 'My Profile', desc: 'Account details & password', url: '/auth/profile/', icon: 'fa-user-circle', cat: 'Account' },
  ];

  let bsModal = null;
  function getModal() {
    if (!bsModal) {
      bsModal = bootstrap.Modal.getOrCreateInstance(modalEl);
    }
    return bsModal;
  }

  function openSpotlight() {
    getModal().show();
    setTimeout(function () {
      if (inputEl) {
        inputEl.value = '';
        renderResults('');
        inputEl.focus();
      }
    }, 150);
  }

  triggers.forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      openSpotlight();
    });
  });

  document.addEventListener('keydown', function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      openSpotlight();
    } else if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
      e.preventDefault();
      openSpotlight();
    }
  });

  function renderResults(query) {
    const q = query.trim().toLowerCase();
    const filtered = COMMANDS.filter(function (cmd) {
      return !q || cmd.title.toLowerCase().includes(q) || cmd.desc.toLowerCase().includes(q) || cmd.cat.toLowerCase().includes(q);
    });

    if (filtered.length === 0) {
      resultsEl.innerHTML = `
        <div class="text-center py-4 text-muted">
          <i class="fas fa-search mb-2" style="font-size:1.5rem;opacity:.4;"></i>
          <div>No results found for "${escapeHtml(query)}"</div>
          <small class="text-muted">Try searching for "cells", "birthdays", or "service"</small>
        </div>
      `;
      return;
    }

    const categories = {};
    filtered.forEach(function (cmd) {
      if (!categories[cmd.cat]) categories[cmd.cat] = [];
      categories[cmd.cat].push(cmd);
    });

    let html = '';
    let globalIndex = 0;
    Object.keys(categories).forEach(function (cat) {
      html += `<div class="ci-cmd-cat">${cat}</div>`;
      categories[cat].forEach(function (cmd) {
        const isSelected = globalIndex === 0 ? 'selected' : '';
        html += `
          <a href="${cmd.url}" class="ci-cmd-item ${isSelected}" data-index="${globalIndex}">
            <div class="ci-cmd-icon"><i class="fas ${cmd.icon}"></i></div>
            <div class="flex-grow-1 overflow-hidden">
              <div class="fw-semibold text-truncate" style="font-size:.9rem;">${cmd.title}</div>
              <div class="text-muted small text-truncate" style="font-size:.76rem;">${cmd.desc}</div>
            </div>
            <i class="fas fa-chevron-right fa-xs text-muted opacity-50"></i>
          </a>
        `;
        globalIndex++;
      });
    });

    resultsEl.innerHTML = html;
  }

  if (inputEl) {
    inputEl.addEventListener('input', function () {
      renderResults(inputEl.value);
    });

    inputEl.addEventListener('keydown', function (e) {
      const items = resultsEl.querySelectorAll('.ci-cmd-item');
      if (!items.length) return;

      let currentIndex = -1;
      items.forEach(function (item, idx) {
        if (item.classList.contains('selected')) currentIndex = idx;
      });

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        const nextIndex = (currentIndex + 1) % items.length;
        updateSelection(items, nextIndex);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        const prevIndex = (currentIndex - 1 + items.length) % items.length;
        updateSelection(items, prevIndex);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (currentIndex >= 0 && items[currentIndex]) {
          items[currentIndex].click();
        }
      }
    });
  }

  function updateSelection(items, index) {
    items.forEach(function (el, i) {
      el.classList.toggle('selected', i === index);
      if (i === index) el.scrollIntoView({ block: 'nearest' });
    });
  }

  function escapeHtml(str) {
    return str.replace(/[&<>'"]/g, function (tag) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' })[tag] || tag;
    });
  }
}

// ── Tactile Click Ripples ───────────────────────────────────
function initTactileRipples() {
  document.addEventListener('click', function (e) {
    const target = e.target.closest('.btn, .ci-quick-card, .ci-stat, .ci-card-interactive');
    if (!target) return;

    target.classList.add('ci-ripple-target');
    const rect = target.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;

    const wave = document.createElement('span');
    wave.className = 'ci-ripple-wave';
    wave.style.width = wave.style.height = `${size}px`;
    wave.style.left = `${x}px`;
    wave.style.top = `${y}px`;

    target.appendChild(wave);
    setTimeout(function () {
      wave.remove();
    }, 600);
  });
}


// ── Helpers ─────────────────────────────────────────────────
function getCsrf() {
  const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
  return cookie ? cookie.split('=')[1] : '';
}

function updateBadge(delta) {
  const badges = document.querySelectorAll('.notif-badge');
  badges.forEach(function (b) {
    const cur = parseInt(b.textContent, 10) || 0;
    const next = cur + delta;
    b.textContent = next > 0 ? next : '';
    b.style.display = next > 0 ? '' : 'none';
  });
}

// ── Toast helper (callable from templates) ──────────────────
function showToast(message, type) {
  type = type || 'success';
  const container = document.getElementById('toast-container') || createToastContainer();
  const id = 'toast-' + Date.now();
  const icon = type === 'success' ? 'fa-check-circle' : type === 'danger' ? 'fa-exclamation-circle' : 'fa-info-circle';
  container.insertAdjacentHTML('beforeend', `
    <div id="${id}" class="toast align-items-center text-bg-${type} border-0 show" role="alert">
      <div class="d-flex">
        <div class="toast-body"><i class="fas ${icon} me-2"></i>${message}</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>
    </div>
  `);
  setTimeout(function () {
    const el = document.getElementById(id);
    if (el) { bootstrap.Toast.getOrCreateInstance(el).hide(); }
  }, 4000);
}

function createToastContainer() {
  const c = document.createElement('div');
  c.id = 'toast-container';
  c.className = 'toast-container position-fixed bottom-0 end-0 p-3';
  c.style.zIndex = '9999';
  document.body.appendChild(c);
  return c;
}
