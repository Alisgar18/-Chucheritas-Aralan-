<script>
    import { goto } from "$app/navigation";
    import { ArrowRight, ShoppingBag } from "lucide-svelte";

    let { product } = $props();

    function openProduct() {
        goto(`/productos/${product.product_id}`);
    }

    function getImage() {
        return (
            product.product_pictures?.[0]?.picture_url ??
            "/placeholder-product.png"
        );
    }
</script>

<button
    on:click={openProduct}
    class="
    group w-56 rounded-[2rem] p-3
    bg-white/30 backdrop-blur-xl
    border border-white/40
    shadow-xl
    transition-all duration-300
    hover:scale-[1.03]
    hover:bg-white/40
    hover:shadow-2xl
    "
>
    <div class="overflow-hidden rounded-[1.5rem]">
        <img
            src={getImage()}
            alt={product.name}
            class="
            h-64 w-full object-cover
            transition-transform duration-500
            group-hover:scale-105
            "
        />
    </div>

    <div class="pt-4 space-y-1 text-left">
        <h3 class="font-semibold text-lg truncate">
            {product.name}
        </h3>

        <p class="text-sm text-base-content/60">
            {product.categories?.description ?? "Sin categoría"}
        </p>

        <div class="flex items-center justify-between pt-2">
            <div class="flex items-center gap-2">
                <ShoppingBag size={16} />
                <span class="font-bold text-lg">
                    ${product.price}
                </span>
            </div>

            <div
                class="
                p-2 rounded-full
                bg-white/50
                group-hover:translate-x-1
                transition
                "
            >
                <ArrowRight size={16} />
            </div>
        </div>
    </div>
</button>
