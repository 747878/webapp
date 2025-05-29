// Prefix for localStorage keys to avoid conflicts
const CART_STORAGE_PREFIX = 'restaurant_cart_';

/**
 * Retrieves the cart from localStorage.
 * @returns {Array} An array of cart items.
 */
function getCart() {
    const cartJson = localStorage.getItem(CART_STORAGE_PREFIX + 'items');
    return cartJson ? JSON.parse(cartJson) : [];
}

/**
 * Saves the cart to localStorage.
 * @param {Array} cart - The cart array to save.
 */
function saveCart(cart) {
    localStorage.setItem(CART_STORAGE_PREFIX + 'items', JSON.stringify(cart));
    updateCartDisplay(); // Update cart count in header or other UI elements
}

/**
 * Adds an item to the cart or updates its quantity if it already exists.
 * @param {string|number} menuItemId - The ID of the menu item.
 * @param {string} name - The name of the menu item.
 * @param {number} price - The price of the menu item.
 * @param {string|object} [customizations] - Optional customizations for the item.
 * @param {number} [quantity=1] - Optional quantity to add.
 */
function addToCart(menuItemId, name, price, customizations = '', quantity = 1) {
    const cart = getCart();
    const existingItemIndex = cart.findIndex(item => item.menuItemId === menuItemId && JSON.stringify(item.customizations) === JSON.stringify(customizations));

    if (existingItemIndex > -1) {
        cart[existingItemIndex].quantity += quantity;
    } else {
        cart.push({ menuItemId, name, price, customizations, quantity });
    }
    saveCart(cart);
    console.log(`${name} added to cart. Current cart:`, getCart());
    alert(`${name} added to cart!`); // Simple feedback
}

/**
 * Updates the quantity of a specific item in the cart.
 * Removes the item if the new quantity is zero or less.
 * @param {string|number} menuItemId - The ID of the menu item.
 * @param {number} newQuantity - The new quantity for the item.
 * @param {string|object} [customizations] - Optional customizations for the item (to identify unique items).
 */
function updateQuantity(menuItemId, newQuantity, customizations = '') {
    let cart = getCart();
    const itemIndex = cart.findIndex(item => item.menuItemId === menuItemId && JSON.stringify(item.customizations) === JSON.stringify(customizations));

    if (itemIndex > -1) {
        if (newQuantity > 0) {
            cart[itemIndex].quantity = newQuantity;
        } else {
            cart.splice(itemIndex, 1); // Remove item if quantity is 0 or less
        }
        saveCart(cart);
        console.log(`Quantity updated for ${menuItemId}. New cart:`, getCart());
        // If on Your_order.html, re-render the cart display
        if (typeof renderCartItemsOnPage === 'function') {
            renderCartItemsOnPage();
        }
    }
}

/**
 * Removes an item from the cart completely.
 * @param {string|number} menuItemId - The ID of the menu item.
 * @param {string|object} [customizations] - Optional customizations for the item.
 */
function removeFromCart(menuItemId, customizations = '') {
    let cart = getCart();
    const itemIndex = cart.findIndex(item => item.menuItemId === menuItemId && JSON.stringify(item.customizations) === JSON.stringify(customizations));

    if (itemIndex > -1) {
        cart.splice(itemIndex, 1);
        saveCart(cart);
        console.log(`Item ${menuItemId} removed. New cart:`, getCart());
        // If on Your_order.html, re-render the cart display
        if (typeof renderCartItemsOnPage === 'function') {
            renderCartItemsOnPage();
        }
    }
}

/**
 * Calculates the total price of all items in the cart.
 * @returns {number} The total price.
 */
function getCartTotal() {
    const cart = getCart();
    return cart.reduce((total, item) => total + (item.price * item.quantity), 0);
}

/**
 * Gets the total number of individual items in the cart (sum of quantities).
 * @returns {number} The total item count.
 */
function getCartItemCount() {
    const cart = getCart();
    return cart.reduce((count, item) => count + item.quantity, 0);
}

/**
 * Clears all items from the cart in localStorage.
 */
function clearCart() {
    localStorage.removeItem(CART_STORAGE_PREFIX + 'items');
    saveCart([]); // Save an empty cart to trigger UI updates
    console.log('Cart cleared.');
    // If on Your_order.html, re-render the cart display (which should show empty)
    if (typeof renderCartItemsOnPage === 'function') {
        renderCartItemsOnPage();
    }
}

/**
 * Updates the cart display (e.g., item count in header).
 * This function should be called whenever the cart changes.
 */
function updateCartDisplay() {
    const cartItemCount = getCartItemCount();
    // Attempt to find cart count elements in any of the known structures
    const cartButtons = document.querySelectorAll('button span.truncate, a span.truncate');
    cartButtons.forEach(span => {
        // More specific targeting for "Cart (X)"
        if (span.textContent.toLowerCase().startsWith('cart')) {
            span.textContent = `Cart (${cartItemCount})`;
        }
        // For the specific structure in Your_order.html header
        if (span.parentElement && span.parentElement.textContent.toLowerCase().includes('cart')) {
             span.textContent = `Cart (${cartItemCount})`;
        }
    });

     // Update the cart count in the specific header location in Your_order.html
    const cartButtonYourOrder = document.querySelector('#cart-button-your-order span.truncate');
    if (cartButtonYourOrder) {
        cartButtonYourOrder.textContent = `Cart (${cartItemCount})`;
    }
}

// Initial update of cart display on page load
document.addEventListener('DOMContentLoaded', () => {
    updateCartDisplay();
});
