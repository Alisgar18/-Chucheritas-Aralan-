<<<<<<< Updated upstream
<h1>Chucheritas Aralan 💗</h1>
<p>Muy pronto</p>
<p>Aqui se edita el contenido</p>
=======
<script>
  // Arreglo con las secciones destacadas para el inicio
  const destacados = [
    {
      titulo: "Líneas de expresión y cuidado facial",
      categoria: "SKINCARE",
      descripcion: "Reduce visiblemente las líneas de expresión y luce una piel saludable con nuestra mascarilla de Ácido Hialurónico. Hidratación profunda para combatir los signos de la fatiga en tu día a día.",
      precio: 25.00,
      imagen: "https://placehold.co/800x800/ff6b6b/white?text=Cuidado+Facial",
      enlace: "/catalogo?cat=SKIN",
      alineacionDerecha: false // Imagen a la izquierda, texto a la derecha
    },
    {
      titulo: "Brillo extremo sin sensación pegajosa",
      categoria: "LABIOS",
      descripcion: "El Lip Oil de Beauty Creations se ha convertido en un básico. Aporta el brillo de un gloss con la hidratación profunda de un bálsamo, dejando tus labios suaves y con un ligero toque de color.",
      precio: 75.00,
      imagen: "https://placehold.co/800x800/ff6b6b/white?text=Lip+Oil",
      enlace: "/catalogo?cat=LAB",
      alineacionDerecha: true // Texto a la izquierda, imagen a la derecha
    }
  ];
</script>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 space-y-24">
  
  {#each destacados as item}
    <div class="flex flex-col {item.alineacionDerecha ? 'md:flex-row-reverse' : 'md:flex-row'} items-center gap-10 lg:gap-16">
      
      <div class="w-full md:w-1/2">
        <div class="overflow-hidden rounded-sm bg-base-300 shadow-2xl">
          <img 
            src={item.imagen} 
            alt={item.titulo} 
            class="w-full h-auto object-cover aspect-square hover:scale-105 transition-transform duration-700" 
          />
        </div>
      </div>
      
      <div class="w-full md:w-1/2 flex flex-col justify-center text-left">
        <p class="text-primary text-xs font-bold tracking-widest uppercase mb-3">
          {item.categoria}
        </p>
        
        <h2 class="text-3xl md:text-4xl lg:text-5xl font-bold leading-tight mb-6">
          {item.titulo}
        </h2>
        
        <p class="text-base md:text-lg opacity-70 leading-relaxed mb-6 max-w-lg">
          {item.descripcion}
        </p>
        
        <p class="text-2xl font-semibold text-primary mb-8">
          ${item.precio.toFixed(2)} MXN
        </p>
        
        <div>
          <a href={item.enlace} class="btn btn-primary rounded-sm px-10 text-white tracking-wider uppercase font-bold">
            Ver Producto
          </a>
        </div>
      </div>
      
    </div>
  {/each}

</div>
>>>>>>> Stashed changes
