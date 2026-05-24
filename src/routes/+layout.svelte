<!-- Layout -->
<script>
    import "../app.css";
    import favicon from "$lib/assets/favicon.svg";
    import Header from "$lib/components/Header.svelte";
    import Footer from "$lib/components/Footer.svelte";

    let { children } = $props();
</script>

<svelte:head>
    <link rel="icon" href={favicon} />
    <title>Chucheritas Aralan</title>
    <meta name="description" content="Tienda de maquillaje" />
</svelte:head>

<!-- components/Header.svelte -->
<Header></Header>

<!-- pagina -->
<main class="contenido-principal">
    {@render children()}
</main>

<!-- components/Footer.svelte -->
<Footer></Footer>
