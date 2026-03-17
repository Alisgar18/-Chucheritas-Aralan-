# 🛍️ Chucheritas Aralan

Tienda en línea de accesorios. Construida con **SvelteKit** y **Tailwind CSS**.

---

📋 Requisitos previos

- [Node.js](https://nodejs.org/) v18 o superior
- [Yarn](https://yarnpkg.com/) como gestor de paquetes
- [VS Code](https://code.visualstudio.com/) como editor
- [GitHub Desktop](https://desktop.github.com/) para manejar el repositorio

---

## 🚀 Cómo correr el proyecto

**1. Clonar el repositorio** desde GitHub Desktop: `File → Clone repository` y busca `chucheritas-aralan`.

**2. Instalar dependencias** — abre la terminal integrada de VS Code (`Ctrl + J`) y ejecuta:

```bash
yarn install
```

**3. Iniciar el servidor:**

```bash
yarn dev
```

Abre http://localhost:5173 en tu navegador.

> ⚠️ Si aparece un error de Yarn Berry al correr `yarn dev`, ejecuta primero:
> ```bash
> yarn config set nodeLinker node-modules
> yarn install
> ```

---

## 📁 Estructura del proyecto

```
src/
├── app.html              → HTML base (no tocar)
├── app.css               → Estilos y variables globales
│
├── lib/
│   ├── assets/           → Imágenes, logo, iconos
│   ├── components/       → Componentes reutilizables .svelte (Header, Footer, etc.)
│   └── stores/           → Estado global de la app (carrito, sesión)
│
└── routes/               → Cada carpeta = una página/URL
    ├── +layout.svelte    → Marco que envuelve TODAS las páginas
    ├── +page.svelte      → Página de inicio (/)
    ├── catalogo/         → /catalogo
    ├── carrito/          → /carrito
    ├── login/            → /login
    ├── registro/         → /registro
    ├── perfil/           → /perfil
    ├── pedidos/          → /pedidos
    └── admin/
        ├── +page.svelte  → /admin (dashboard)
        ├── productos/    → /admin/productos
        └── pedidos/      → /admin/pedidos
```

---

## 🧩 Cómo está construido

| Tecnología | Para qué se usa |
|---|---|
| [SvelteKit](https://kit.svelte.dev/) | Framework principal (rutas, páginas, componentes) |
| [Svelte 5](https://svelte.dev/) | Sintaxis de componentes — usa `$state`, `$props`, `onclick` |
| [Tailwind CSS 4](https://tailwindcss.com/) | Estilos — se usa con `@apply` dentro de cada componente |
| [Lucide Svelte](https://lucide.dev/) | Íconos |
| [DaisyUI 4](https://daisyui.com/)| Biblioteca de componentes|

### Svelte 5 — sintaxis importante

Este proyecto usa **Svelte 5**. Los tutoriales de YouTube suelen mostrar Svelte 4, hay diferencias clave:

```svelte
<!-- ✅ Svelte 5 — lo que usamos -->
<script>
  let count = $state(0);       // variables reactivas con $state
  let { title } = $props();    // props del componente
</script>

<button onclick={() => count++}>Click</button>
{@render children()}

<!-- ❌ Svelte 4 — NO usar -->
<script>
  let count = 0;
  export let title;
</script>
<button on:click={() => count++}>Click</button>
<slot />
```

### Rutas

Crear una página nueva es crear una carpeta y un archivo. Se puede hacer directo desde VS Code sin tocar la terminal:

```
src/routes/nueva-pagina/+page.svelte
```

SvelteKit automáticamente la registra como `/nueva-pagina`.

---

## 🔌 Pendientes de backend

El proyecto actualmente usa datos de prueba en `src/lib/data.js`. Lo que falta conectar:

- **CMS** — para gestionar productos y contenido sin tocar código
- **Base de datos** — para usuarios, pedidos e inventario
- **API de Instagram** — para publicaciones automáticas desde el panel
- **Flujo de compra** — pedidos por WhatsApp o similar (sin cobro con tarjeta por ahora)
- **Panel de ventas** — para que Alis y las administradoras vean qué se ha vendido

---

## 🗂️ Páginas pendientes

| Página | Ruta | Estado |
|---|---|---|
| Inicio | `/` | 🔧 En progreso |
| Catálogo | `/catalogo` | ⬜ Pendiente |
| Carrito | `/carrito` | ⬜ Pendiente |
| Login | `/login` | ⬜ Pendiente |
| Registro | `/registro` | ⬜ Pendiente |
| Perfil | `/perfil` | ⬜ Pendiente |
| Mis Pedidos | `/pedidos` | ⬜ Pendiente |
| Dashboard Admin | `/admin` | ⬜ Pendiente |
| Gestionar Productos | `/admin/productos` | ⬜ Pendiente |
| Panel de Ventas | `/admin/ventas` | ⬜ Pendiente |

---

## 🤝 Flujo de trabajo en equipo

Cada integrante trabaja en su propia rama según su rol:

| Integrante | Rama | Rol |
|---|---|---|
| _(front 1)_ | `front/nombre` | Frontend |
| _(front 2)_ | `front/nombre` | Frontend |
| _(back 1)_  | `back/nombre`  | Backend  |
| _(back 2)_  | `back/nombre`  | Backend  |


**Flujo:**

1. Desde GitHub Desktop, crea tu rama antes de empezar a trabajar
2. Haz tus cambios en VS Code
3. Desde GitHub Desktop haz commit con un mensaje descriptivo
4. Sube tu rama (`Push origin`)
5. Abre un **Pull Request** en GitHub para que se revise antes de unirse a `main`

> ⚠️ Nunca trabajes directo en `main`.

**NOTA**
Al finalizar, hay que modificar este archivo