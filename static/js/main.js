/**
 * Lab Equipment Booking System - Core JavaScript
 * Handles client-side validations, real-time availability checks,
 * modal triggers, confirmation prompts, and UI enhancements across all pages.
 */

document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    // =========================================================================
    // 1. Global: Auto-dismiss Flash Alerts
    // =========================================================================
    const flashAlerts = document.querySelectorAll('.alert:not(.alert-permanent):not(#timeValidationAlert):not(#availabilityBadge)');
    flashAlerts.forEach(function (alert) {
        setTimeout(function () {
            if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                if (bsAlert) {
                    bsAlert.close();
                }
            } else {
                alert.style.transition = 'opacity 0.5s ease';
                alert.style.opacity = '0';
                setTimeout(function () {
                    alert.remove();
                }, 500);
            }
        }, 6000);
    });

    // =========================================================================
    // 2. Global: Confirmation for Destructive Actions
    // =========================================================================
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            const message = this.getAttribute('data-confirm') || 'Are you sure you want to proceed with this action?';
            if (!window.confirm(message)) {
                e.preventDefault();
                e.stopPropagation();
            }
        });
    });

    // =========================================================================
    // 3. Global: Active Navbar Link Highlight
    // =========================================================================
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    navLinks.forEach(function (link) {
        const href = link.getAttribute('href');
        if (href && (href === currentPath || (href !== '/' && currentPath.startsWith(href)))) {
            link.classList.add('active');
        }
    });

    // =========================================================================
    // 4. Booking Form (/student/book): Date, Time & Real-time Availability
    // =========================================================================
    const bookingForm = document.getElementById('bookingForm');
    if (bookingForm) {
        // Enforce min date to today
        const dateInput = bookingForm.querySelector('input[type="date"]');
        if (dateInput) {
            const today = new Date().toISOString().split('T')[0];
            dateInput.setAttribute('min', today);
        }

        const startTimeInput = bookingForm.querySelector('input[name="start_time"]');
        const endTimeInput = bookingForm.querySelector('input[name="end_time"]');
        const timeAlert = document.getElementById('timeValidationAlert');
        const equipmentSelect = bookingForm.querySelector('select[name="equipment_id"]');
        const quantityInput = bookingForm.querySelector('input[name="quantity"]');
        const submitBtn = bookingForm.querySelector('button[type="submit"]');

        // Container for dynamic availability feedback if present or create dynamically
        let availabilityContainer = document.getElementById('availabilityBadge');
        if (!availabilityContainer && timeAlert) {
            availabilityContainer = document.createElement('div');
            availabilityContainer.id = 'availabilityBadge';
            availabilityContainer.className = 'alert d-none py-2 px-3 mb-3 small';
            timeAlert.parentNode.insertBefore(availabilityContainer, timeAlert.nextSibling);
        }

        function validateTimes() {
            if (!startTimeInput || !endTimeInput) return true;
            const startVal = startTimeInput.value;
            const endVal = endTimeInput.value;

            if (startVal && endVal) {
                if (startVal >= endVal) {
                    if (timeAlert) {
                        timeAlert.classList.remove('d-none');
                        timeAlert.textContent = 'Start time must be strictly earlier than end time.';
                    }
                    if (submitBtn) submitBtn.disabled = true;
                    return false;
                } else {
                    if (timeAlert) {
                        timeAlert.classList.add('d-none');
                    }
                    if (submitBtn) submitBtn.disabled = false;
                    return true;
                }
            }
            return true;
        }

        function checkLiveAvailability() {
            if (!validateTimes()) return;
            if (!equipmentSelect || !dateInput || !startTimeInput || !endTimeInput) return;

            const eqId = equipmentSelect.value;
            const bDate = dateInput.value;
            const sTime = startTimeInput.value;
            const eTime = endTimeInput.value;

            if (eqId && bDate && sTime && eTime && sTime < eTime) {
                const apiUrl = `/equipment/api/check-availability?equipment_id=${encodeURIComponent(eqId)}&date=${encodeURIComponent(bDate)}&start_time=${encodeURIComponent(sTime)}&end_time=${encodeURIComponent(eTime)}`;

                fetch(apiUrl)
                    .then(function (res) { return res.json(); })
                    .then(function (data) {
                        if (data && data.success && availabilityContainer) {
                            availabilityContainer.classList.remove('d-none', 'alert-success', 'alert-warning', 'alert-danger');
                            if (data.available_quantity > 0) {
                                availabilityContainer.classList.add('alert-success');
                                availabilityContainer.innerHTML = `<i class="bi bi-check-circle-fill me-1"></i> Slot Available: <strong>${data.available_quantity}</strong> of ${data.total_inventory} units currently available.`;
                                if (quantityInput) {
                                    quantityInput.max = data.available_quantity;
                                }
                            } else {
                                availabilityContainer.classList.add('alert-warning');
                                availabilityContainer.innerHTML = `<i class="bi bi-exclamation-triangle-fill me-1"></i> Slot Overbooked: 0 of ${data.total_inventory} units available (all currently booked).`;
                            }
                        }
                    })
                    .catch(function () {
                        // Silent fail for optional live check
                    });
            }
        }

        if (startTimeInput) startTimeInput.addEventListener('change', function () { validateTimes(); checkLiveAvailability(); });
        if (endTimeInput) endTimeInput.addEventListener('change', function () { validateTimes(); checkLiveAvailability(); });
        if (dateInput) dateInput.addEventListener('change', checkLiveAvailability);
        if (equipmentSelect) equipmentSelect.addEventListener('change', checkLiveAvailability);

        // Pre-validate on page load if inputs have pre-filled values
        validateTimes();
    }

    // =========================================================================
    // 5. Auth / Registration: Real-time Password Confirmation & Strength
    // =========================================================================
    const regForm = document.querySelector('form[action*="register"]');
    if (regForm) {
        const passwordInput = regForm.querySelector('input[name="password"]');
        const confirmInput = regForm.querySelector('input[name="confirm_password"]');
        const submitBtn = regForm.querySelector('button[type="submit"]');

        let matchFeedback = document.getElementById('passwordMatchFeedback');
        if (!matchFeedback && confirmInput) {
            matchFeedback = document.createElement('div');
            matchFeedback.id = 'passwordMatchFeedback';
            matchFeedback.className = 'form-text small mt-1';
            confirmInput.parentNode.appendChild(matchFeedback);
        }

        function checkPasswordMatch() {
            if (!passwordInput || !confirmInput) return;
            const p1 = passwordInput.value;
            const p2 = confirmInput.value;

            if (p2.length > 0) {
                if (p1 !== p2) {
                    confirmInput.classList.add('is-invalid');
                    confirmInput.classList.remove('is-valid');
                    if (matchFeedback) {
                        matchFeedback.className = 'form-text small text-danger mt-1';
                        matchFeedback.innerHTML = '<i class="bi bi-x-circle me-1"></i> Passwords do not match.';
                    }
                } else {
                    confirmInput.classList.remove('is-invalid');
                    confirmInput.classList.add('is-valid');
                    if (matchFeedback) {
                        matchFeedback.className = 'form-text small text-success mt-1';
                        matchFeedback.innerHTML = '<i class="bi bi-check-circle me-1"></i> Passwords match.';
                    }
                }
            } else {
                confirmInput.classList.remove('is-invalid', 'is-valid');
                if (matchFeedback) {
                    matchFeedback.textContent = '';
                }
            }
        }

        if (confirmInput) confirmInput.addEventListener('input', checkPasswordMatch);
        if (passwordInput) passwordInput.addEventListener('input', checkPasswordMatch);
    }

    // =========================================================================
    // 6. Login Page: Password Visibility Toggle Helper
    // =========================================================================
    const passwordFields = document.querySelectorAll('input[type="password"]');
    passwordFields.forEach(function (field) {
        const parentGroup = field.closest('.input-group');
        if (parentGroup && !parentGroup.querySelector('.toggle-password-btn')) {
            const toggleBtn = document.createElement('button');
            toggleBtn.type = 'button';
            toggleBtn.className = 'btn btn-outline-secondary toggle-password-btn';
            toggleBtn.setAttribute('tabindex', '-1');
            toggleBtn.setAttribute('aria-label', 'Toggle password visibility');
            toggleBtn.innerHTML = '<i class="bi bi-eye"></i>';

            toggleBtn.addEventListener('click', function () {
                if (field.type === 'password') {
                    field.type = 'text';
                    toggleBtn.innerHTML = '<i class="bi bi-eye-slash"></i>';
                } else {
                    field.type = 'password';
                    toggleBtn.innerHTML = '<i class="bi bi-eye"></i>';
                }
            });
            parentGroup.appendChild(toggleBtn);
        }
    });

    // =========================================================================
    // 7. Staff Dashboard / Pending: Auto-focus Rejection Modal Reason Textarea
    // =========================================================================
    const rejectionModals = document.querySelectorAll('.modal');
    rejectionModals.forEach(function (modal) {
        modal.addEventListener('shown.bs.modal', function () {
            const textarea = modal.querySelector('textarea');
            if (textarea) {
                textarea.focus();
            }
        });
    });
});
