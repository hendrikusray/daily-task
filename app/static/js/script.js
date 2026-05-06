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

// === CATEGORY CUSTOM FIELD ===
function handleCategorySelect(select) {
    const wrapper = select.closest('.category-wrapper');
    const textInput = wrapper.querySelector('.category-text-input');
    if (select.value === '__custom__') {
        textInput.style.display = 'block';
        textInput.value = '';
        textInput.focus();
    } else {
        textInput.style.display = 'none';
        textInput.value = select.value;
    }
}

// Initialize category field for edit form (called inline from template)
function initCategoryField(currentValue, presetValues) {
    const select = document.getElementById('category_preset');
    const textInput = document.getElementById('category_value');
    if (!select || !textInput) return;

    if (presetValues.includes(currentValue)) {
        select.value = currentValue;
        textInput.value = currentValue;
        textInput.style.display = 'none';
    } else if (currentValue) {
        select.value = '__custom__';
        textInput.value = currentValue;
        textInput.style.display = 'block';
    } else {
        textInput.style.display = 'none';
    }
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

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && deleteModal && !deleteModal.hidden) {
            closeDeleteModal();
        }
    });
});
