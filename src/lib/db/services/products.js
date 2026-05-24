// src/lib/db/services/products.js
import { supabase } from "../public-client.js";

// ─────────────────────────────────────────
// CONSULTAS — accesibles para todos
// ─────────────────────────────────────────

/**
 * Devuelve todos los productos activos con su categoría y fotos.
 *
 * @returns {{ data: object[] | null, error: string | null }}
 */
export async function getProducts() {
  const { data, error } = await supabase
    .from("products")
    .select(
      `
            *,
            categories(category_id, description),
            product_pictures(picture_id, picture_url)
        `,
    )
    .eq("status", "active")
    .order("name");

  if (error) return { data: null, error: error.message };
  return { data, error: null };
}

/**
 * Devuelve un producto por su ID con categoría y fotos.
 *
 * @param {number} productId
 * @returns {{ data: object | null, error: string | null }}
 */
export async function getProductById(productId) {
  const { data, error } = await supabase
    .from("products")
    .select(
      `
            *,
            categories(category_id, description),
            product_pictures(picture_id, picture_url)
        `,
    )
    .eq("product_id", productId)
    .maybeSingle();

  if (error) return { data: null, error: error.message };
  return { data, error: null };
}

/**
 * Devuelve productos filtrados por categoría.
 *
 * @param {string} categoryId
 * @returns {{ data: object[] | null, error: string | null }}
 */
export async function getProductsByCategory(categoryId) {
  const { data, error } = await supabase
    .from("products")
    .select(
      `
            *,
            categories(category_id, description),
            product_pictures(picture_id, picture_url)
        `,
    )
    .eq("category_id", categoryId)
    .eq("status", "active")
    .order("name");

  if (error) return { data: null, error: error.message };
  return { data, error: null };
}

/**
 * Devuelve todas las categorías.
 *
 * @returns {{ data: object[] | null, error: string | null }}
 */
export async function getCategories() {
  const { data, error } = await supabase
    .from("categories")
    .select("*")
    .order("description");

  if (error) return { data: null, error: error.message };
  return { data, error: null };
}

// ─────────────────────────────────────────
// MUTACIONES — solo admin (RLS lo garantiza)
// ─────────────────────────────────────────

/**
 * Agrega un producto con sus fotos usando la función de la DB.
 *
 * @param {{ categoryId: string, name: string, description: string, price: number, stock: number, pictureUrls: string[] }} data
 * @returns {{ productId: number | null, error: string | null }}
 */
export async function addProduct({
  categoryId,
  name,
  description,
  price,
  stock,
  pictureUrls = [],
}) {
  const { data, error } = await supabase.rpc("add_product", {
    p_category_id: categoryId,
    p_name: name,
    p_description: description,
    p_price: price,
    p_stock: stock,
    p_picture_urls: pictureUrls,
  });

  if (error) return { productId: null, error: error.message };
  return { productId: data, error: null };
}

/**
 * Actualiza un producto. Solo pasa los campos que quieres cambiar.
 * Para reemplazar fotos pasa un nuevo array en pictureUrls.
 * Para no tocar las fotos omite pictureUrls o pasa null.
 *
 * @param {number} productId
 * @param {{ categoryId?: string, name?: string, description?: string, price?: number, stock?: number, status?: string, pictureUrls?: string[] | null }} fields
 * @returns {{ error: string | null }}
 */
export async function updateProduct(
  productId,
  { categoryId, name, description, price, stock, status, pictureUrls = null },
) {
  const { error } = await supabase.rpc("update_product", {
    p_product_id: productId,
    p_category_id: categoryId ?? null,
    p_name: name ?? null,
    p_description: description ?? null,
    p_price: price ?? null,
    p_stock: stock ?? null,
    p_status: status ?? null,
    p_picture_urls: pictureUrls,
  });

  if (error) return { error: error.message };
  return { error: null };
}

/**
 * Sube una foto al storage de Supabase y devuelve la URL pública.
 * Usar antes de llamar addProduct o updateProduct.
 *
 * @param {File} file
 * @param {number} productId  — usado para nombrar el archivo
 * @returns {{ url: string | null, error: string | null }}
 */
export async function uploadProductPicture(file, productId) {
  const ext = file.name.split(".").pop();
  const filename = `${productId}_${Date.now()}.${ext}`;

  const { error: uploadError } = await supabase.storage
    .from("fotos-productos")
    .upload(filename, file, { upsert: true });

  if (uploadError) return { url: null, error: uploadError.message };

  const { data } = supabase.storage
    .from("fotos-productos")
    .getPublicUrl(filename);

  return { url: data.publicUrl, error: null };
}
