document.addEventListener('DOMContentLoaded', function() {
    // Form validation and dynamic updates
    const form = document.querySelector('form');
    const loanAmountInput = document.getElementById('loan_amount');
    const monthlyIncomeInput = document.getElementById('monthly_income');
    const loanDurationInput = document.getElementById('loan_duration');
    const interestRateInput = document.getElementById('interest_rate');

    if (form) {
        form.addEventListener('submit', function(e) {
            // Basic form validation
            if (!validateForm()) {
                e.preventDefault();
                return false;
            }
        });
    }

    // Add input event listeners for real-time validation
    const numericInputs = document.querySelectorAll('input[type="number"]');
    numericInputs.forEach(input => {
        input.addEventListener('input', function() {
            validateInput(this);
        });
    });

    function validateForm() {
        let isValid = true;
        const requiredInputs = form.querySelectorAll('input[required], select[required]');
        
        requiredInputs.forEach(input => {
            if (!validateInput(input)) {
                isValid = false;
            }
        });

        // Additional validation rules
        if (parseFloat(loanAmountInput.value) > parseFloat(monthlyIncomeInput.value) * 60) {
            alert('Loan amount should not exceed 5 years of monthly income');
            isValid = false;
        }

        return isValid;
    }

    function validateInput(input) {
        const value = input.value.trim();
        
        // Remove any existing error messages
        const existingError = input.parentElement.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }

        // Check if empty
        if (input.hasAttribute('required') && !value) {
            showError(input, 'This field is required');
            return false;
        }

        // Validate numeric ranges
        if (input.type === 'number') {
            const min = input.getAttribute('min');
            const max = input.getAttribute('max');
            const numValue = parseFloat(value);

            if (min && numValue < parseFloat(min)) {
                showError(input, `Minimum value is ${min}`);
                return false;
            }
            if (max && numValue > parseFloat(max)) {
                showError(input, `Maximum value is ${max}`);
                return false;
            }
        }

        return true;
    }

    function showError(input, message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.style.color = 'red';
        errorDiv.style.fontSize = '0.8rem';
        errorDiv.style.marginTop = '0.25rem';
        errorDiv.textContent = message;
        input.parentElement.appendChild(errorDiv);
    }

    // Calculate and display monthly payment (if on form page)
    if (loanAmountInput && loanDurationInput && interestRateInput) {
        [loanAmountInput, loanDurationInput, interestRateInput].forEach(input => {
            input.addEventListener('input', calculateMonthlyPayment);
        });
    }

    function calculateMonthlyPayment() {
        const principal = parseFloat(loanAmountInput.value) || 0;
        const duration = parseFloat(loanDurationInput.value) || 0;
        const rate = (parseFloat(interestRateInput.value) || 0) / 100 / 12;

        if (principal > 0 && duration > 0 && rate > 0) {
            const monthlyPayment = (principal * rate * Math.pow(1 + rate, duration)) / 
                                 (Math.pow(1 + rate, duration) - 1);
            
            // Update or create monthly payment display
            let paymentDisplay = document.getElementById('monthly-payment-display');
            if (!paymentDisplay) {
                paymentDisplay = document.createElement('div');
                paymentDisplay.id = 'monthly-payment-display';
                paymentDisplay.style.marginTop = '1rem';
                paymentDisplay.style.padding = '1rem';
                paymentDisplay.style.backgroundColor = '#e3f2fd';
                paymentDisplay.style.borderRadius = '8px';
                loanAmountInput.parentElement.appendChild(paymentDisplay);
            }
            paymentDisplay.textContent = `Estimated Monthly Payment: $${monthlyPayment.toFixed(2)}`;
        }
    }
});
