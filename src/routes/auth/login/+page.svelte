<script>
  import { login } from '$lib/auth.svelte.js'; 
  import { goto } from '$app/navigation';
  
  let correo = $state('');
  let contrasena = $state('');

  function manejarLogin(event) {
    event.preventDefault();
    
    // Aquí puedes poner tu lógica de validación real (como verificar con una API)
    // Por ahora, simulamos un inicio de sesión exitoso:
    if (correo && contrasena) {
      const nombreUsuario = correo.split('@')[0]; 
      
      // Llamamos a la función global para cambiar el estado de la app
      login({ name: nombreUsuario }); 
      
      // Redirigimos al inicio automáticamente
      goto('/'); 
    }
  }
</script>

<div class="flex flex-col md:flex-row w-full min-h-[85vh] mt-6 px-4 lg:px-8 max-w-7xl mx-auto">
  
  <div class="hidden md:flex md:w-1/2 relative items-center justify-center overflow-hidden rounded-l-3xl shadow-2xl">
    <img 
      src="https://placehold.co/1000x1200/ff6b6b/white?text=Chucheritas" 
      alt="Fondo Chucheritas" 
      class="absolute inset-0 w-full h-full object-cover"
    />
    <div class="absolute inset-0 bg-primary/20 mix-blend-multiply"></div>
    <div class="absolute inset-0 bg-black/40"></div>
    
    <div class="relative z-10 text-center">
      <h2 class="text-5xl lg:text-6xl font-bold text-white tracking-widest uppercase drop-shadow-2xl">
        Chucheritas
      </h2>
      <p class="text-xl lg:text-2xl text-white tracking-[0.4em] mt-3 font-light">ARALAN</p>
    </div>
  </div>

  <div class="w-full md:w-1/2 flex flex-col justify-center items-center p-8 lg:p-14 bg-base-200/30 backdrop-blur-md rounded-3xl md:rounded-l-none md:rounded-r-3xl shadow-2xl border-y border-r border-white/5">
    
    <div class="w-full max-w-md flex flex-col">
      
      <h1 class="text-3xl font-medium mb-12 text-center text-white tracking-wide">
        Iniciar sesión
      </h1>

      <form onsubmit={manejarLogin} class="w-full space-y-8">
        
        <div class="w-full">
          <label for="correo" class="block text-sm font-medium mb-3 text-gray-300 tracking-wide">
            Correo electrónico
          </label>
          <input 
            id="correo"
            type="email" 
            class="w-full bg-base-100/50 border border-gray-600/40 rounded-xl py-4 px-5 text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all backdrop-blur-sm"
            bind:value={correo} 
            required 
          />
        </div>

        <div class="w-full">
          <label for="contrasena" class="block text-sm font-medium mb-3 text-gray-300 tracking-wide">
            Contraseña
          </label>
          <input 
            id="contrasena"
            type="password" 
            class="w-full bg-base-100/50 border border-gray-600/40 rounded-xl py-4 px-5 text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all backdrop-blur-sm"
            bind:value={contrasena} 
            required 
          />
        </div>

        <button 
          type="submit" 
          class="w-full bg-primary/90 text-white hover:bg-primary font-bold py-4 rounded-full transition-all mt-4 shadow-lg shadow-primary/20 hover:shadow-primary/40"
        >
          Iniciar sesión
        </button>
      </form>

      <div class="flex flex-col items-center gap-5 mt-10 text-sm">
        <a href="/recuperar-contrasena" class="text-gray-400 hover:text-primary transition-colors">¿Olvidaste tu contraseña?</a>
        <a href="/ayuda" class="text-gray-400 hover:text-primary transition-colors">¿Tienes problemas para iniciar sesión?</a>
      </div>

      <div class="divider divider-neutral my-8 text-gray-500 text-xs">O</div>

      <a 
        href="/registro" 
        class="w-full border border-gray-600/60 text-gray-300 hover:text-white hover:border-primary hover:bg-primary/10 font-bold py-4 rounded-full text-center transition-all"
      >
        Crear una cuenta nueva
      </a>
      
    </div>
  </div>
</div>

<style>
  /* Aquí mantienes tus estilos, recuerda que si ves avisos amarillos es por Tailwind */
  @reference "../../app.css";
  /* ... resto de tus estilos ... */
</style>
