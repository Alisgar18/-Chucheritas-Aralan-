<script>
  let metodoPago = $state('tarjeta'); 
  
  let nombre = $state('');
  let direccion = $state('');
  let ciudad = $state('');
  let codigoPostal = $state('');

  let itemsCarrito = $state([
    {
      id_producto: 1,
      nombre: "Lip Oil Hidratante",
      marca: "Beauty Creations",
      precio: 75.00,
      cantidad: 2,
      foto_url: "https://placehold.co/400x500/2a2a2a/ffffff?text=Lip+Oil" 
    },
    {
      id_producto: 4,
      nombre: "Mascarilla Facial",
      marca: "Bioaqua",
      precio: 25.00,
      cantidad: 1,
      foto_url: "https://placehold.co/400x500/2a2a2a/ffffff?text=Mascarilla"
    }
  ]);

  let subtotal = $derived(itemsCarrito.reduce((suma, item) => suma + (item.precio * item.cantidad), 0));
  let costoEnvio = $derived(subtotal >= 150 || subtotal === 0 ? 0 : 80.00); 
  let total = $derived(subtotal + costoEnvio);

  function procesarPedido() {
    console.log("Procesando pedido para:", nombre, "Método:", metodoPago);
    // Esto le dice al navegador que viaje a la nueva ventana que creaste
    window.location.href = '/confirmacion';
  }
</script>

<div class="fixed inset-0 z-[-1] flex justify-center items-center overflow-hidden pointer-events-none select-none">
  <h1 class="text-[12vw] font-black text-white opacity-[0.02] whitespace-nowrap -rotate-12 tracking-widest uppercase">
    Chucheritas Aralan
  </h1>
</div>

<div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16 min-h-[85vh] relative z-10 text-gray-200">
  
  <div class="flex flex-col lg:flex-row gap-16 lg:gap-28">
    
    <div class="w-full lg:w-[55%] flex flex-col gap-16">
      
      <section>
        <h2 class="text-2xl font-thin tracking-wide mb-12 text-white">Información de Envío</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-12">
          <div class="md:col-span-2">
            <label for="nombre" class="text-[10px] uppercase tracking-[0.2em] text-gray-400 font-thin block mb-3">Nombre Completo</label>
            <input id="nombre" type="text" bind:value={nombre} class="w-full bg-transparent border-b border-gray-600/40 py-3 focus:outline-none focus:border-white transition-colors font-thin text-sm rounded-none" placeholder="Ej. Milton Gonzalez" />
          </div>
          
          <div class="md:col-span-2">
            <label for="direccion" class="text-[10px] uppercase tracking-[0.2em] text-gray-400 font-thin block mb-3">Dirección de Entrega</label>
            <input id="direccion" type="text" bind:value={direccion} class="w-full bg-transparent border-b border-gray-600/40 py-3 focus:outline-none focus:border-white transition-colors font-thin text-sm rounded-none" placeholder="Calle, Número, Colonia" />
          </div>
          
          <div>
            <label for="ciudad" class="text-[10px] uppercase tracking-[0.2em] text-gray-400 font-thin block mb-3">Ciudad</label>
            <input id="ciudad" type="text" bind:value={ciudad} class="w-full bg-transparent border-b border-gray-600/40 py-3 focus:outline-none focus:border-white transition-colors font-thin text-sm rounded-none" placeholder="Ej. Toluca" />
          </div>
          
          <div>
            <label for="cp" class="text-[10px] uppercase tracking-[0.2em] text-gray-400 font-thin block mb-3">Código Postal</label>
            <input id="cp" type="text" bind:value={codigoPostal} class="w-full bg-transparent border-b border-gray-600/40 py-3 focus:outline-none focus:border-white transition-colors font-thin text-sm rounded-none" placeholder="Ej. 50000" />
          </div>
        </div>
      </section>

      <section class="mt-6">
        <h2 class="text-2xl font-thin tracking-wide mb-14 text-white">Método de Pago</h2>
        
        <div class="flex gap-12 mb-24 border-b border-gray-600/30">
          <button 
            onclick={() => metodoPago = 'tarjeta'}
            class="pb-5 text-xs uppercase tracking-[0.2em] transition-all border-b border-transparent {metodoPago === 'tarjeta' ? '!border-white text-white font-normal' : 'text-gray-500 font-thin hover:text-gray-300'}"
          >
            Tarjeta
          </button>
          <button 
            onclick={() => metodoPago = 'efectivo'}
            class="pb-5 text-xs uppercase tracking-[0.2em] transition-all border-b border-transparent {metodoPago === 'efectivo' ? '!border-white text-white font-normal' : 'text-gray-500 font-thin hover:text-gray-300'}"
          >
            Efectivo
          </button>
        </div>

        <div class="h-[240px]"> 
          {#if metodoPago === 'tarjeta'}
            <div class="grid grid-cols-2 gap-x-12 gap-y-16 animate-fade-in">
              <div class="col-span-2">
                <label for="num_tarjeta" class="text-[10px] uppercase tracking-[0.2em] text-gray-400 font-thin block mb-4">Número de Tarjeta</label>
                <input id="num_tarjeta" type="text" class="w-full bg-transparent border-b border-gray-600/40 py-4 focus:outline-none focus:border-white transition-colors font-thin text-sm rounded-none" placeholder="0000 0000 0000 0000" />
              </div>
              <div>
                <label for="expiracion" class="text-[10px] uppercase tracking-[0.2em] text-gray-400 font-thin block mb-4">Expiración</label>
                <input id="expiracion" type="text" class="w-full bg-transparent border-b border-gray-600/40 py-4 focus:outline-none focus:border-white transition-colors font-thin text-sm rounded-none" placeholder="MM/AA" />
              </div>
              <div>
                <label for="cvc" class="text-[10px] uppercase tracking-[0.2em] text-gray-400 font-thin block mb-4">CVV</label>
                <input id="cvc" type="text" class="w-full bg-transparent border-b border-gray-600/40 py-4 focus:outline-none focus:border-white transition-colors font-thin text-sm rounded-none" placeholder="***" />
              </div>
            </div>
          {:else}
            <div class="h-full flex items-start pt-12 animate-fade-in">
              <p class="text-sm font-thin text-gray-400 tracking-wide leading-relaxed">
                El pago se realizará en <span class="text-white font-normal">efectivo</span> al momento de la entrega
              </p>
            </div>
          {/if}
        </div>
      </section>

      <div class="pt-12">
        <button 
          onclick={procesarPedido}
          class="w-full bg-white text-black py-6 text-[11px] font-bold uppercase tracking-[0.3em] hover:bg-gray-200 transition-colors rounded-none"
        >
          Confirmar Orden
        </button>
      </div>

    </div>

    <div class="w-full lg:w-[45%]">
      <div class="sticky top-12 pt-2">
        
        <h2 class="text-2xl font-thin tracking-wide mb-12 text-white">Resumen del Pedido</h2>
        
        <div class="flex flex-col gap-10 mb-14">
          {#each itemsCarrito as item}
            <div class="flex gap-6 items-center">
              <img src={item.foto_url} alt={item.nombre} class="w-20 h-24 object-cover bg-base-300 rounded-none" />
              <div class="flex flex-col justify-center">
                <h3 class="font-normal text-sm text-gray-200 tracking-wide">{item.nombre}</h3>
                <p class="font-thin text-xs text-gray-400 mt-1.5 tracking-wide">{item.marca} | Cant: {item.cantidad}</p>
                <p class="font-medium text-sm text-white mt-3">${(item.precio * item.cantidad).toFixed(2)}</p>
              </div>
            </div>
          {/each}
        </div>
        
        <div class="space-y-6 text-sm mb-10 pt-10 border-t border-gray-600/30">
          <div class="flex justify-between font-thin text-gray-300 tracking-wide">
            <span>Subtotal</span>
            <span class="text-white">${subtotal.toFixed(2)}</span>
          </div>
          <div class="flex justify-between font-thin text-gray-300 tracking-wide">
            <span>Envío</span>
            <span class="text-white">{costoEnvio === 0 ? 'Gratis' : '$' + costoEnvio.toFixed(2)}</span>
          </div>
        </div>

        <div class="flex justify-between items-center mb-10 pt-10 border-t border-gray-600/30">
          <span class="font-thin text-lg text-white tracking-wide">Total</span>
          <span class="text-3xl font-normal text-white">${total.toFixed(2)}</span>
        </div>

        <p class="text-[10px] font-thin text-gray-500 italic tracking-wider leading-relaxed">
          Proceso de pago encriptado.
        </p>

      </div>
    </div>

  </div>
</div>

<style>
  .animate-fade-in {
    animation: fadeIn 0.4s ease-out forwards;
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(5px); }
    to { opacity: 1; transform: translateY(0); }
  }
</style>