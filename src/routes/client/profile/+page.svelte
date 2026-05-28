<script>
  import { auth, logout } from '$lib/auth.svelte.js';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';

  // Protegemos la ruta: si no está logueado, lo mandamos al login
  onMount(() => {
    if (!auth.isLoggedIn) {
      goto('/login');
    }
  });
</script>

<div class="max-w-2xl mx-auto mt-20 p-8 text-white">
  <h1 class="text-3xl font-thin tracking-widest uppercase mb-10">Mi Perfil</h1>

  {#if auth.isLoggedIn}
    <div class="bg-base-200/30 p-8 rounded-2xl border border-white/10 backdrop-blur-sm">
      <p class="text-gray-400 text-[10px] uppercase tracking-[0.2em] mb-1">Nombre</p>
      <p class="text-xl mb-6">{auth.user?.name}</p>

      <p class="text-gray-400 text-[10px] uppercase tracking-[0.2em] mb-1">Correo</p>
      <p class="text-xl mb-8">usuario@chucheritas.com</p>

      <button 
        onclick={logout} 
        class="border border-white/20 px-6 py-3 text-[10px] uppercase tracking-widest hover:bg-white hover:text-black transition-all"
      >
        Cerrar Sesión
      </button>
    </div>
  {/if}
</div>
