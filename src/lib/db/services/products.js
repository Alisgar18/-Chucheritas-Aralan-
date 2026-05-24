// src/lib/db/services/products.js
import { supabase } from "../public-client.js";
import { compressImages } from "../utils/picEditor.js";
import { getCache, setCache, clearCache } from "../cache.js";

const BUCKET = "product_pictures";

// ─────────────────────────────────────────
// CONSULTAS — accesibles para todos
// ─────────────────────────────────────────

/**
 * Devuelve todos los productos activos con su categoría y fotos.
 *
 * @returns {{ data: object[], error: null } | { data: null, error: string }}
 */
export async function getProducts() {
  const cached = getCache("products");
  if (cached) return { data: cached, error: null };

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
  setCache("products", data, 300);
  return { data, error: null };
}

/**
 * Devuelve un producto por su ID con categoría y fotos.
 *
 * @param {number} productId
 * @returns {{ data: object, error: null } | { data: null, error: string }}
 */
export async function getProductById(productId) {
  const cached = getCache(`product:${productId}`);
  if (cached) return { data: cached, error: null };

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
  setCache(`product:${productId}`, data, 300);
  return { data, error: null };
}

/**
 * Devuelve productos filtrados por categoría.
 *
 * @param {string} categoryId
 * @returns {{ data: object[], error: null } | { data: null, error: string }}
 */
export async function getProductsByCategory(categoryId) {
  const cached = getCache(`products:category:${categoryId}`);
  if (cached) return { data: cached, error: null };

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
  setCache(`products:category:${categoryId}`, data, 300);
  return { data, error: null };
}

/**
 * Devuelve todas las categorías.
 *
 * @returns {{ data: object[], error: null } | { data: null, error: string }}
 */
export async function getCategories() {
  const cached = getCache("categories");
  if (cached) return { data: cached, error: null };

  const { data, error } = await supabase
    .from("categories")
    .select("*")
    .order("description");

  if (error) return { data: null, error: error.message };
  setCache("categories", data, 3600);
  return { data, error: null };
}

// ─────────────────────────────────────────
// MUTACIONES — solo admin (RLS lo garantiza)
// ─────────────────────────────────────────

/**
 * Agrega un producto con sus fotos usando la función de la DB.
 *
 * @param {{ categoryId: string, name: string, description: string, price: number, stock: number, pictureFiles: File[] }} data
 * @returns {{ productId: number, error: null } | { productId: null, error: string }}
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
    compressedPictures.map(({ path, buffer }) =>
      uploadProductPicture(path, buffer),
    ),
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

  if (!error) clearCache("products");
  return {
    productId: data,
    error: error?.message ?? null,
  };
}

/**
 * Actualiza un producto. Solo pasa los campos que quieres cambiar.
 * Para reemplazar fotos pasa un nuevo array en pictureFiles.
 * Para no tocar las fotos omite pictureFiles o pasa null.
 *
 * @param {number} productId
 * @param {{ categoryId?: string, name?: string, description?: string, price?: number, stock?: number, status?: string, pictureFiles?: File[] | null }} fields
 * @returns {{ error: null } | { error: string }}
 */
export async function updateProduct(
  productId,
  { categoryId, name, description, price, stock, status, pictureFiles = null },
) {
  let pictureUrls = null;

  if (pictureFiles && pictureFiles.length > 0) {
    const compressedPictures = await compressImages(pictureFiles, {
      prefix: `${categoryId ?? "product"}_${name ?? productId}`,
      quality: 75,
    });

    const uploadedPictures = await Promise.all(
      compressedPictures.map(({ path, buffer }) =>
        uploadProductPicture(path, buffer),
      ),
    );

    pictureUrls = uploadedPictures
      .filter((pic) => !pic.error && pic.url)
      .map((pic) => pic.url);
  }

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

  clearCache("products");
  clearCache(`product:${productId}`);
  clearCache(`products:category:${categoryId}`);
  return { error: null };
}

// ─────────────────────────────────────────
// HELPERS — internos
// ─────────────────────────────────────────

/**
 * Sube una foto comprimida al storage y devuelve la URL pública.
 *
 * @param {string} storagePath
 * @param {Buffer} fileBuffer
 * @param {boolean} upsert
 * @returns {{ url: string, error: null } | { url: null, error: string }}
 */
async function uploadProductPicture(storagePath, fileBuffer, upsert = false) {
  const { data, error: uploadError } = await supabase.storage
    .from(BUCKET)
    .upload(storagePath, fileBuffer, {
      contentType: "image/webp",
      cacheControl: "2592000", // 30 días
      upsert,
    });

  if (uploadError) return { url: null, error: uploadError.message };

  return {
    url: getProductPictureUrl(data.path),
    error: null,
  };
}

/**
 * Construye la URL pública de una foto dado su path en el storage.
 *
 * @param {string} path
 * @returns {string}
 */
export function getProductPictureUrl(path) {
  const { data } = supabase.storage.from(BUCKET).getPublicUrl(path);
  return data.publicUrl;
}
