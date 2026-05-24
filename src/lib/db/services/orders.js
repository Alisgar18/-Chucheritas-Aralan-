// src/lib/db/services/orders.js
import { supabase } from "../public-client.js";

// ─────────────────────────────────────────
// CREAR PEDIDO
// ─────────────────────────────────────────

/**
 * Crea un pedido completo con sus detalles.
 * El trigger decrease_stock valida y descuenta el stock automáticamente.
 *
 * @param {{
 *   clientId:     number,
 *   addressId:    number,
 *   delivererId:  number,
 *   deliveryDate: string,   // 'YYYY-MM-DD'
 *   totalAmount:  number,
 *   items: { productId: number, quantity: number, subtotal: number }[]
 * }} orderData
 * @returns {{ orderId: number, error: null || orderId: null, error: string }}
 */
export async function createOrder({
  clientId,
  addressId,
  delivererId,
  deliveryDate,
  totalAmount,
  items,
}) {
  // Insertar pedido
  const { data: order, error: orderError } = await supabase
    .from("orders")
    .insert({
      client_id: clientId,
      address_id: addressId,
      deliverer_id: delivererId,
      delivery_date: deliveryDate,
      total_amount: totalAmount,
    })
    .select("order_id")
    .single();

  if (orderError) return { orderId: null, error: orderError.message };

  // Insertar detalles — el trigger valida stock por cada row
  const details = items.map((item) => ({
    order_id: order.order_id,
    product_id: item.productId,
    quantity: item.quantity,
    subtotal: item.subtotal,
  }));

  const { error: detailsError } = await supabase
    .from("order_details")
    .insert(details);

  if (detailsError) {
    // Si fallan los detalles (ej. stock insuficiente), cancelar el pedido
    await supabase
      .from("orders")
      .update({ status: "cancelled" })
      .eq("order_id", order.order_id);

    return { orderId: null, error: detailsError.message };
  }

  return { orderId: order.order_id, error: null };
}

// ─────────────────────────────────────────
// CONSULTAS — CLIENTE
// ─────────────────────────────────────────

/**
 * Devuelve todos los pedidos del cliente autenticado con sus detalles.
 *
 * @returns {{ data: object[] | null, error: string | null }}
 */
export async function getMyOrders() {
  const { data, error } = await supabase
    .from("orders")
    .select(
      `
            *,
            delivery_addresses(name, street, zip_code),
            employees(name),
            order_details(
                quantity,
                subtotal,
                products(name, product_pictures(picture_url))
            )
        `,
    )
    .order("created_at", { ascending: false });

  if (error) return { data: null, error: error.message };
  return { data, error: null };
}

// ─────────────────────────────────────────
// CONSULTAS — REPARTIDOR
// ─────────────────────────────────────────

/**
 * Devuelve los pedidos asignados al repartidor autenticado.
 *
 * @returns {{ data: object[] | null, error: string | null }}
 */
export async function getAssignedOrders() {
  const { data, error } = await supabase
    .from("orders")
    .select(
      `
            *,
            clients(name, phone),
            delivery_addresses(name, street, zip_code),
            order_details(
                quantity,
                subtotal,
                products(name)
            )
        `,
    )
    .in("status", ["processing", "on_the_way"])
    .order("delivery_date");

  if (error) return { data: null, error: error.message };
  return { data, error: null };
}

/**
 * Actualiza el status de un pedido asignado al repartidor.
 * Solo permite: on_the_way, delivered (RLS bloquea el resto).
 *
 * @param {number} orderId
 * @param {'on_the_way' | 'delivered'} status
 * @returns {{ error: string | null }}
 */
export async function updateOrderStatus(orderId, status) {
  const { error } = await supabase
    .from("orders")
    .update({ status })
    .eq("order_id", orderId);

  if (error) return { error: error.message };
  return { error: null };
}

// ─────────────────────────────────────────
// CONSULTAS — ADMIN
// ─────────────────────────────────────────

/**
 * Devuelve todos los pedidos con información completa.
 * Opcionalmente filtrar por status.
 *
 * @param {{ status?: string }} filters
 * @returns {{ data: object[] | null, error: string | null }}
 */
export async function getAllOrders({ status } = {}) {
  let query = supabase
    .from("orders")
    .select(
      `
            *,
            clients(name, email, phone),
            delivery_addresses(name, street, zip_code),
            employees(name, phone),
            order_details(
                quantity,
                subtotal,
                products(name)
            )
        `,
    )
    .order("created_at", { ascending: false });

  if (status) query = query.eq("status", status);

  const { data, error } = await query;
  if (error) return { data: null, error: error.message };
  return { data, error: null };
}

/**
 * Cancela un pedido (solo admin).
 * El trigger restore_stock restaura el stock automáticamente.
 *
 * @param {number} orderId
 * @returns {{ error: string | null }}
 */
export async function cancelOrder(orderId) {
  const { error } = await supabase
    .from("orders")
    .update({ status: "cancelled" })
    .eq("order_id", orderId);

  if (error) return { error: error.message };
  return { error: null };
}
