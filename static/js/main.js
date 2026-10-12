// Main JavaScript for Lab Equipment Booking System

document.addEventListener('DOMContentLoaded', function () {
    // 1. Enforce minimum date to today for booking date inputs
    const bookingDateInputs = document.querySelectorAll('input[type="date"].min-today');
    if (bookingDateInputs.length > 0) {
        const today = new Date().toISOString().split('T')[0];
        bookingDateInputs.forEach(input => {
            input.setAttribute('min', today);
        });
    }

    // 2. Client-side time validation feedback on booking form
    const bookingForm = document.getElementById('bookingForm');
    if (bookingForm) {
        const startTimeInput = bookingForm.querySelector('input[name="start_time"]');
        const endTimeInput = bookingForm.querySelector('input[name="end_time"]');
        const timeAlert = document.getElementById('timeValidationAlert');

        function checkTimes() {
            if (startTimeInput && endTimeInput && startTimeInput.value && endTimeInput.value) {
                if (startTimeInput.value >= endTimeInput.value) {
                    if (timeAlert) {
                        timeAlert.classList.remove('d-none');
                        timeAlert.textContent = 'Start time must be strictly earlier than end time.';
                    }
                } else {
                    if (timeAlert) {
                        timeAlert.classList.add('d-none');
                    }
                }
            }
        }

        if (startTimeInput && endTimeInput) {
            startTimeInput.addEventListener('change', checkTimes);
            endTimeInput.addEventListener('change', checkTimes);
        }
    }

    // 3. Confirmation modal/prompt for destructive actions
    const deleteButtons = document.querySelectorAll('[data-confirm]');
    deleteButtons.forEach(btn => {
        btn.addEventListener('click', function (e) {
            const message = this.getAttribute('data-confirm') || 'Are you sure you want to proceed with this action?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // 4. Auto-dismiss temporary alerts after 6 seconds
    const flashAlerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    flashAlerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 6000);
    });
});
