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
