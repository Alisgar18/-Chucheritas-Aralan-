// src/lib/db/services/products.js
import { supabase } from "../public-client.js";
import { compressImages } from "../utils/picEditor.js";

// ─────────────────────────────────────────
// CONSULTAS — accesibles para todos
// ─────────────────────────────────────────

/**
 * Devuelve todos los productos activos con su categoría y fotos.
 *
 * @returns {{ data: object[], error: null || data: null, error: string }}
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
 * @returns {{ data: object, error: null || data: null, error: string }}
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
 * @returns {{ data: object[], error: null || data: null, error: string }}
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
 * @returns {{ data: object[], error: null || data: null, error: string }}
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
 * @returns {{ productId: number, error: null || productId: null, error: string }}
 */
export async function addProduct({
  categoryId,
  name,
  description,
  price,
  stock,
  pictureFiles = [],
}) {
  // Comprime y genera path+buffer
  const compressedPictures = await compressImages(pictureFiles, {
    prefix: `${categoryId}_${name}`,
    quality: 75,
  });

  // Subir imágenes
  const uploadedPictures = await Promise.all(
    compressedPictures.map(async ({ path, buffer }) => {
      return await uploadProductPicture(path, buffer);
    }),
  );

  // Extraer URLs válidas
  const pictureUrls = uploadedPictures
    .filter((pic) => !pic.error && pic.url)
    .map((pic) => pic.url);

  const { data, error } = await supabase.rpc("add_product", {
    p_category_id: categoryId,
    p_name: name,
    p_description: description,
    p_price: price,
    p_stock: stock,
    p_picture_urls: pictureUrls,
  });

  return {
    productId: data,
    error: error?.message ?? null,
  };
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
 * Sube una foto al storage de Supabase y devuelve la URL.
 * Usar antes de llamar addProduct o updateProduct.
 *
 * @param {string} storagePath
 * @param {File} fileBuffer
 * @param {boolean} upsert
 * @returns {{ url: string , error: null || url: null, error: string }}
 */

async function uploadProductPicture(storagePath, fileBuffer, upsert = false) {
  const bucket = "product_pictures";

  const { data, error: uploadError } = await supabase.storage
    .from(bucket)
    .upload(storagePath, fileBuffer, {
      contentType: "image/webp",
      cacheControl: "3600",
      upsert: upsert,
    });

  return {
    url: data?.path ?? null,
    error: uploadError?.message ?? null,
  };
}
