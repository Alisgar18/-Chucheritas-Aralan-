<script>
    import { onMount } from "svelte";
    import { getProducts } from "$lib/db/services/products";
    import ProductGrid from "$lib/components/ProductGrid.svelte";

    let products = [];

    onMount(async () => {
        const { data, error } = await getProducts();

        if (!error) {
            products = data;
        }
    });
</script>

<ProductGrid {products} />
