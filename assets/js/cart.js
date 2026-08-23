// Panier partagé entre les pages, stocké en localStorage.
(function (window) {
  const STORAGE_KEY = 'devercinge_cart';

  function parsePrice(priceStr) {
    return parseFloat(String(priceStr).replace('€', '').replace(',', '.').trim()) || 0;
  }

  function formatPrice(value) {
    return value.toFixed(2).replace('.', ',') + ' €';
  }

  function getCart() {
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch (e) {
      return [];
    }
  }

  function saveCart(cart) {
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(cart));
    } catch (e) {
      /* localStorage indisponible (navigation privée, etc.) : on ignore. */
    }
    updateCartBadges();
  }

  function addToCart(item) {
    const cart = getCart();
    const key = item.id + '__' + item.size;
    const existing = cart.find(function (line) { return line.id + '__' + line.size === key; });
    if (existing) {
      existing.qty += item.qty;
    } else {
      cart.push(item);
    }
    saveCart(cart);
  }

  function updateLineQty(index, qty) {
    const cart = getCart();
    if (!cart[index]) return;
    if (qty <= 0) {
      cart.splice(index, 1);
    } else {
      cart[index].qty = qty;
    }
    saveCart(cart);
  }

  function removeLine(index) {
    const cart = getCart();
    cart.splice(index, 1);
    saveCart(cart);
  }

  function clearCart() {
    saveCart([]);
  }

  function cartCount() {
    return getCart().reduce(function (sum, line) { return sum + line.qty; }, 0);
  }

  function cartTotal() {
    return getCart().reduce(function (sum, line) { return sum + line.priceValue * line.qty; }, 0);
  }

  function updateCartBadges() {
    const count = cartCount();
    document.querySelectorAll('[data-cart-badge]').forEach(function (el) {
      el.textContent = count;
      el.style.display = count > 0 ? 'inline-flex' : 'none';
    });
  }

  window.DevercingeCart = {
    parsePrice: parsePrice,
    formatPrice: formatPrice,
    getCart: getCart,
    addToCart: addToCart,
    updateLineQty: updateLineQty,
    removeLine: removeLine,
    clearCart: clearCart,
    cartCount: cartCount,
    cartTotal: cartTotal,
    updateCartBadges: updateCartBadges
  };

  document.addEventListener('DOMContentLoaded', updateCartBadges);
})(window);
