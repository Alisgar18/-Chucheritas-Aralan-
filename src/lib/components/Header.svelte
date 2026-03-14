<script>
  import { page } from '$app/stores';
  import logo from '$lib/assets/logo.png';

  let menuAbierto = $state(false);
</script>

<header>
  <div class="header-inner">

    <!-- Logo -->
    <a href="/" class="logo">
        <img src={logo} alt="Chucheritas Aralan" class="logo-img" />
    </a>

    <!-- Nav desktop -->
    <nav class="nav-desktop">
        <div>
            <a href="/" class:activa={$page.url.pathname === '/'}>Inicio</a>
            <a href="/catalogo" class:activa={$page.url.pathname === '/catalogo'}>Catálogo</a>
        </div>
        <div>
            <a href="/login" class="btn-login">Iniciar sesión</a>
            <a href="/carrito" class:activa={$page.url.pathname === '/carrito'}>Carrito</a>
        </div>
    </nav>

    <!-- Botón hamburguesa (móvil) -->
    <button
        class="hamburger"
        onclick={() => menuAbierto = !menuAbierto}
        aria-label="Abrir menú"
        >
        {menuAbierto ? '✕' : '☰'}
    </button>

  </div>

  
    
</header>

<!-- Menú celular -->
{#if menuAbierto}
    <div class="drawer-overlay" onclick={() => menuAbierto = false} role="presentation"></div>
    <nav class="drawer">
        <div class="drawer-header">
            <img src={logo} alt="Chucheritas Aralan" class="drawer-logo" />
            <button class="drawer-cerrar" onclick={() => menuAbierto = false}>✕</button>
        </div>

        <div class="drawer-links">
            <a href="/" onclick={() => menuAbierto = false}>Inicio</a>
            <a href="/carrito" onclick={() => menuAbierto = false}>Carrito</a>
            <a href="/catalogo" onclick={() => menuAbierto = false}>Catálogo</a>
        </div>

        <hr class="drawer-divider" />

        <div class="drawer-auth">
        <a href="/login" class="btn-primary" onclick={() => menuAbierto = false}>Iniciar sesión</a>
            
        </div>
    </nav>
    {/if}


<!--Estilos del componente-->

<style>
  header {
  @apply sticky z-[100] w-[min(92%,1100px)] rounded-[var(--radius-lg)] 
    shadow-[0_6px_28px_var(--sombra-fuerte)] mt-4 mb-0 mx-auto top-4;
  background: var(--rosa);
}
.header-inner {
  @apply flex items-center justify-between gap-4 px-6 py-3;
}

/* Logo */
.logo {
  @apply flex items-baseline gap-[0.2rem] text-[white] text-[1.3rem] font-bold;
  font-family: var(--font-display);
}
.logo-img {
  @apply h-20 w-auto object-contain animate-[latido_2s_infinite];
}

/* Nav desktop */
.nav-desktop {
  @apply flex items-center justify-between flex-1 mx-8 my-0;
}
.nav-desktop div:first-child {
  @apply flex items-center gap-[0.2rem] mx-auto my-0;
}
.nav-desktop div:last-child {
  @apply flex items-center gap-[0.2rem];
}
.nav-desktop a {
  @apply text-[white] font-medium text-[0.92rem] rounded-[var(--radius-pill)] 
    transition-[background] duration-[var(--transition)] px-3.5 py-[7px];
}
.nav-desktop a:hover,
.nav-desktop a.activa {
  background: rgba(255, 255, 255, 0.22);
}
.btn-login {
  @apply border-[1.5px] border-solid border-[rgba(255,255,255,0.5)];
}

/* Hamburguesa */
.hamburger {
  @apply hidden text-[white] text-[1.6rem] leading-none p-1 border-[none];
  background: none;
}

/* Drawer */
:global(.drawer-overlay) {
  @apply fixed backdrop-blur-[2px] z-[200] inset-0;
  background: rgba(0, 0, 0, 0.3);
}
:global(.drawer) {
  @apply fixed h-screen w-[280px] z-[201] flex flex-col 
    shadow-[-8px_0_32px_rgba(0,0,0,0.15)] px-5 py-6 right-0 top-0;
  background: white;
}
:global(.drawer-header) {
  @apply flex items-center justify-between mb-8;
}
:global(.drawer-logo) {
  @apply h-12 w-auto;
}
:global(.drawer-cerrar) {
  @apply text-[color:var(--rosa-texto)] text-[1.1rem] w-[34px] h-[34px] flex items-center 
    justify-center transition-[background] duration-[var(--transition)] rounded-[50%] 
    border-[none];
  background: var(--rosa-claro);
}
:global(.drawer-links) {
  @apply flex flex-col gap-1;
}
:global(.drawer-links a) {
  @apply text-[color:var(--negro-suave)] font-medium text-base rounded-[var(--radius-md)] 
    transition-[background] duration-[var(--transition)] px-4 py-3;
}
:global(.drawer-links a:hover) {
  background: var(--rosa-fondo);
}
:global(.drawer-divider) {
  @apply border-t-[color:var(--rosa-claro)] mx-0 my-[1.2rem] border-[none] 
    border-t border-solid;
}
:global(.drawer-auth) {
  @apply flex flex-col gap-[0.8rem];
}
:global(.drawer-auth a) {
  @apply text-center justify-center;
}
@media (max-width: 768px) {
  .nav-desktop {
    @apply hidden;
  }
  .hamburger {
    @apply block;
  }
}
@keyframes latido {
    0%, 100% { transform: scale(1); }
    50%       { transform: scale(1.06); }
}
</style>