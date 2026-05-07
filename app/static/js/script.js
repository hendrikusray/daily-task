// === PAGE LOADER ===
;(function () {
    var loader = document.getElementById('pageLoader');
    if (!loader) return;
    var t0 = Date.now();
    var MIN_MS = 3000;

    function hideLoader() {
        var wait = Math.max(0, MIN_MS - (Date.now() - t0));
        setTimeout(function () {
            loader.classList.add('loader-out');
            setTimeout(function () { loader.style.display = 'none'; }, 750);
        }, wait);
    }

    if (document.readyState === 'complete') {
        hideLoader();
    } else {
        window.addEventListener('load', hideLoader);
    }
}());

// === PASSWORD TOGGLE ===
function togglePasswordVisibility(inputId) {
    const input = document.getElementById(inputId);
    const toggle = input.parentElement.querySelector('.password-toggle');
    if (input.type === 'password') {
        input.type = 'text';
        toggle.textContent = '🙈';
    } else {
        input.type = 'password';
        toggle.textContent = '👁️';
    }
}

// === CATEGORY DROPDOWN + FREETEXT ===
function handleCategorySelect(select) {
    var input = document.getElementById('category_value');
    if (!input) return;
    if (select.value === '__custom__') {
        input.style.display = 'block';
        input.value = '';
        input.focus();
    } else {
        input.style.display = 'none';
        input.value = select.value;
    }
}

function initCategoryField(currentValue, presetValues) {
    var select = document.getElementById('category_preset');
    var input = document.getElementById('category_value');
    if (!select || !input) return;
    if (presetValues.includes(currentValue)) {
        select.value = currentValue;
        input.value = currentValue;
        input.style.display = 'none';
    } else if (currentValue) {
        select.value = '__custom__';
        input.value = currentValue;
        input.style.display = 'block';
    }
}

// === PK DRIVE UPLOAD ===
function uploadPKToDrive(inputEl) {
    var file = inputEl.files[0];
    if (!file) return;
    var linkInput = document.getElementById('product_knowledge_link');
    var statusEl = document.getElementById('pkUploadStatus');

    function setStatus(cls, msg) {
        statusEl.className = 'drive-status ' + cls;
        statusEl.textContent = msg;
        statusEl.style.display = 'block';
    }

    setStatus('uploading', '⏳ Mengupload "' + file.name + '" ke Google Drive...');
    var formData = new FormData();
    formData.append('file', file);

    fetch('/drive/upload', { method: 'POST', body: formData })
        .then(function (r) { return r.json(); })
        .then(function (d) {
            if (d.error) { setStatus('error', '❌ ' + d.error); }
            else { if (linkInput) linkInput.value = d.link; setStatus('success', '✅ Upload berhasil!'); }
        })
        .catch(function () { setStatus('error', '❌ Gagal upload. Coba lagi.'); })
        .finally(function () { inputEl.value = ''; });
}

// === CAMPAIGN DETAIL PANEL ===
function openCampaignDetail(row) {
    var modal = document.getElementById('campaignDetailModal');
    if (!modal) return;

    document.getElementById('detailCategory').textContent = row.dataset.category || '';
    document.getElementById('detailCampaign').textContent = row.dataset.campaign || '-';
    document.getElementById('detailBrand').textContent = row.dataset.brand || '';
    document.getElementById('detailEditBtn').href = row.dataset.editUrl || '#';

    var statusClass = (row.dataset.status || 'none').toLowerCase().replace(/ /g, '-').replace(/'/g, '');
    var body = document.getElementById('detailBody');
    body.innerHTML = '';

    // Quick stats row: Platform, Status, Deadline, Payment, Fee
    var stats = [
        { label: 'Platform',  value: row.dataset.platform },
        { label: 'Status',    value: row.dataset.status,   isStatus: true },
        { label: 'Deadline',  value: row.dataset.deadline, isDeadline: true },
        { label: 'Payment',   value: row.dataset.payment },
        { label: 'Fee',       value: row.dataset.fee },
    ];
    var hasStats = stats.some(function(s) { return !!s.value; });
    if (hasStats) {
        var grid = document.createElement('div');
        grid.className = 'detail-stats-grid';
        stats.forEach(function(s) {
            if (!s.value) return;
            var cell = document.createElement('div');
            cell.className = 'detail-stat';
            var val;
            if (s.isStatus) {
                val = '<span class="status-badge status-' + statusClass + '">' + s.value + '</span>';
            } else if (s.isDeadline) {
                var tag = '';
                if (row.dataset.deadlineState === 'due-soon') tag = ' <span class="deadline-soon-tag">H-5</span>';
                if (row.dataset.deadlineState === 'overdue')  tag = ' <span class="deadline-overdue-tag">Overdue</span>';
                val = '<span class="detail-stat-value">' + s.value + tag + '</span>';
            } else {
                val = '<span class="detail-stat-value">' + s.value + '</span>';
            }
            cell.innerHTML = '<span class="detail-stat-label">' + s.label + '</span>' + val;
            grid.appendChild(cell);
        });
        body.appendChild(grid);
    }

    // Text sections
    var sections = [
        { label: '📝 SOW',               value: row.dataset.sow },
        { label: '🛍️ Product Knowledge', value: row.dataset.pk },
        { label: '📎 PK Link / File',    value: row.dataset.pkLink, isLink: true, linkText: 'Buka File' },
        { label: '🔗 Link Content',      value: row.dataset.link,   isLink: true, linkText: 'Buka Link Content' },
        { label: '💬 Note',              value: row.dataset.note },
    ];
    sections.forEach(function(s) {
        if (!s.value) return;
        var sec = document.createElement('div');
        sec.className = 'detail-section';
        var content = s.isLink
            ? '<a href="' + s.value + '" target="_blank" rel="noopener" class="detail-link-btn">🔗 ' + s.linkText + '</a>'
            : '<div class="detail-section-content">' + s.value.replace(/\n/g, '<br>') + '</div>';
        sec.innerHTML = '<div class="detail-section-label">' + s.label + '</div>' + content;
        body.appendChild(sec);
    });

    modal.hidden = false;
    document.body.classList.add('modal-open');
}

function closeCampaignDetail() {
    var modal = document.getElementById('campaignDetailModal');
    if (modal) { modal.hidden = true; document.body.classList.remove('modal-open'); }
}

// === GOOGLE DRIVE UPLOAD ===
function uploadToDrive(input) {
    const file = input.files[0];
    if (!file) return;

    const linkInput = document.getElementById('link_content');
    const statusEl = document.getElementById('driveUploadStatus');
    const uploadBtn = document.getElementById('driveUploadBtn');

    function setStatus(cls, msg) {
        statusEl.className = 'drive-status ' + cls;
        statusEl.textContent = msg;
        statusEl.style.display = 'block';
    }

    setStatus('uploading', '⏳ Mengupload "' + file.name + '" ke Google Drive...');
    if (uploadBtn) { uploadBtn.disabled = true; uploadBtn.textContent = 'Mengupload...'; }

    const formData = new FormData();
    formData.append('file', file);

    fetch('/drive/upload', { method: 'POST', body: formData })
        .then(function (res) { return res.json(); })
        .then(function (data) {
            if (data.error) {
                setStatus('error', '❌ ' + data.error);
            } else {
                if (linkInput) linkInput.value = data.link;
                setStatus('success', '✅ Upload berhasil! Link sudah diisi otomatis.');
            }
        })
        .catch(function () {
            setStatus('error', '❌ Terjadi kesalahan jaringan. Coba lagi.');
        })
        .finally(function () {
            if (uploadBtn) {
                uploadBtn.disabled = false;
                uploadBtn.innerHTML = '<svg class="drive-icon" viewBox="0 0 87.3 78" xmlns="http://www.w3.org/2000/svg"><path d="M6.6 66.85l3.85 6.65c.8 1.4 1.95 2.5 3.3 3.3L28 55.65H0c0 1.55.4 3.1 1.2 4.5z" fill="#0066DA"/><path d="M43.65 25L29.35 0c-1.35.8-2.5 1.9-3.3 3.3L1.2 46.4C.4 47.8 0 49.35 0 50.9h28z" fill="#00AC47"/><path d="M73.55 76.8c1.35-.8 2.5-1.9 3.3-3.3L77.7 72l14.5-25.1c.8-1.4 1.2-2.95 1.2-4.5H65.3L73.55 76.8z" fill="#EA4335"/><path d="M43.65 25L57.95 0H29.35z" fill="#00832D"/><path d="M86.1 50.9H65.3L43.65 25 28 50.9z" fill="#2684FC"/><path d="M43.65 25l-15.65 25.9-15.4 15.15c.8.8 1.75 1.45 2.85 1.8l28.2-42.85z" fill="#FFBA00"/></svg> Upload ke Drive';
            }
            input.value = '';
        });
}

// === INIT ON DOM READY ===
document.addEventListener('DOMContentLoaded', function () {
    const deleteModal = document.getElementById('deleteModal');
    const deleteCampaignTitle = document.getElementById('deleteCampaignTitle');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    let pendingDeleteForm = null;

    function openDeleteModal(form) {
        if (!deleteModal || !confirmDeleteBtn) return;

        pendingDeleteForm = form;
        const campaignTitle = form.dataset.deleteTitle || 'Campaign ini';
        if (deleteCampaignTitle) {
            deleteCampaignTitle.textContent = campaignTitle;
        }

        deleteModal.hidden = false;
        document.body.classList.add('modal-open');
        confirmDeleteBtn.focus();
    }

    function closeDeleteModal() {
        if (!deleteModal) return;

        deleteModal.hidden = true;
        document.body.classList.remove('modal-open');
        pendingDeleteForm = null;
    }

    // Flatpickr date pickers
    if (typeof flatpickr !== 'undefined') {
        flatpickr('.datepicker', {
            locale: 'id',
            dateFormat: 'Y-m-d',
            altInput: true,
            altFormat: 'd F Y',
            disableMobile: false,
            allowInput: false
        });
    }

    // Auto-dismiss alerts after 4.5 seconds
    document.querySelectorAll('.alert').forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = 'opacity 0.4s, transform 0.4s';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-6px)';
            setTimeout(function () { alert.remove(); }, 400);
        }, 4500);
    });

    // Custom delete confirmation modal
    document.querySelectorAll('.konten-delete-form').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            openDeleteModal(form);
        });
    });

    document.querySelectorAll('[data-modal-close]').forEach(function (button) {
        button.addEventListener('click', closeDeleteModal);
    });

    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', function () {
            if (!pendingDeleteForm) return;
            HTMLFormElement.prototype.submit.call(pendingDeleteForm);
        });
    }

    // === THEME PICKER ===
    var themeSheet = document.getElementById('mobileThemeSheet');
    var themeIcons = {
        lily: '🌸',
        polka: '●',
        garden: '🌿',
        floral: '✿'
    };

    function syncThemeControls(theme) {
        document.querySelectorAll('.theme-dot[data-theme-btn]').forEach(function (btn) {
            var isActive = btn.dataset.themeBtn === theme;
            btn.classList.toggle('active', isActive);
            btn.setAttribute('aria-pressed', isActive ? 'true' : 'false');
        });

        document.querySelectorAll('.theme-choice[data-theme-choice]').forEach(function (choice) {
            var isActive = choice.dataset.themeChoice === theme;
            choice.classList.toggle('active', isActive);
            choice.setAttribute('aria-pressed', isActive ? 'true' : 'false');
        });

        document.querySelectorAll('[data-current-theme-icon]').forEach(function (icon) {
            icon.textContent = themeIcons[theme] || themeIcons.lily;
        });
    }

    function setTheme(theme) {
        document.body.dataset.theme = theme;
        try { localStorage.setItem('marianne-theme', theme); } catch (e) {}
        syncThemeControls(theme);
    }

    function openThemeSheet() {
        if (!themeSheet) return;
        themeSheet.hidden = false;
        document.body.classList.add('modal-open');

        var activeChoice = themeSheet.querySelector('.theme-choice.active') ||
            themeSheet.querySelector('.theme-choice');
        if (activeChoice) activeChoice.focus();
    }

    function closeThemeSheet() {
        if (!themeSheet) return;
        themeSheet.hidden = true;
        document.body.classList.remove('modal-open');
    }

    syncThemeControls(document.body.dataset.theme || 'lily');

    document.querySelectorAll('.theme-dot[data-theme-btn]').forEach(function (btn) {
        btn.addEventListener('click', function () {
            setTheme(btn.dataset.themeBtn);
        });
    });

    document.querySelectorAll('.theme-choice[data-theme-choice]').forEach(function (choice) {
        choice.addEventListener('click', function () {
            setTheme(choice.dataset.themeChoice);
            closeThemeSheet();
        });
    });

    document.querySelectorAll('[data-theme-open]').forEach(function (button) {
        button.addEventListener('click', openThemeSheet);
    });

    document.querySelectorAll('[data-theme-close]').forEach(function (button) {
        button.addEventListener('click', closeThemeSheet);
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            if (deleteModal && !deleteModal.hidden) closeDeleteModal();
            var detailModal = document.getElementById('campaignDetailModal');
            if (detailModal && !detailModal.hidden) closeCampaignDetail();
            if (themeSheet && !themeSheet.hidden) closeThemeSheet();
        }
    });
});
