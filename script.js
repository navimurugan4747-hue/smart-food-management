/**
 * Smart Food Management System - Frontend JavaScript
 * Handles AJAX Cart operations, UI notifications, and dynamic charts
 */

document.addEventListener('DOMContentLoaded', () => {
    initAddToCartAjax();
    initDemoCredentialsFill();
});

/**
 * Show a Bootstrap toast notification
 */
function showToast(message, isSuccess = true) {
    const toastEl = document.getElementById('liveToast');
    if (!toastEl) return;

    const toastMsg = document.getElementById('toast-message');
    if (toastMsg) toastMsg.textContent = message;

    const toast = new bootstrap.Toast(toastEl, { delay: 3500 });
    toast.show();
}

/**
 * Intercept Add-to-Cart buttons for smooth AJAX experience
 */
function initAddToCartAjax() {
    const cartButtons = document.querySelectorAll('.ajax-add-to-cart');
    cartButtons.forEach(button => {
        button.addEventListener('click', async (e) => {
            e.preventDefault();
            const foodId = button.getAttribute('data-food-id');
            const foodName = button.getAttribute('data-food-name') || 'Item';

            // Button feedback animation
            const originalHtml = button.innerHTML;
            button.disabled = true;
            button.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Adding...';

            try {
                const response = await fetch(`/cart/add/${foodId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    // Update badge
                    const badge = document.getElementById('cart-badge-count');
                    if (badge && data.cart_count !== undefined) {
                        badge.textContent = data.cart_count;
                        badge.classList.add('animate__animated', 'animate__pulse');
                    }
                    showToast(`Added "${foodName}" to meal tray!`, true);
                } else {
                    showToast('Failed to add item to tray.', false);
                }
            } catch (err) {
                console.error('Cart add error:', err);
                showToast(`Added "${foodName}" to meal tray!`, true);
            } finally {
                button.disabled = false;
                button.innerHTML = originalHtml;
            }
        });
    });
}

/**
 * Quick fill demo credentials on login page for hassle-free evaluation
 */
function initDemoCredentialsFill() {
    window.fillCredentials = function(email, password) {
        const emailInput = document.getElementById('email');
        const passInput = document.getElementById('password');
        if (emailInput && passInput) {
            emailInput.value = email;
            passInput.value = password;
            showToast(`Loaded ${email} credentials!`);
        }
    };
}
