
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

function addToCart(productId, quantity = 1) {
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
            updateCartCount(data.cart_count);
        } else {
            showNotification('danger', data.error || 'Ошибка добавления в корзину');
        }
    })
    .catch(error => {
        showNotification('danger', 'Ошибка соединения с сервером');
        console.error('Error:', error);
    });
}

function showNotification(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 80px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function updateCartCount(count) {
    const cartBadge = document.getElementById('cart-count');
    if (cartBadge) {
        cartBadge.textContent = count;
    }
}
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
                        <button class="btn-add-to-cart" onclick="addToCart(${product.id})">
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
        
        // Рендерим товары
        products.forEach(product => {
            const col = document.createElement('div');
            col.className = 'col-md-4 col-sm-6 mb-4';
            col.innerHTML = `
                <div class="card product-card h-100">
                    ${product.image ? 
                        `<img src="${product.image}" class="card-img-top" alt="${product.name}" style="height: 200px; object-fit: cover;">` :
                        `<div class="card-img-top bg-light d-flex align-items-center justify-content-center" style="height: 200px;">
                            <i class="bi bi-image display-1 text-secondary"></i>
                        </div>`
                    }
                    <div class="card-body">
                        <h5 class="card-title">${product.name}</h5>
                        <p class="card-text text-truncate">${product.description || ''}</p>
                        <p class="product-price">${product.price} ₽</p>
                        <a href="/product/${product.slug}/" class="btn btn-outline-primary btn-sm">
                            <i class="bi bi-eye"></i> Подробнее
                        </a>
                        <button class="btn btn-primary btn-sm" onclick="addToCart(${product.id})">
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
        console.error('Error loading products:', error);
    }
}