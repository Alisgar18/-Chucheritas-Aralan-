<script>
    import ProductCard from "$lib/components/ProductCard.svelte";

    export let products = [];
</script>

<div class="flex flex-wrap justify-center gap-6">
    {#each products as product}
        <ProductCard
            id={product.id}
            name={product.name}
            price={product.price}
            category={product.category}
            image={product.picture_urls?.[0]}
        />
    {/each}
</div>
