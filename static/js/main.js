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

function addToCartHandler(productId, quantity = 1) {
    const csrfToken = getCsrfToken();
    fetch('/api/cart/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('success', data.message);
            updateCartBadge();
        } else {
            showNotification('danger', data.error || 'Ошибка добавления');
        }
    })
    .catch(error => {
        showNotification('danger', 'Ошибка соединения с сервером');
    });
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

function updateCartBadge() {
    const badge = document.getElementById('cart-count');
    if (badge) {
        fetch('/api/cart/count/')
            .then(response => response.json())
            .then(data => {
                badge.textContent = data.count || 0;
            })
            .catch(() => {});
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

async function loadProducts(filters = {}) {
    const container = document.getElementById('products-container');
    const spinner = document.getElementById('loading-spinner');
    if (!container) return;
    if (spinner) spinner.style.display = 'block';
    container.innerHTML = '';
    try {
        const params = new URLSearchParams(filters);
        const url = `/api/products/?${params.toString()}`;
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const products = await response.json();
        if (spinner) spinner.style.display = 'none';
        if (products.length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center py-5">
                    <i class="bi bi-box-seam display-1 text-muted"></i>
                    <p class="lead mt-3">Товары не найдены</p>
                </div>
            `;
            return;
        }
        products.forEach(product => {
            const col = document.createElement('div');
            col.className = 'col-md-4 col-sm-6 mb-4';
            col.innerHTML = `
                <div class="product-item">
                    ${product.product_photo ? 
                        `<img src="${product.product_photo}" class="card-img-top" alt="${product.title}" style="height: 200px; object-fit: cover;">` :
                        `<div class="card-img-top bg-light d-flex align-items-center justify-content-center" style="height: 200px;">
                            <i class="bi bi-image display-1 text-secondary"></i>
                        </div>`
                    }
                    <div class="product-list">
                        <h3>${product.title}</h3>
                        <div class="manufacturer">${product.manufacturer}</div>
                        <span class="price">${product.price} ₽</span>
                        <button class="btn-add-to-cart" onclick="addToCartHandler(${product.id})">
                            <i class="bi bi-cart-plus"></i> В корзину
                        </button>
                    </div>
                </div>
            `;
            container.appendChild(col);
        });
    } catch (error) {
        if (spinner) spinner.style.display = 'none';
        container.innerHTML = `
            <div class="col-12 text-center py-5">
                <i class="bi bi-exclamation-triangle display-1 text-danger"></i>
                <p class="lead mt-3 text-danger">Ошибка загрузки товаров</p>
                <p>${error.message}</p>
                <button class="btn btn-primary" onclick="location.reload()">
                    <i class="bi bi-arrow-clockwise"></i> Обновить
                </button>
            </div>
        `;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('form[method="post"]').forEach(form => {
        if (!form.querySelector('[name=csrfmiddlewaretoken]')) {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'csrfmiddlewaretoken';
            input.value = getCsrfToken();
            form.appendChild(input);
        }
    });
});