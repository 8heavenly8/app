function getCsrfToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function authFetch(url, options = {}) {
    const csrfToken = getCsrfToken();
    
    const defaultOptions = {
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
        },
    };
    
    const methodsWithCSRF = ['POST', 'PUT', 'PATCH', 'DELETE'];
    if (methodsWithCSRF.includes(options.method?.toUpperCase())) {
        defaultOptions.headers['X-CSRFToken'] = csrfToken;
    }
    
    const finalOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers,
        },
    };
    
    return fetch(url, finalOptions)
        .then(response => {
            if (response.status === 401) {
                handleUnauthorized();
                throw new Error('Не авторизован');
            }
            if (response.status === 403) {
                handleForbidden();
                throw new Error('Доступ запрещен');
            }
            return response;
        });
}

function handleUnauthorized() {
    const message = 'Сессия истекла. Пожалуйста, войдите заново.';
    showNotification('warning', message);
    
    setTimeout(() => {
        window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
    }, 2000);
}

function handleForbidden() {
    const message = 'У вас недостаточно прав для этого действия.';
    showNotification('danger', message);
}

function showNotification(type, message) {
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-width: 400px;
            width: 100%;
        `;
        document.body.appendChild(container);
    }
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.style.cssText = `
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        margin-bottom: 0;
        animation: slideInRight 0.5s ease;
    `;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" style="position: absolute; right: 15px; top: 50%; transform: translateY(-50%);"></button>
    `;
    
    container.appendChild(alertDiv);
    
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.style.opacity = '0';
            alertDiv.style.transition = 'opacity 0.5s';
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.remove();
                }
            }, 500);
        }
    }, 5000);
}

function getProfile() {
    return authFetch('/api/me/')
        .then(response => response.json())
        .catch(error => {
            console.error('Ошибка получения профиля:', error);
            throw error;
        });
}

function updateProfile(data) {
    return authFetch('/api/me/update/', {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .catch(error => {
        console.error('Ошибка обновления профиля:', error);
        throw error;
    });
}

function getProducts(filters = {}) {
    const params = new URLSearchParams(filters);
    const url = `/api/products/?${params.toString()}`;
    
    return authFetch(url)
        .then(response => response.json())
        .catch(error => {
            console.error('Ошибка получения товаров:', error);
            throw error;
        });
}

function createProduct(data) {
    return authFetch('/api/products/create/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .catch(error => {
        console.error('Ошибка создания товара:', error);
        throw error;
    });
}

function getOrders() {
    return authFetch('/api/orders/')
        .then(response => response.json())
        .catch(error => {
            console.error('Ошибка получения заказов:', error);
            throw error;
        });
}

function getOrderDetail(orderId) {
    return authFetch(`/api/orders/${orderId}/`)
        .then(response => response.json())
        .catch(error => {
            console.error('Ошибка получения деталей заказа:', error);
            throw error;
        });
}

function addToCart(productId, quantity = 1) {
    return authFetch('/api/cart/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity
        }),
    })
    .then(response => response.json())
    .catch(error => {
        console.error('Ошибка добавления в корзину:', error);
        throw error;
    });
}

function getCartCount() {
    return authFetch('/api/cart/count/')
        .then(response => response.json())
        .then(data => data.count || 0)
        .catch(error => {
            console.error('Ошибка получения количества корзины:', error);
            return 0;
        });
}

function updateCartBadge() {
    const badge = document.getElementById('cart-count');
    if (badge) {
        getCartCount().then(count => {
            badge.textContent = count;
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    updateCartBadge();
    
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
    `;
    document.head.appendChild(style);
});

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        authFetch,
        getProfile,
        updateProfile,
        getProducts,
        createProduct,
        getOrders,
        getOrderDetail,
        addToCart,
        getCartCount,
        updateCartBadge,
        showNotification,
    };
}