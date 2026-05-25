<script>
  import { cart, removeFromCart, updateCantidad } from '$lib/cart.svelte.js';

  // Calculamos los totales basándonos en el carrito global
  let subtotal = $derived(cart.items.reduce((suma, item) => suma + (item.precio * item.cantidad), 0));
  let costoEnvio = $derived(subtotal >= 150 || subtotal === 0 ? 0 : 80.00); 
  let total = $derived(subtotal + costoEnvio);
</script>

<div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-14 min-h-[80vh]">
  
  <h1 class="text-4xl font-light mb-14 tracking-widest uppercase">Tu Bolsa</h1>

  <div class="flex flex-col lg:flex-row gap-16 lg:gap-20">
    
    <div class="w-full lg:flex-1">
      {#if cart.items.length === 0}
        <div class="text-left py-10">
          <p class="text-gray-400 mb-6 font-light">No tienes artículos en tu bolsa.</p>
          <a href="/catalogo" class="btn btn-primary text-white rounded-md px-8 font-medium">Continuar Comprando</a>
        </div>
      {:else}
        <div class="flex flex-col gap-14">
          {#each cart.items as item}
            <div class="flex flex-col sm:flex-row gap-8 group">
              
              <img src={item.foto_url} alt={item.nombre} class="w-full sm:w-48 h-56 object-cover bg-base-200 rounded-md" />
              
              <div class="flex flex-col flex-1">
                <div class="flex justify-between items-start gap-4">
                  <div>
                    <h3 class="font-normal text-xl leading-tight mb-2 tracking-wide">{item.nombre}</h3>
                    <p class="text-sm font-light text-gray-400 tracking-wide">{item.marca}</p>
                    <span class="inline-block bg-base-200/50 text-gray-400 text-xs px-3 py-1 mt-4 rounded-sm font-light uppercase tracking-widest">
                      En Stock
                    </span>
                  </div>
                  
                  <div class="font-medium text-lg whitespace-nowrap">
                    ${(item.precio * item.cantidad).toFixed(2)}
                  </div>
                </div>

                <div class="mt-auto flex justify-between items-end pt-8">
                  
                  <div class="flex items-center border border-gray-600/30 rounded-full px-3 py-1">
                    <button onclick={() => updateCantidad(item.id, -1)} class="text-gray-400 hover:text-white px-3 py-1 font-light transition-colors">−</button>
                    <span class="w-8 text-center text-sm font-normal">{item.cantidad}</span>
                    <button onclick={() => updateCantidad(item.id, 1)} class="text-gray-400 hover:text-white px-3 py-1 font-light transition-colors">+</button>
                  </div>
                  
                  <button 
                    onclick={() => removeFromCart(item.id)} 
                    class="text-xs font-light text-gray-400 hover:text-white underline underline-offset-4 decoration-gray-600/50 transition-colors uppercase tracking-widest"
                  >
                    Eliminar
                  </button>
                  
                </div>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <div class="w-full lg:w-[420px] shrink-0">
      
      <div class="bg-base-200/30 rounded-2xl p-10 mb-6">
        <h2 class="text-lg font-light tracking-widest uppercase mb-10 text-gray-200">Resumen del Pedido</h2>
        
        <div class="space-y-6 text-base font-light text-gray-400 mb-10">
          <div class="flex justify-between items-center">
            <span>Subtotal</span>
            <span class="text-white">${subtotal.toFixed(2)}</span>
          </div>
          <div class="flex justify-between items-center">
            <span>Envío</span>
            {#if costoEnvio === 0}
              <span class="text-white font-medium uppercase tracking-widest text-sm">Gratis</span>
            {:else}
              <span class="text-white">${costoEnvio.toFixed(2)}</span>
            {/if}
          </div>
        </div>
        
        <div class="flex justify-between items-center border-t border-gray-600/20 pt-8 mb-10">
          <span class="text-sm font-light uppercase tracking-widest text-gray-400">Total</span>
          <span class="text-3xl font-medium text-white">${total.toFixed(2)}</span>
        </div>

        {#if cart.items.length > 0}
          <a 
            href="/pago"
            class="block w-full text-center bg-primary hover:bg-primary/90 text-white font-medium tracking-widest uppercase text-sm rounded-md py-5 transition-colors"
          >
            Pagar Ahora
          </a>
        {:else}
          <button 
            class="w-full bg-gray-600 cursor-not-allowed text-gray-400 font-medium tracking-widest uppercase text-sm rounded-md py-5"
            disabled
          >
            Bolsa Vacía
          </button>
        {/if}
        
        </div>
    </div>
  </div>
</div>