import { browser } from '$app/environment';

// 1. Inicializamos el estado leyendo el localStorage
let initialItems = [];
if (browser) {
    const saved = localStorage.getItem('cart');
    if (saved) {
        initialItems = JSON.parse(saved);
    }
}

export const cart = $state({ items: initialItems });

// Función interna para persistir los cambios
function sync() {
    if (browser) {
        localStorage.setItem('cart', JSON.stringify(cart.items));
    }
}

export function addToCart(product) {
    const existing = cart.items.find(i => i.id === product.id);
    if (existing) {
        existing.cantidad += 1;
    } else {
        cart.items.push({ ...product, cantidad: 1 });
    }
    sync(); // Guardamos automáticamente
}

export function removeFromCart(productId) {
    cart.items = cart.items.filter(item => item.id !== productId);
    sync(); // Guardamos automáticamente
}

// Nuevas funciones para manejar cantidades desde cualquier lugar
export function updateCantidad(id, delta) {
    const item = cart.items.find(i => i.id === id);
    if (item) {
        item.cantidad += delta;
        if (item.cantidad <= 0) {
            removeFromCart(id);
        } else {
            sync();
        }
    }
}

export function getTotalItems() {
    return cart.items.reduce((acc, item) => acc + item.cantidad, 0);
}