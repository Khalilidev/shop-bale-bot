// ========================================
// State
// ========================================
let state = {
    products: [],
    cart: [],
    currentCategory: 'all',
    loading: false
};

// ========================================
// DOM Elements
// ========================================
const DOM = {
    categoriesContainer: document.getElementById('categoriesContainer'),
    productsGrid: document.getElementById('productsGrid'),
    productsTitle: document.getElementById('productsTitle'),
    cartBadge: document.getElementById('cartBadge'),
    cartSidebar: document.getElementById('cartSidebar'),
    cartOverlay: document.getElementById('cartOverlay'),
    cartItems: document.getElementById('cartItems'),
    cartTotal: document.getElementById('cartTotal'),
    checkoutBtn: document.getElementById('checkoutBtn'),
    toastContainer: document.getElementById('toastContainer'),
    loadingOverlay: document.getElementById('loadingOverlay')
};

// ========================================
// Toast System
// ========================================
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        info: 'fa-info-circle',
        warning: 'fa-exclamation-triangle'
    };
    
    toast.innerHTML = `
        <i class="fas ${icons[type] || icons.info}"></i>
        <span>${message}</span>
    `;
    
    DOM.toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100px)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ========================================
// Loading
// ========================================
function showLoading() {
    DOM.loadingOverlay.classList.add('show');
}

function hideLoading() {
    DOM.loadingOverlay.classList.remove('show');
}

// ========================================
// Cart Functions
// ========================================
function getCartTotal() {
    return state.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
}

function getCartCount() {
    return state.cart.reduce((sum, item) => sum + item.quantity, 0);
}

function updateCartUI() {
    const count = getCartCount();
    DOM.cartBadge.textContent = count;
    DOM.cartBadge.style.display = count > 0 ? 'flex' : 'none';
    
    // Update cart items
    if (state.cart.length === 0) {
        DOM.cartItems.innerHTML = `
            <div class="empty-cart">
                <i class="fas fa-shopping-bag"></i>
                <p>سبد خرید خالی است</p>
            </div>
        `;
        DOM.checkoutBtn.disabled = true;
    } else {
        DOM.cartItems.innerHTML = state.cart.map(item => `
            <div class="cart-item" data-id="${item.id}">
                <div class="cart-item-image">
                    ${item.image_url ? `<img src="${item.image_url}" alt="${item.name}">` : 
                    `<i class="fas fa-box" style="display:flex;align-items:center;justify-content:center;width:100%;height:100%;color:#ccc;"></i>`}
                </div>
                <div class="cart-item-info">
                    <div class="cart-item-name">${item.name}</div>
                    <div class="cart-item-price">${item.price.toLocaleString()} تومان</div>
                    <div class="cart-item-qty">
                        <button onclick="updateCartQty(${item.id}, -1)">−</button>
                        <span>${item.quantity}</span>
                        <button onclick="updateCartQty(${item.id}, 1)">+</button>
                    </div>
                </div>
                <div class="cart-item-remove" onclick="removeFromCart(${item.id})">
                    <i class="fas fa-trash-alt"></i>
                </div>
            </div>
        `).join('');
        DOM.checkoutBtn.disabled = false;
    }
    
    DOM.cartTotal.textContent = getCartTotal().toLocaleString() + ' تومان';
}

function updateCartQty(productId, delta) {
    const item = state.cart.find(i => i.id === productId);
    if (!item) return;
    
    const newQty = item.quantity + delta;
    if (newQty <= 0) {
        removeFromCart(productId);
        return;
    }
    
    // Check stock
    const product = state.products.find(p => p.id === productId);
    if (product && newQty > product.stock) {
        showToast('موجودی کافی نیست!', 'error');
        return;
    }
    
    item.quantity = newQty;
    updateCartUI();
    updateProductButtons();
}

function removeFromCart(productId) {
    state.cart = state.cart.filter(item => item.id !== productId);
    updateCartUI();
    updateProductButtons();
    showToast('محصول از سبد خرید حذف شد', 'info');
}

function addToCart(productId) {
    const product = state.products.find(p => p.id === productId);
    if (!product) return;
    
    if (product.stock <= 0) {
        showToast('این محصول موجود نیست!', 'error');
        return;
    }
    
    const existing = state.cart.find(item => item.id === productId);
    
    if (existing) {
        if (existing.quantity >= product.stock) {
            showToast('موجودی کافی نیست!', 'error');
            return;
        }
        existing.quantity++;
    } else {
        state.cart.push({
            id: product.id,
            name: product.name,
            price: product.price,
            image_url: product.image_url,
            quantity: 1
        });
    }
    
    updateCartUI();
    updateProductButtons();
    showToast(`${product.name} به سبد خرید اضافه شد`, 'success');
}

function toggleCart() {
    const isOpen = DOM.cartSidebar.classList.contains('open');
    DOM.cartSidebar.classList.toggle('open', !isOpen);
    DOM.cartOverlay.classList.toggle('show', !isOpen);
}

// ========================================
// Product UI Functions
// ========================================
function updateProductButtons() {
    document.querySelectorAll('.btn-add').forEach(btn => {
        const id = parseInt(btn.dataset.id);
        const inCart = state.cart.find(i => i.id === id);
        const product = state.products.find(p => p.id === id);
        
        if (inCart) {
            btn.textContent = `✓ ${inCart.quantity}`;
            btn.classList.add('added');
        } else {
            btn.textContent = '➕ افزودن';
            btn.classList.remove('added');
        }
        
        if (product && product.stock <= 0) {
            btn.disabled = true;
            btn.textContent = 'ناموجود';
        } else {
            btn.disabled = false;
        }
    });
}

function renderProducts(products, title = 'همه محصولات') {
    DOM.productsTitle.textContent = title;
    
    if (products.length === 0) {
        DOM.productsGrid.innerHTML = `
            <div style="grid-column:1/-1;text-align:center;padding:40px 0;color:var(--gray-400);">
                <i class="fas fa-box-open" style="font-size:48px;display:block;margin-bottom:12px;"></i>
                <p>هیچ محصولی در این دسته‌بندی یافت نشد.</p>
            </div>
        `;
        return;
    }
    
    DOM.productsGrid.innerHTML = products.map(product => `
        <div class="product-card" onclick="showProductDetail(${product.id})">
            <div class="product-image">
                ${product.image_url ? 
                    `<img src="${product.image_url}" alt="${product.name}" loading="lazy">` : 
                    `<i class="fas fa-box no-image"></i>`
                }
            </div>
            <div class="product-info">
                <div class="product-name">${product.name}</div>
                <div class="product-brand">${product.brand}</div>
                <div class="product-price">${product.price.toLocaleString()} <span>تومان</span></div>
                <div class="product-stock ${product.stock <= 5 ? (product.stock <= 0 ? 'out' : 'low') : ''}">
                    موجودی: ${product.stock} عدد
                </div>
                <div class="product-actions">
                    <button class="btn-add" data-id="${product.id}" onclick="event.stopPropagation();addToCart(${product.id})">
                        ➕ افزودن
                    </button>
                </div>
            </div>
        </div>
    `).join('');
    
    updateProductButtons();
}

function renderCategories(categories) {
    let html = `
        <button class="category-btn all-btn active" data-category="all" onclick="filterProducts('all')">
            <i class="fas fa-th-list"></i> همه
        </button>
    `;
    
    categories.forEach(cat => {
        html += `
            <button class="category-btn" data-category="${cat}" onclick="filterProducts('${cat}')">
                ${cat}
            </button>
        `;
    });
    
    DOM.categoriesContainer.innerHTML = html;
}

// ========================================
// Product Filter
// ========================================
function filterProducts(category) {
    state.currentCategory = category;
    
    // Update active state
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.category === category);
    });
    
    let products;
    let title;
    
    if (category === 'all') {
        products = state.products;
        title = 'همه محصولات';
    } else {
        products = state.products.filter(p => p.category === category);
        title = `دسته‌بندی: ${category}`;
    }
    
    renderProducts(products, title);
}

// ========================================
// Product Detail Modal
// ========================================
function showProductDetail(productId) {
    const product = state.products.find(p => p.id === productId);
    if (!product) return;
    
    const modal = document.createElement('div');
    modal.className = 'product-modal-overlay';
    modal.id = 'productModal';
    modal.onclick = (e) => {
        if (e.target === modal) closeModal();
    };
    
    modal.innerHTML = `
        <div class="product-modal">
            <div class="modal-image">
                ${product.image_url ? 
                    `<img src="${product.image_url}" alt="${product.name}">` : 
                    `<i class="fas fa-box" style="display:flex;align-items:center;justify-content:center;width:100%;height:100%;font-size:60px;color:#ccc;"></i>`
                }
            </div>
            <div class="modal-name">${product.name}</div>
            <div class="modal-brand">🏷️ ${product.brand}</div>
            <div class="modal-price">${product.price.toLocaleString()} تومان</div>
            ${product.description ? `<div class="modal-desc">${product.description}</div>` : ''}
            <div class="modal-stock">📦 موجودی: ${product.stock} عدد</div>
            <div class="modal-actions">
                <button class="modal-close" onclick="closeModal()">بستن</button>
                <button class="modal-add" onclick="addToCart(${product.id});closeModal();">
                    ➕ افزودن به سبد خرید
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    const modal = document.getElementById('productModal');
    if (modal) {
        modal.remove();
        document.body.style.overflow = '';
    }
}
async function checkout() {
    if (state.cart.length === 0) {
        showToast('سبد خرید خالی است!', 'warning');
        return;
    }
    
    // ۱. دریافت نام و شماره تلفن از فیلدهای فرم جدید
    const nameInput = document.getElementById('customerName').value.trim();
    const phoneInput = document.getElementById('customerPhone').value.trim();
    
    // ۲. اعتبارسنجی پر بودن اطلاعات فرم
    if (!nameInput || !phoneInput) {
        showToast('لطفاً نام و شماره تماس خود را وارد کنید.', 'error');
        return;
    }
    
    // ۳. بررسی مجدد موجودی انبار پیش از ارسال درخواست[cite: 4]
    for (const item of state.cart) {
        const product = state.products.find(p => p.id === item.id);
        if (!product || product.stock < item.quantity) {
            showToast(`موجودی ${product ? product.name : 'محصول'} کافی نیست!`, 'error');
            return;
        }
    }
    
    const total = getCartTotal();
    const items = state.cart.map(item => ({
        product_id: item.id,
        quantity: item.quantity
    }));
    
    // ۴. دریافت آیدی کاربر از پارامتر startapp در آدرس URL[cite: 4]
    const urlParams = new URLSearchParams(window.location.search);
    const userId = urlParams.get('startapp') || 'unknown';
    
    showLoading();
    
    try {
        const response = await fetch('/api/order', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: parseInt(userId) || 0,
                customer_name: nameInput,
                customer_phone: phoneInput,
                items: items,
                total_price: total
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast(result.message, 'success');
            
            // خالی کردن سبد خرید و فرم[cite: 4]
            state.cart = [];
            document.getElementById('customerName').value = '';
            document.getElementById('customerPhone').value = '';
            
            // بروزرسانی رابط کاربری[cite: 4]
            updateCartUI();
            updateProductButtons();
            toggleCart();
        } else {
            showToast(result.message || 'خطا در ثبت سفارش', 'error');
        }
    } catch (error) {
        console.error('Checkout error:', error);
        showToast('خطا در ارتباط با سرور!', 'error');
    } finally {
        hideLoading();
    }
}
// ========================================
// Load Products
// ========================================
async function loadProducts() {
    try {
        const response = await fetch('/api/products');
        state.products = await response.json();
        
        // Load categories
        const catResponse = await fetch('/api/categories');
        const categories = await catResponse.json();
        renderCategories(categories.categories || []);
        
        renderProducts(state.products);
    } catch (error) {
        console.error('Error loading products:', error);
        showToast('خطا در بارگذاری محصولات!', 'error');
    }
}

// ========================================
// Init
// ========================================
document.addEventListener('DOMContentLoaded', () => {
    loadProducts();
    
    // Close cart on Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            if (DOM.cartSidebar.classList.contains('open')) {
                toggleCart();
            }
            closeModal();
        }
    });
});