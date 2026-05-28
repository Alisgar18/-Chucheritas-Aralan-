<script>
    import ProductCard from "$lib/components/ProductCard.svelte";

    let { products = [] } = $props();
</script>

<div class="flex flex-wrap justify-center gap-6">
    {#each products as product (product.product_id)}
        <ProductCard {product} />
    {/each}
</div>
