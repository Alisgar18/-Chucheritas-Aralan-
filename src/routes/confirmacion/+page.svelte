<script>
  const numeroOrden = "CH-" + Math.floor(10000 + Math.random() * 90000);

  // Simulamos los productos con sus cantidades
  const itemsComprados = [
    {
      id: 1,
      nombre: "Lip Oil Hidratante",
      variante: "Tono: Fresa",
      precio: 75.00,
      cantidad: 2,
      foto_url: "https://placehold.co/400x500/2a2a2a/ffffff?text=Lip+Oil"
    },
    {
      id: 4,
      nombre: "Mascarilla Facial",
      variante: "Ácido Hialurónico",
      precio: 25.00,
      cantidad: 1,
      foto_url: "https://placehold.co/400x500/2a2a2a/ffffff?text=Mascarilla"
    }
  ];

  // Cálculos reales para el resumen
  const subtotal = itemsComprados.reduce((suma, item) => suma + (item.precio * item.cantidad), 0);
  const costoEnvio = subtotal >= 150 || subtotal === 0 ? 0 : 80.00;
  const totalFinal = subtotal + costoEnvio;

  const hoy = new Date();
  const fechaLlegada = new Date(hoy);
  fechaLlegada.setDate(fechaLlegada.getDate() + 3);
  const opcionesFecha = { day: 'numeric', month: 'long', year: 'numeric' };
  const fechaEst = fechaLlegada.toLocaleDateString('es-MX', opcionesFecha);
  
  // Simulamos el método de pago elegido
  const metodoPago = "Tarjeta terminada en 4242"; // O podría decir "Efectivo al recibir"
</script>

<div class="fixed inset-0 z-[-1] flex justify-center items-center overflow-hidden pointer-events-none select-none">
  <h1 class="text-[12vw] font-black text-white opacity-[0.02] whitespace-nowrap -rotate-12 tracking-widest uppercase">
    Chucheritas Aralan
  </h1>
</div>

<div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16 min-h-[85vh] relative z-10 text-gray-200">
  
  <div class="flex flex-col items-center text-center mb-20 animate-fade-in">
    <div class="w-16 h-16 rounded-full border border-gray-500 flex items-center justify-center mb-8">
      <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1">
        <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"></path>
      </svg>
    </div>
    
    <h1 class="text-3xl lg:text-4xl font-thin tracking-wide text-white mb-4">
      Gracias por tu compra
    </h1>
    
    <p class="text-sm font-thin text-gray-400 tracking-wide">
      Tu pedido <span class="font-normal text-white">#{numeroOrden}</span> ha sido realizado y se está procesando.
    </p>
  </div>

  <div class="flex flex-col lg:flex-row gap-16 lg:gap-24 animate-fade-in" style="animation-delay: 0.1s;">
    
    <div class="w-full lg:w-3/5">
      <h2 class="text-[10px] uppercase tracking-[0.2em] font-normal text-gray-400 mb-8 border-b border-gray-600/30 pb-4">
        Resumen del Pedido
      </h2>
      
      <div class="flex flex-col gap-8">
        {#each itemsComprados as item}
          <div class="flex gap-6 items-center">
            <img src={item.foto_url} alt={item.nombre} class="w-20 h-24 object-cover bg-base-300 rounded-none" />
            <div class="flex flex-col justify-center flex-1">
              <h3 class="font-normal text-sm text-gray-200 tracking-wide">{item.nombre}</h3>
              <p class="font-thin text-xs text-gray-500 mt-1.5 tracking-wide">{item.variante} | Cant: {item.cantidad}</p>
            </div>
            <div class="font-normal text-sm text-white">
              ${(item.precio * item.cantidad).toFixed(2)}
            </div>
          </div>
        {/each}
      </div>

      <div class="mt-10 pt-8 border-t border-gray-600/30 space-y-4">
        <div class="flex justify-between text-sm font-thin text-gray-300 tracking-wide">
          <span>Subtotal</span>
          <span class="text-white">${subtotal.toFixed(2)}</span>
        </div>
        <div class="flex justify-between text-sm font-thin text-gray-300 tracking-wide">
          <span>Envío</span>
          <span class="text-white">{costoEnvio === 0 ? 'Gratis' : '$' + costoEnvio.toFixed(2)}</span>
        </div>
      </div>

      <div class="flex justify-between items-end mt-6 pt-6 border-t border-gray-600/30">
        <span class="font-normal text-sm text-white tracking-wide">Total</span>
        <span class="text-3xl font-normal text-white">${totalFinal.toFixed(2)}</span>
      </div>
    </div>

    <div class="w-full lg:w-2/5 flex flex-col gap-8">
      
      <div class="bg-base-200/20 border border-white/5 p-8 lg:p-10 rounded-none">
        
        <h2 class="text-[10px] uppercase tracking-[0.2em] font-normal text-gray-400 mb-6">
          Detalles de Envío
        </h2>
        
        <div class="mb-8">
          <p class="font-normal text-sm text-white mb-2 tracking-wide">Milton Gonzalez</p>
          <p class="font-thin text-xs text-gray-400 leading-relaxed tracking-wide">
            Calle de Ejemplo 123<br>
            Colonia Centro, 50000<br>
            Toluca, México
          </p>
        </div>

        <h2 class="text-[10px] uppercase tracking-[0.2em] font-normal text-gray-400 mb-4">
          Entrega Estimada
        </h2>
        <div class="flex items-center gap-3 text-sm font-thin text-white tracking-wide mb-8">
          <svg class="w-4 h-4 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
          </svg>
          Entre el {fechaEst}
        </div>

        <h2 class="text-[10px] uppercase tracking-[0.2em] font-normal text-gray-400 mb-4">
          Método de Pago
        </h2>
        <div class="flex items-center gap-3 text-sm font-thin text-white tracking-wide">
          <svg class="w-4 h-4 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 8.25h19.5M2.25 9h19.5m-16.5 5.25h6m-6 2.25h3m-3.75 3h15a2.25 2.25 0 002.25-2.25V6.75A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25v10.5A2.25 2.25 0 004.5 19.5z" />
          </svg>
          {metodoPago}
        </div>

      </div>

      <div class="flex flex-col gap-4">
        <a href="/" class="block w-full text-center bg-white text-black font-bold py-5 text-[10px] uppercase tracking-[0.2em] hover:bg-gray-200 transition-colors rounded-none">
          Continuar Comprando
        </a>
        
        <button class="w-full text-center bg-transparent border border-gray-600/50 text-white py-5 text-[10px] font-bold uppercase tracking-[0.2em] hover:border-white transition-colors rounded-none">
          Ver Detalles del Pedido
        </button>
      </div>

      <div class="text-center mt-4">
        <p class="text-xs font-thin text-gray-500 tracking-wide">
          ¿Tienes alguna duda? <a href="/contacto" class="text-white hover:underline underline-offset-4">Contáctanos</a>
        </p>
      </div>

    </div>

  </div>
</div>

<style>
  .animate-fade-in {
    opacity: 0;
    animation: fadeIn 0.5s ease-out forwards;
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
</style>