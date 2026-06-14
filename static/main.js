// Pramod General Store - Upgraded Smart Shopping Cart & UI Operations

// In-Memory Cart State (Linked with LocalStorage)
let cart = JSON.parse(localStorage.getItem('pramod_store_cart')) || [];

// Cart threshold configurations (will fallback if settings injected fail)
const DELIVERY_CHARGE = 30;
const FREE_DELIVERY_THRESHOLD = 500;

// Add item to basket
function addToCart(id, name, price, maxStock) {
    const existing = cart.find(item => item.id === id);
    
    if (existing) {
        if (existing.quantity < maxStock) {
            existing.quantity += 1;
        } else {
            alert(`Sorry! Only ${maxStock} units of this item are available in stock.`);
            return;
        }
    } else {
        cart.push({
            id: id,
            name: name,
            price: price,
            quantity: 1,
            maxStock: maxStock
        });
    }
    
    saveCart();
    renderCart();
}

// Update quantity from input
function updateQty(id, newQty) {
    const item = cart.find(item => item.id === id);
    if (!item) return;
    
    newQty = parseInt(newQty);
    if (isNaN(newQty) || newQty < 1) {
        newQty = 1;
    }
    
    if (newQty > item.maxStock) {
        alert(`Only ${item.maxStock} units of this item are available in stock.`);
        newQty = item.maxStock;
    }
    
    item.quantity = newQty;
    saveCart();
    renderCart();
}

// Remove item from basket
function removeFromCart(id) {
    cart = cart.filter(item => item.id !== id);
    saveCart();
    renderCart();
}

// Save cart to LocalStorage
function saveCart() {
    localStorage.setItem('pramod_store_cart', JSON.stringify(cart));
}

// Render Shopping Cart Drawer view
function renderCart() {
    const listContainer = document.getElementById('cart-items-list');
    const badge = document.getElementById('cart-badge');
    const subtotalLabel = document.getElementById('cart-subtotal');
    const shippingLabel = document.getElementById('cart-shipping');
    const totalLabel = document.getElementById('cart-total');
    const tipBanner = document.getElementById('delivery-tip-banner');
    const formInput = document.getElementById('cart-form-input');
    
    if (!listContainer) return; // If on admin view
    
    listContainer.innerHTML = "";
    
    if (cart.length === 0) {
        const emptyMsg = document.getElementById('cart-empty-message');
        if (emptyMsg) emptyMsg.style.display = 'block';
        if (badge) badge.innerText = "0";
        if (subtotalLabel) subtotalLabel.innerText = "₹0";
        if (shippingLabel) shippingLabel.innerText = "₹0";
        if (totalLabel) totalLabel.innerText = "₹0";
        if (tipBanner) tipBanner.innerText = "Add ₹500 for FREE delivery!";
        if (formInput) formInput.value = "";
        return;
    }
    
    const emptyMsg = document.getElementById('cart-empty-message');
    if (emptyMsg) emptyMsg.style.display = 'none';
    
    let subtotal = 0;
    let totalQty = 0;
    
    cart.forEach(item => {
        const itemCost = item.price * item.quantity;
        subtotal += itemCost;
        totalQty += item.quantity;
        
        const row = document.createElement('div');
        row.className = "flex items-center justify-between p-3 bg-white rounded-xl border border-slate-100 shadow-sm text-xs font-semibold";
        row.innerHTML = `
            <div class="flex-grow pr-2">
                <span class="text-[#4E342E] block leading-tight font-bold">${item.name}</span>
                <span class="text-[10px] text-[#C65D2E] block mt-0.5">₹${item.price} each</span>
            </div>
            <div class="flex items-center space-x-2 shrink-0">
                <input type="number" value="${item.quantity}" min="1" max="${item.maxStock}" onchange="updateQty(${item.id}, this.value)" class="w-10 px-1.5 py-1 text-center bg-orange-50/50 border border-slate-200 rounded-lg focus:outline-none focus:border-[#C65D2E]">
                <button onclick="removeFromCart(${item.id})" class="text-rose-500 hover:text-rose-700 transition-colors p-1">
                    <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
                </button>
            </div>
        `;
        listContainer.appendChild(row);
    });
    
    // Calculate shipping from configurations or fallbacks
    const charge = typeof settings !== 'undefined' ? settings.delivery_charge : DELIVERY_CHARGE;
    const threshold = typeof settings !== 'undefined' ? settings.free_delivery_threshold : FREE_DELIVERY_THRESHOLD;
    
    const shipping = subtotal >= threshold ? 0 : charge;
    const grandTotal = subtotal + shipping;
    
    // Update labels
    if (badge) badge.innerText = totalQty;
    if (subtotalLabel) subtotalLabel.innerText = `₹${subtotal.toLocaleString()}`;
    if (shippingLabel) shippingLabel.innerText = shipping === 0 ? "FREE" : `₹${shipping}`;
    if (totalLabel) totalLabel.innerText = `₹${grandTotal.toLocaleString()}`;
    
    if (tipBanner) {
        if (subtotal >= threshold) {
            tipBanner.innerText = "🎉 Congratulations! You have unlocked FREE delivery.";
            tipBanner.className = "text-[9px] text-emerald-600 font-extrabold uppercase tracking-wider text-center";
        } else {
            const diff = threshold - subtotal;
            tipBanner.innerText = `Add ₹${diff} more to unlock FREE delivery!`;
            tipBanner.className = "text-[9px] text-[#C65D2E] font-bold uppercase tracking-wider text-center";
        }
    }
    
    // Serialize to form input
    if (formInput) {
        formInput.value = JSON.stringify(cart);
    }
    
    lucide.createIcons();
}

// Payment selectors toggle handler
function togglePaymentSelection() {
    const methodEl = document.getElementById('payment_method');
    if (!methodEl) return;
    
    const method = methodEl.value;
    const notice = document.getElementById('payment-notice');
    const form = document.getElementById('checkout-form');
    const submitBtn = form.querySelector('button[type="submit"]');
    
    if (!notice || !submitBtn) return;
    
    notice.classList.add('hidden');
    submitBtn.innerText = "Place Order (COD)";
    
    if (method === "Cash on Delivery") {
        submitBtn.innerText = "Place Order (COD)";
    } else if (method === "UPI") {
        submitBtn.innerText = "Place Order (UPI)";
        notice.classList.remove('hidden');
        notice.innerHTML = `
            <span class="font-bold text-amber-900 block mb-0.5">UPI Payment details</span>
            A UPI payment link will be shared to your registered mobile number upon dispatch. Please pay once your order arrives.
        `;
    } else if (method === "QR Payment") {
        submitBtn.innerText = "Generate QR Code";
        notice.classList.remove('hidden');
        notice.innerHTML = `
            <span class="font-bold text-amber-900 block mb-0.5">Scan & Pay</span>
            Clicking "Generate QR Code" will open a secure local merchant QR code for instant village UPI scanning.
        `;
    } else if (method === "Razorpay") {
        submitBtn.innerText = "Pay via Razorpay Secure";
        notice.classList.remove('hidden');
        notice.innerHTML = `
            <span class="font-bold text-blue-900 block mb-0.5">Razorpay Online Gateway</span>
            Processes immediate debit card, credit card, netbanking, or UPI payments with processing status logs.
        `;
    } else if (method === "Khata Credit") {
        submitBtn.innerText = "Charge to Bahi Khata";
        notice.classList.remove('hidden');
        notice.innerHTML = `
            <span class="font-bold text-[#8D230F] block mb-0.5">Bahi Khata Credit Terms</span>
            By charging this order to credit, it will automatically record outstanding dues under your family account. Please settle dues monthly.
        `;
    }
}

// Checkout validations
function validateCheckoutForm(e) {
    if (cart.length === 0) {
        alert("Your shopping cart is empty!");
        return false;
    }
    
    const method = document.getElementById('payment_method').value;
    
    if (method === "QR Payment") {
        openQrModal();
        return false; // Prevent immediate submission
    }
    
    if (method === "Razorpay") {
        openRazorpayModal();
        return false; // Prevent immediate submission to allow simulation
    }
    
    // Clear cart on successful submit
    setTimeout(() => {
        cart = [];
        saveCart();
    }, 100);
    
    return true;
}

// Modal QR Controls
function openQrModal() {
    const totalLabel = document.getElementById('cart-total').innerText;
    document.getElementById('qr-amount-label').innerText = totalLabel;
    document.getElementById('qr-modal').classList.remove('hidden');
}

// Modal Razorpay controls
function openRazorpayModal() {
    const totalLabel = document.getElementById('cart-total').innerText;
    document.getElementById('razorpay-amount-label').innerText = totalLabel;
    
    // Clear previous inputs
    document.getElementById('rzp-card-no').value = "";
    document.getElementById('rzp-expiry').value = "";
    document.getElementById('rzp-cvv').value = "";
    
    // Reset status overlay screen
    document.getElementById('rzp-status-screen').classList.add('hidden');
    document.getElementById('rzp-spinner').classList.remove('hidden');
    document.getElementById('rzp-success-icon').classList.add('hidden');
    
    document.getElementById('razorpay-modal').classList.remove('hidden');
}

function closeRazorpayModal() {
    document.getElementById('razorpay-modal').classList.add('hidden');
}

function submitRazorpaySimulate() {
    const cardNo = document.getElementById('rzp-card-no').value.trim();
    const expiry = document.getElementById('rzp-expiry').value.trim();
    const cvv = document.getElementById('rzp-cvv').value.trim();
    
    if (cardNo === "" || expiry === "" || cvv === "") {
        alert("Please enter all card details to process payment simulation.");
        return;
    }
    
    // Show loading overlay inside modal
    const overlay = document.getElementById('rzp-status-screen');
    const title = document.getElementById('rzp-status-title');
    const desc = document.getElementById('rzp-status-desc');
    const spinner = document.getElementById('rzp-spinner');
    const successIcon = document.getElementById('rzp-success-icon');
    
    title.innerText = "Processing transaction...";
    desc.innerText = "Communicating with bank payment systems.";
    overlay.classList.remove('hidden');
    
    // Simulate delay for authorization
    setTimeout(() => {
        title.innerText = "Authorizing credit limit...";
        desc.innerText = "Awaiting response code from merchant bank.";
        
        setTimeout(() => {
            // Success state
            spinner.classList.add('hidden');
            successIcon.classList.remove('hidden');
            title.innerText = "Payment Successful!";
            desc.innerText = "Transaction ID: TXN_RZP_" + Math.floor(Math.random() * 900000 + 100000);
            
            // Clear cart
            cart = [];
            saveCart();
            
            setTimeout(() => {
                // Submit form
                closeRazorpayModal();
                const form = document.getElementById('checkout-form');
                form.onsubmit = null; // Remove validation intercept
                form.submit();
            }, 1000);
            
        }, 1500);
    }, 1000);
}

function closeQrModal() {
    document.getElementById('qr-modal').classList.add('hidden');
}

function confirmQrPaymentSubmit() {
    cart = [];
    saveCart();
    
    closeQrModal();
    const form = document.getElementById('checkout-form');
    form.onsubmit = null;
    form.submit();
}

// Document loaded event
document.addEventListener('DOMContentLoaded', () => {
    renderCart();
    togglePaymentSelection();
});
