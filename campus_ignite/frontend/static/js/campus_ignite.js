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
});

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
