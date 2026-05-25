<script>
  import { page } from '$app/stores';
  // Importamos la función para añadir productos
  import { addToCart } from '$lib/cart.svelte.js';

  const categorias = [
    { id_categoria: 'TODOS', descripcion: 'Todos' },
    { id_categoria: 'LAB',   descripcion: 'Labios' },
    { id_categoria: 'OJOS',  descripcion: 'Ojos' },
    { id_categoria: 'ROST',  descripcion: 'Rostro' },
    { id_categoria: 'SKIN',  descripcion: 'Skincare' }
  ];

  // Estado inicial
  let categoriaSeleccionada = $state('TODOS');

  // Magia de Svelte: Si venimos de Inicio con una categoría en la URL
  $effect(() => {
    const catUrl = $page.url.searchParams.get('cat');
    if (catUrl) {
      categoriaSeleccionada = catUrl;
    }
  });

  // Función para cambiar de categoría y limpiar la URL
  function cambiarCategoria(cat) {
    categoriaSeleccionada = cat;
    window.history.replaceState({}, '', '/catalogo'); 
  }

  const productosDB = [
      {
          id: 1, // Agregué id para que coincida con tu lógica del carrito
          nombre: "Lip Oil Hidratante",
          marca: "Beauty Creations",
          tono: "Fresa / Transparente",
          id_categoria: "LAB",
          descripcion: "Aceite para labios que aporta brillo extremo sin sensación pegajosa.",
          precio: 75.00,
          existencias: 12,
          estado: 'activo',
          foto_url: "https://placehold.co/600x800/ff6b6b/white?text=Lip+Oil"
      },
      {
          id: 2,
          nombre: "Paleta de Sombras Neutras",
          marca: "Bissú",
          tono: "Tierra / Cálidos",
          id_categoria: "OJOS",
          descripcion: "Paleta de alta pigmentación ideal para looks de día y de noche.",
          precio: 140.00,
          existencias: 5,
          estado: 'activo',
          foto_url: "https://placehold.co/600x800/ff6b6b/white?text=Sombras"
      },
      {
          id: 3,
          nombre: "Rubor Líquido Matte",
          marca: "Pink Up",
          tono: "Durazno Suave",
          id_categoria: "ROST",
          descripcion: "Rubor de larga duración, fácil de difuminar y acabado natural.",
          precio: 85.00,
          existencias: 0,
          estado: 'activo',
          foto_url: "https://placehold.co/600x800/ff6b6b/white?text=Rubor"
      },
      {
          id: 4,
          nombre: "Mascarilla de Hialurónico",
          marca: "Bioaqua",
          tono: "N/A",
          id_categoria: "SKIN",
          descripcion: "Mascarilla en tela para hidratación profunda y cuidado de la piel.",
          precio: 25.00,
          existencias: 30,
          estado: 'activo',
          foto_url: "https://placehold.co/600x800/ff6b6b/white?text=Mascarilla"
      }
  ];

  let productosFiltrados = $derived(
    categoriaSeleccionada === 'TODOS'
      ? productosDB
      : productosDB.filter(p => p.id_categoria === categoriaSeleccionada)
  );
</script>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
  
  <div class="text-center mb-16">
    <h2 class="text-3xl font-light tracking-widest uppercase mb-6">Catálogo</h2>
    
    <div class="flex flex-wrap justify-center gap-6 sm:gap-10">
      {#each categorias as cat}
        <button 
          class="text-xs uppercase tracking-widest pb-2 border-b-2 transition-all duration-300 {categoriaSeleccionada === cat.id_categoria ? 'border-primary text-primary font-bold' : 'border-transparent text-gray-400 hover:text-gray-200'}"
          onclick={() => cambiarCategoria(cat.id_categoria)}
        >
          {cat.descripcion}
        </button>
      {/each}
    </div>
  </div>

  <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-x-6 gap-y-12">
    
    {#each productosFiltrados as producto}
      <div class="group cursor-pointer flex flex-col">
        <div class="relative overflow-hidden mb-4 bg-base-300 rounded-sm">
          <img src={producto.foto_url} alt={producto.nombre} class="w-full aspect-[4/5] object-cover transition-transform duration-700 group-hover:scale-105" />
          
          {#if producto.existencias === 0}
            <div class="absolute inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center">
              <span class="text-white text-xs font-bold tracking-widest border border-white px-4 py-2">AGOTADO</span>
            </div>
          {/if}
        </div>
        
        <div class="flex flex-col flex-grow">
          <p class="text-[10px] text-gray-400 uppercase tracking-widest mb-1">{producto.marca}</p>
          <h3 class="text-sm font-medium leading-snug mb-1 group-hover:text-primary transition-colors">{producto.nombre}</h3>
          
          {#if producto.tono !== 'N/A'}
            <p class="text-xs text-gray-500 mb-3">{producto.tono}</p>
          {/if}
          
          <div class="mt-auto flex justify-between items-center pt-2">
            <p class="text-base font-semibold">${producto.precio.toFixed(2)}</p>
            
            {#if producto.existencias > 0 && producto.estado === 'activo'}
              <button 
                onclick={() => addToCart(producto)}
                class="text-xs font-bold text-primary uppercase tracking-wider hover:underline"
              >
                + Añadir
              </button>
            {/if}
          </div>
        </div>
      </div>
    {:else}
      <div class="col-span-full text-center py-20">
        <p class="text-gray-400 font-light tracking-wide">No hay productos disponibles en esta categoría.</p>
      </div>
    {/each}

  </div>
</div>