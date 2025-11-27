// static/js/carrito.js

class CarritoManager {
    constructor() {
        this.init();
    }

    init() {
        this.actualizarContador();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Botones de agregar al carrito
        document.querySelectorAll('.btn-agregar-carrito').forEach(btn => {
            btn.addEventListener('click', (e) => this.agregarAlCarrito(e));
        });

        // Botones de actualizar cantidad
        document.querySelectorAll('.btn-actualizar-cantidad').forEach(btn => {
            btn.addEventListener('click', (e) => this.actualizarCantidad(e));
        });

        // Botones de eliminar item
        document.querySelectorAll('.btn-eliminar-item').forEach(btn => {
            btn.addEventListener('click', (e) => this.eliminarItem(e));
        });

        // Inputs de cantidad
        document.querySelectorAll('.input-cantidad').forEach(input => {
            input.addEventListener('change', (e) => this.cambiarCantidad(e));
        });

        // Botón vaciar carrito
        const btnVaciar = document.getElementById('btn-vaciar-carrito');
        if (btnVaciar) {
            btnVaciar.addEventListener('click', () => this.vaciarCarrito());
        }
    }

    async agregarAlCarrito(event) {
        event.preventDefault();
        const btn = event.currentTarget;
        const idProducto = btn.dataset.productoId;
        const cantidad = btn.dataset.cantidad || 1;

        try {
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Agregando...';

            const formData = new FormData();
            formData.append('cantidad', cantidad);

            const response = await fetch(`/agregar-carrito/${idProducto}`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (data.status === 'ok') {
                this.mostrarNotificacion('✓ Producto agregado al carrito', 'success');
                this.actualizarContador();
                
                // Efecto visual
                btn.innerHTML = '<i class="fas fa-check"></i> Agregado';
                setTimeout(() => {
                    btn.innerHTML = '<i class="fas fa-cart-plus"></i> Agregar al carrito';
                    btn.disabled = false;
                }, 2000);
            } else {
                throw new Error(data.msg);
            }

        } catch (error) {
            this.mostrarNotificacion('✗ ' + error.message, 'error');
            btn.innerHTML = '<i class="fas fa-cart-plus"></i> Agregar al carrito';
            btn.disabled = false;
        }
    }

    async actualizarCantidad(event) {
        event.preventDefault();
        const btn = event.currentTarget;
        const idProducto = btn.dataset.productoId;
        const input = document.querySelector(`#cantidad-${idProducto}`);
        const cantidad = parseInt(input.value);

        if (cantidad < 1) {
            this.mostrarNotificacion('La cantidad debe ser mayor a 0', 'warning');
            return;
        }

        try {
            const formData = new FormData();
            formData.append('cantidad', cantidad);

            const response = await fetch(`/carrito/actualizar/${idProducto}`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (data.status === 'ok') {
                location.reload(); // Recargar para actualizar totales
            } else {
                throw new Error(data.msg);
            }

        } catch (error) {
            this.mostrarNotificacion('✗ ' + error.message, 'error');
        }
    }

    async cambiarCantidad(event) {
        const input = event.target;
        const idProducto = input.dataset.productoId;
        const cantidad = parseInt(input.value);
        const precioUnitario = parseFloat(input.dataset.precio);

        // Actualizar subtotal en la UI
        const subtotalElement = document.querySelector(`#subtotal-${idProducto}`);
        if (subtotalElement) {
            const subtotal = cantidad * precioUnitario;
            subtotalElement.textContent = `$${subtotal.toFixed(2)}`;
        }

        // Actualizar total general
        this.actualizarTotalGeneral();
    }

    async eliminarItem(event) {
        event.preventDefault();
        
        if (!confirm('¿Estás seguro de eliminar este producto del carrito?')) {
            return;
        }

        const btn = event.currentTarget;
        const idProducto = btn.dataset.productoId;

        try {
            const response = await fetch(`/carrito/eliminar/${idProducto}`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (data.status === 'ok') {
                // Remover elemento del DOM con animación
                const item = btn.closest('.carrito-item');
                item.style.opacity = '0';
                item.style.transform = 'translateX(-20px)';
                
                setTimeout(() => {
                    item.remove();
                    this.actualizarContador();
                    this.actualizarTotalGeneral();
                    
                    // Si no hay más items, mostrar mensaje vacío
                    if (document.querySelectorAll('.carrito-item').length === 0) {
                        location.reload();
                    }
                }, 300);

                this.mostrarNotificacion('Producto eliminado', 'success');
            } else {
                throw new Error(data.msg);
            }

        } catch (error) {
            this.mostrarNotificacion('✗ ' + error.message, 'error');
        }
    }

    async vaciarCarrito() {
        if (!confirm('¿Estás seguro de vaciar todo el carrito?')) {
            return;
        }

        try {
            const response = await fetch('/carrito/vaciar', {
                method: 'POST'
            });

            if (response.ok) {
                location.reload();
            }

        } catch (error) {
            this.mostrarNotificacion('Error al vaciar el carrito', 'error');
        }
    }

    async actualizarContador() {
        try {
            const response = await fetch('/api/carrito/cantidad');
            const data = await response.json();
            
            const contador = document.querySelector('.carrito-contador');
            if (contador) {
                contador.textContent = data.cantidad;
                contador.style.display = data.cantidad > 0 ? 'inline-block' : 'none';
            }

        } catch (error) {
            console.error('Error al actualizar contador:', error);
        }
    }

    actualizarTotalGeneral() {
        const items = document.querySelectorAll('.carrito-item');
        let total = 0;

        items.forEach(item => {
            const input = item.querySelector('.input-cantidad');
            if (input) {
                const cantidad = parseInt(input.value);
                const precio = parseFloat(input.dataset.precio);
                total += cantidad * precio;
            }
        });

        const totalElement = document.querySelector('#total-carrito');
        if (totalElement) {
            totalElement.textContent = `$${total.toFixed(2)}`;
        }
    }

    mostrarNotificacion(mensaje, tipo = 'info') {
        // Crear notificación
        const notif = document.createElement('div');
        notif.className = `notificacion notificacion-${tipo}`;
        notif.textContent = mensaje;
        notif.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            background: ${tipo === 'success' ? '#10b981' : tipo === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 9999;
            animation: slideIn 0.3s ease-out;
        `;

        document.body.appendChild(notif);

        setTimeout(() => {
            notif.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => notif.remove(), 300);
        }, 3000);
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new CarritoManager();
});

// Estilos para animaciones
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .carrito-item {
        transition: all 0.3s ease;
    }
`;
document.head.appendChild(style);